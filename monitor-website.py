import boto3
import requests
import smtplib
import os
import paramiko
import time
import schedule

# Αυτά είναι environmental variables τα οποία τα έχω βάλει στο PyCharm μέσω του Edit Configuration...
#   Δεν θέλω να το κάνω global βάζοντάς τα μέσω terminal
#   Σαν EMAIL_ADDRESS έχω το nickzerze@gamil.com
#   Σαν EMAIL_PASSWORD έχω φτιάξει ένα app password για το google account μου (myaccount.google.com/u/1/apppasswords)
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

# Αυτό το θέλω για να κάνω reboot το ec2-instance
SERVER_INSTANCE_ID = 'i-0bbf82db77d632b2c'

#   Το έχω κάνει function γιατί το χρησιμοποιώ σε 2 σημεία οπότε δεν θέλω να επαναλαμβάνονται πράγματα
def send_email_notification(email_msg):
    with smtplib.SMTP('smtp.gmail.com', port=587) as smtp:
        smtp.ehlo()         # Για να μάθουμε αν ο smtp server υποστηρίζει STARTTLS. Το EHLO είναι η εντολή με την οποία ο client λέει στον SMTP server:«γεια, θέλω να μιλήσουμε με Extended SMTP» «πες μου τι δυνατότητες υποστηρίζεις»
        smtp.starttls()     # από αυτό το σημείο και μετά το username/password και τα δεδομένα του email στέλνονται κρυπτογραφημένα και όχι plain text
        smtp.ehlo()         # Μετά το starttls(): η σύνδεση γίνεται κρυπτογραφημένη, ο SMTP διάλογος ουσιαστικά ξεκινά από την αρχή, ο server μπορεί τώρα να δώσει διαφορετικές δυνατότητες, ειδικά authentication methods
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        message = f"Subject: SITE is DOWN\n{email_msg}"
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, message)

def restart_container_via_ssh_to_server():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())  # Αυτό το θέλουμε για να μην χρειαστεί να πατήσουμε Yes για το missing key την πρώτη φορά που θα πάμε να σηνδεθούμε στον server
    ssh.connect(hostname='3.68.230.122', username='ec2-user',
                key_filename="C:/Users/nickz/Desktop/ppk's-tokens/aws-java-maven-app.pem")
    stdin, stdout, stderr = ssh.exec_command("docker start b170b1b661e4")
    print(stdout.readlines())
    ssh.close()

def restart_server_and_container():
    # Restart AWS ec2-instance server
    print("Restarting the EC2-instance...")
    ec2_client = boto3.client('ec2', region_name='eu-central-1')
    ec2_client.reboot_instances(InstanceIds=[SERVER_INSTANCE_ID])
    print("Waiting for EC2-instance to have state = running...")

    while True:
        # Φέρνω το describe_instances μόνο για το συγκεκριμένο instance-id και το βάζω στο response. Αυτό είναι ένα dictionary
        ec2_response = ec2_client.describe_instances(InstanceIds=[SERVER_INSTANCE_ID])
        # Τώρα από το "Reservations" αν και έχει μονο ένα στοιχείο, πρέπει να κρατήσω το πρώτο στοιχείο [0] γιατί αυτό είναι μια λίστα κανονικά
        reservation = ec2_response["Reservations"][0]
        # Τώρα κρατάω το πρώτο στοιχείο [0] από το "Instances" γιατί αν και είναι μόνο ένα στοιχείο, είναι μέσα σε μια λίστα
        instance = reservation["Instances"][0]

        # Αντί να το σπάσω, μπορούσα αμέσως έτσι, αλλά καλύτερα έτσι για να καταλαβαίνω.
        #state = ec2_response['Reservations'][0]['Instances'][0]['State']['Name']
        if instance["State"]["Name"] == 'running':
            print("EC2-instance is running again, waiting 10 more seconds...")
            time.sleep(10)

            # Restart the docker container (Application)...
            print("Restarting the docker container (Application)...")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())  # Αυτό το θέλουμε για να μην χρειαστεί να πατήσουμε Yes για το missing key την πρώτη φορά που θα πάμε να σηνδεθούμε στον server
            ssh.connect(hostname='3.68.230.122', username='ec2-user',
                        key_filename="C:/Users/nickz/Desktop/ppk's-tokens/aws-java-maven-app.pem")
            stdin, stdout, stderr = ssh.exec_command("docker start b170b1b661e4")
            print(stdout.readlines())
            ssh.close()
            print("Application (docker container) restarted")
            break

def monitor_application():
    try:
        response = requests.get('http://3.68.230.122:8080/')
        if response.status_code == 200:
            print("Site is UP")
        else:
            # Εδώ το application κάτι επιστρέφει αλλά ΟΧΙ 200.
            # Οπότε 1) στέλνω Notification και 2) προσθαθώ να κάνω restart το docker.
            #   1) Στέλνω notification
            print("Site is DOWN")
            msg = f"Application returned: {response.status_code}"
            send_email_notification(msg)

            #   2) Restart το application ->
            #   Θα πρέπει να συνδεθώ με ssh στον server και να κάνω restart το container. Θα χρησιμοποιήσω
            #       το paramiko library για να κάνω ssh στον server.
            restart_container_via_ssh_to_server()
            print("Application restarted")

    except Exception as ex:
        # Αν φτάσουμε σε Exception σημαίνει οτι η εφαρμογή δεν είναι καν accessible, δηλαδή δεν είναι ότι δεν επιστρεφει 200
        #   αλλά δεν επιστρέφει τίποτα. O server είναι down.
        print(f"Connection Error: {ex}")
        msg = "Application is not accessible at all"
        send_email_notification(msg)
        restart_server_and_container()


schedule.every(5).minutes.do(monitor_application)
while True:
    schedule.run_pending()
