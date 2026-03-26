import boto3

ec2_client_paris = boto3.client('ec2', region_name ='eu-west-3')
ec2_client_frankfurt = boto3.client('ec2', region_name ='eu-central-1')

reservations_paris = ec2_client_paris.describe_instances()['Reservations']
reservations_frankfurt = ec2_client_frankfurt.describe_instances()['Reservations']

instance_ids_paris = []
instance_ids_frankfurt =[]

for res in reservations_paris:
    instances = res["Instances"]
    for ins in instances:
        instance_ids_paris.append(ins["InstanceId"])

# Τώρα πια ανήκει στο ec2 client και όχι στο resource
#   Απλά πάιρνω copy-paste τον κώδικα από εδώ: https://docs.aws.amazon.com/boto3/latest/reference/services/ec2/client/create_tags.html
#   για το Request syntax και βάζω ότι θέλω εγώ. ΠΡΟΣΟΧΗ: απλά γράφω response = ec2_client_paris.create_tags(...), δεν καλώ κάτι
#   άλλο για να τρέξει αυτό και να μπει το tag, τρέχει μόνο του.
"""
response = ec2_client_paris.create_tags(
    Resources=instance_ids_paris,
    Tags=[
        {
            'Key': 'Test',
            'Value': 'created by python script'
        },
    ]
)
"""
"""
    ###################################################################
    Το κομμάτι για το region της Frankfurt
    ΠΡΟΣΟΧΗ: δες ότι ξανατρέχω το response απλά με άλλα ορίσματα.
    ###################################################################
"""
for res in reservations_frankfurt:
    instances = res["Instances"]
    for ins in instances:
        instance_ids_frankfurt.append(ins["InstanceId"])

response = ec2_client_frankfurt.create_tags(
    Resources=instance_ids_frankfurt,
    Tags=[
        {
            'Key': 'Test',
            'Value': 'created by python script'
        },
    ]
)