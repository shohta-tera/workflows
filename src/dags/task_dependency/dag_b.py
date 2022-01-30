from logging import INFO, basicConfig, getLogger

from airflow.decorators import dag, task
from airflow.models.dag import get_last_dagrun
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.dates import days_ago
from airflow.utils.session import provide_session
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
    @provide_session
    def _get_execution_date_of_task_a(exec_date, session=None, **kwargs):
        dag_last_run = get_last_dagrun("DAG_A", session)
        return dag_last_run.execution_date

    task_a_sensor = ExternalTaskSensor(
        task_id="alpha_sensor",
        external_dag_id="DAG_A",
        external_task_id="alpha",
        allowed_states=["success"],
        execution_date_fn=_get_execution_date_of_task_a,
    )

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
    def beta():
        print("test")

    beta_task = beta()
    task_a_sensor >> beta_task

    return dag
