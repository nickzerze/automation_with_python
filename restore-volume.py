import boto3
from operator import itemgetter

ec2_client = boto3.client('ec2', region_name="eu-central-1")
ec2_resource = boto3.resource('ec2', region_name="eu-central-1")

# Βάζω hardcoded το instance-id από το Jenkins server
instance_id = "i-0dedabb1a374351aa"

# Τώρα θα βρούμε όλα τα volumes που είναι attached σε αυτό το instance-id (μέσω του attachment.instance-id)
volumes = ec2_client.describe_volumes(
    Filters=[
        {
            'Name': 'attachment.instance-id',
            'Values': [instance_id]
        }
    ]
)

# Υποθέτουμε ότι το ec2-instance έχει μόνο ένα volume attached και διαλέγω το πρώτο.
instance_volume = volumes['Volumes'][0]
print(instance_volume['VolumeId'])

# Από αυτό το volume Θέλω να βρώ το πιο πρόσφατο snapshot το οποίο έχω.
# Πρώτα βρίσκω όλα τα snapshots αυτού του volume και μετά τα σορτάρω και κρατάω το πρώτο στοιχείο
snapshots = ec2_client.describe_snapshots(
    OwnerIds=['self'],
    Filters=[
        {
            'Name': 'volume-id',
            'Values': [instance_volume['VolumeId']]
        }
    ]
)

# Κρατάω το πρώτο element από τη σορταρισμένη λίστα με όλα τα snapshots του συγκεκριμένου volume
latest_snapshot = sorted(snapshots['Snapshots'], key=itemgetter('StartTime'), reverse=True)[0]
print(latest_snapshot['StartTime'])

# Τώρα θα φτιάξουμε ένα volume από το latest_snapshot
#   Βάζω hardcoded το AvailabilityZone -> eu-central-1a
new_volume = ec2_resource.create_volume(
    SnapshotId=latest_snapshot['SnapshotId'],
    AvailabilityZone='eu-central-1a',
    TagSpecifications=[
        {
            'ResourceType': 'volume',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': latest_snapshot['Jenkins']
                }
            ]
        }
    ]
)

# Τώρα θα κάνουμε attach το καινούργιο volume στο ec2-instance
#   Για να μπορέσει να γίνει αυτό θα πρέπει πρώτα το volume να είναι available.
while True:
    vol = ec2_resource.Volume(new_volume['VolumeId'])
    # ΠΡΟΣΟΧΗ 1: δες εδώ ότι κάνω προσπέλαση στο state βάζοντας .state (είναι του boto3) και όχι με [] γιατί δεν είναι Dictionary.
    # ΠΡΟΣΟΧΗ 2: για το Device πάω και βλέπω στο ec2-instance μου τι εχω και πάω και προσθέτω το επόμενο γράμμα. Εδώ ήταν /dev/xvda,
    #   οπότε πρέπει να γίνει /dev/xvdb γιατί αλλιώς θα έχω conflict
    print(vol.state)
    if vol.state == 'available':
        ec2_resource.Instance(instance_id).attach_volume(
            VolumeId=new_volume['VolumeId'],
            Device='/dev/xvdb',
        )