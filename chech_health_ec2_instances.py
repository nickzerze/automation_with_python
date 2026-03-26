import boto3
import schedule

ec2_client = boto3.client('ec2')

# Με την describe_instances() μπορώ να δω μόνο το state από τα instances (δηλαδή το running, stopping, stopped, ...)
# Δεν μπορώ να δω το instance status και το system status -> Γι' αυτό καλύτερα χρησιμοποιώ την describe_instance_status
#   με την οποία μπορώ να δω τα πάντα.
"""
reservations = ec2_client.describe_instances()
for reservation in reservations['Reservations']:
    instances = reservation['Instances']
    for instance in instances:
        print(f"Instance {instance['InstanceId']} is {instance['State']['Name']}")
"""

# !ΠΡΟΣΟΧΗ! Στην describe_instance_status() θα πρέπει να περάσω σαν όρισμα το IncludeAllInstances=True
#   γιατί by default επιστρέφει μόνο τα running Instances.
def check_instance_status():
    statuses = ec2_client.describe_instance_status(IncludeAllInstances=True)
    for status in statuses['InstanceStatuses']:
        ins_status = status['InstanceStatus']['Status']
        sys_status = status['SystemStatus']['Status']
        state = status['InstanceState']['Name']
        print(f"Instance {status['InstanceId']} is {state} with instance status {ins_status} and system status {sys_status}")
    print("####################################### ")

# Φτιάχνουμε ένα scheduled task και το βάζουμε να τρέχει για πάντα.
schedule.every(5).seconds.do(check_instance_status)
while True:
    schedule.run_pending()