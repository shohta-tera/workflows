from logging import INFO, basicConfig, getLogger

from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from kubernets.client import models as k8s

basicConfig(level=INFO)
logger = getLogger(__name__)
default_args = {"owner": "admin", "retries": 1}


# dag configuration
@dag(
    default_args=default_args,
    schedule_interval=None,
    start_date=days_ago(1),
    tags=["sample-dag"],
)
# DAG name
def DAG_A():
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
    def alpha():
        print("test")

    alpha()

    return dag
