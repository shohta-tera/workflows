import json

import boto3
from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s

default_args = {"owner": "admin"}


# dag configuration
@dag(
    default_args=default_args,
    schedule_interval=None,
    start_date=days_ago(1),
    tags=["sample-dag"],
)
# DAG name
def sample_job():
    # task definition by @task decorator
    @task(
        executor_config={
            "pod_override": k8s.V1Pod(
                spec=k8s.V1PodSpec(
                    containers=[
                        k8s.V1Container(
                            name="airflow-worker",
                            resources=k8s.V1ResourceRequirements(
                                limits={"cpu": "1000m", "memory": "1Gi"},
                                requests={"cpu": "250m", "memory": "256Mi"},
                            ),
                        )
                    ]
                )
            )
        }
    )
    def create_large_data():
        data = {}
        data_string = "{'1001': 301, '10027': 201, '1003': 502.22}"
        for i in range(1000000):
            data[i] = json.loads(data_string)

        return data

    @task(
        executor_config={
            "KubernetesExecutor": {
                "request_memory": "256Mi",
                "request_cpu": "256m",
                "limit_memory": "512Mi",
                "limit_cpu": "1000m",
            }
        }
    )
    def save_to_storage(data: dict):
        s3_endpoint_url = "http://minio.microservice.svc.cluster.local:9000"
        s3 = boto3.client(
            "s3",
            endpoint_url=s3_endpoint_url,
            aws_access_key_id="access_key",
            aws_secret_access_key="secret_key",
        )
        s3.put_object(Bucket="airflow", Key="data.txt", Body=json.dumps(data))

    data = create_large_data()
    save_to_storage(data)


dag = sample_job()
