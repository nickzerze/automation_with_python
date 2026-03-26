import boto3
from operator import itemgetter

"""
#################################################################################
    Python script που ψάχνει όλα τα volumes που έχουν σαν tag: Name=prod
    και για κάθε ένα volume κρατάει μόνο τα 2 πιο πρόσφατα snapshots. 
    Γενικά για κάθε ένα volume μπορεί να κρατάει snapshot κάθε μια μέρα, 
    οπότε θα έχω πάρα πολλά snapshots (πχ μέσα στο μήνα 30 για κάθε ένα volume)
#################################################################################
"""

ec2_client = boto3.client('ec2', region_name="eu-central-1")

# Αυτό για να κρατάω μόνο τα volumes με tag -> Name=Jenkins
# Το volumes στην ουσία είναι μια λίστα από dictionaries
volumes = ec2_client.describe_volumes(
    Filters=[
        {
            'Name': 'tag:Name',
            'Values': ['Jenkins']
        }
    ]
)

# Για κάθε ένα volume (έχω μια for loop), πάω και:
#   1. κρατάω μόνο τα snapshots τα οποία έχω φτιάξει εγώ (self)
#   2. κάνω φιλτράρισμα ώστε όταν τσεκάρω ένα volume, να κρατάω μόνο τα snapshots από το συγκεκριμένο volume (γι'αυτό έχω το filters με βάση το VolumeId)
#   3. sorted_by_date -> φτιάχνω μια λίστα με descending order με όλα τα snapshots σορταρισμένα με βάση το
#       πεδίο 'StartTime'. Γι'αυτό θέλω το την itemgetter η οποία παίρνει τη λίστα snapshots['Snapshots'] και το σορτάρω με βάση το
#       dictionary key 'StartTime'
#   4. Διαγράφω όλα τα snapshots από το 3ο και μετά από την sorted_by_date λίστα
for volume in volumes['Volumes']:
    snapshots = ec2_client.describe_snapshots(
        OwnerIds=['self'],
        Filters=[
            {
                'Name': 'volume-id',
                'Values': [volume['VolumeId']]
            }
        ]
    )
    print(snapshots['Snapshots'])
    sorted_by_date = sorted(snapshots['Snapshots'], key=itemgetter('StartTime'), reverse=True)
    print(sorted_by_date)

    #   Διαγράφω όλα τα snapshots από το 3ο και μετά από την sorted_by_date λίστα
    for snap in sorted_by_date[2:]:
        response = ec2_client.delete_snapshot(
            SnapshotId=snap['SnapshotId']
        )
        print(response)

