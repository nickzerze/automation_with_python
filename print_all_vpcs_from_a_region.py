import boto3

""" 
    - Φτιάχνουμε έναν client οποίος θα συνδεθεί στο AWS. 
    - Θα χρησιμοποιήσει τα ήδη υπάρχοντα credentials τα οποία υπάρχουν στον φάκελο .aws 
    - Για documentation πάμε στο https://docs.aws.amazon.com/boto3/latest/
"""
ec2_client = boto3.client('ec2', region_name='us-east-1')

"""
    Μέσα από το documentation ψάχνω να βρω τα functions τα οποία με ενδιαφέρουν. Αυτά που με νοιάζουν είναι
        το όνομα του function καθώς επίσης και τα parameters τα οποία πρέπει να περάσουμε στο function.
    O client μας γυρνάει στην ουσία ένα dictionary με αυτά που έχω ζητήσει. 
"""
# Η all_available_vpcs έχει μέσα το dictionary Που επιστρέφει η describe_vpcs()
all_available_vpcs = ec2_client.describe_vpcs()
# Από όλη το dictionary κρατάω μόνο το Vpcs το οποίο είναι μια λίστα από dictionaries, όπου το κάθε ένα dictionary είναι και ένα διαφορετικό VPC
#   Αυτό το κάνω γιατί θέλω να προσπελάσω κάποια συγκεκριμένα στοιχεία από κάθε VPC (πχ VpcId, CidrBlock)
vpcs = all_available_vpcs['Vpcs']


for vpc in vpcs:
    print(vpc["VpcId"])
    # Για να εκτυπώσω το CidrBlockState θα πρέπει να κρατήσω όλο το CidrBlockAssociationSet που είνα μια λίστα από dictionaries
    #   και μέτα μέσα σε αυτή τη λίστα (all_cidr_assoc_sets) να τρέξω μια for loop και να εκτυπώσω το key CidrBlockState από το κάθε ένα dictionary που υπάρχει.
    all_cidr_assoc_sets = vpc["CidrBlockAssociationSet"]
    for cidr_assoc in all_cidr_assoc_sets:
        print(cidr_assoc["CidrBlockState"])



