import boto3
import schedule

def eks_schedule_info():
    eks_client = boto3.client('eks', region_name='eu-central-1')

    # Δες εδώ: πρέπει να βάλεις response = eks_client.list_clusters()['clusters'] και
    # ΟΧΙ μόνο του χωρίς του ['clusters']
    clusters = eks_client.list_clusters()['clusters']

    for cluster in clusters:
        response = eks_client.describe_cluster(
            name=cluster
        )
        cluster_status = response['cluster']['status']
        cluster_endpoint =  response['cluster']['endpoint']
        cluster_version =  response['cluster']['version']
        print(f"Cluster: {cluster} status is {cluster_status} with endpoint {cluster_endpoint} and version {cluster_version}")
    print("#####################################################")

schedule.every(5).seconds.do(eks_schedule_info)
while True:
    schedule.run_pending()