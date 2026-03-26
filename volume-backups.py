import boto3
import schedule

ec2_client = boto3.client('ec2', region_name='eu-central-1')

def create_volume_snapshots():
    volumes = ec2_client.describe_volumes(
        Filters=[
            {   # Φιλτράρω όλα τα volumes και κρατάω μόνο αυτά που έχουν σαν tag: Key=Name και Value=prod ή Value=staging
                # ΠΡΟΣΟΧΗ: το tag πρέπει να μπει στο volume και όχι στο ec2-instance
                'Name': 'tag:Name',
                'Values': ['Jenkins', 'staging']
            }
        ]
    )
    for volume in volumes['Volumes']:
        new_snapshot = ec2_client.create_snapshot(
            VolumeId=volume['VolumeId']
        )
        print(new_snapshot)

schedule.every().day.at("11:16").do(create_volume_snapshots)
while True:
    schedule.run_pending()