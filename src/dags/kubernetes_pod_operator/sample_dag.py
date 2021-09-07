import os

from airflow import models
from airflow.providers.cncf.kubernetes.operators.kubernets_pod import (
    KubernetesPodOperator,
)
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s

default_args = {"owner": "sample", "retries": 2}
volume_mount = k8s.V1VolumeMount(
    name="sample-data", mount_path="/sample-data", sub_path=None
)
volume = k8s.V1Volume(name="sample-data", empty_dir={})
env = os.getenv("ENV", "local")

if env != "local":
    account_id = os.getenv("ACCOUNT_ID")
    image_tag = os.getenv("IMAGE_TAG", "1.0.0")
    iamge = f"{account_id}.dkr.ecr.us-west-2.amazonaws.com/test/nodejobs:{image_tag}"
    image_pull_secrets = [k8s.V1LocalObjectReference("aws-registry")]
else:
    image = "test/nodejobs:1.0.0"
    image_pull_secrets = []

# 1.define dag. DAG ID shows in airflow ui
with models.DAG(
    dag_id="node_jobs",
    schedule_interval=None,
    start_date=days_ago(1),
    is_paused_upon_creation=False,
    catchup=False,
) as dag:
    node_jobs = KubernetesPodOperator(
        task_id="test_task",
        name="test",
        cmds=["node", "services/service/nodejobs.js"],
        arguments=["{{ dag_run.conf }}"],
        namespace="jobs",
        image_pull_secrets=image_pull_secrets,
        volumes=[volume],
        volume_mounts=[volume_mount],
        env_vars={"DB_USER": os.getenv("DB_USER")},
        annotations={"sidecar.istio.io/inject": "false"},
        resources={
            "request_cpu": "200m",
            "request_memory": "256Mi",
            "limit_cpu": "1000m",
            "limit_memory": "1Gi",
        },
    )
