from logging import INFO, basicConfig, getLogger

from airflow.decorators import task
from airflow.models import DAG
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s

basicConfig(level=INFO)
logger = getLogger(__name__)


def sample_job(dag_id, schedule, default_args, res_id, name):
    with DAG(
        dag_id=dag_id,
        default_args={"owner": "admin"},
        schedule_interval=schedule,
        start_date=days_ago(1),
        tags=[name, "sample", "tempalted"],
        catchup=True,
    ) as dag:

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
        def sample():
            print("Hello")

    sample_job()

    return dag
