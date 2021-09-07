import os

from airflow.models import DagBag

# Need to specify directry list
dags_dirs = ["./kubernetes_pod_operator"]

for dir in dags_dirs:
    dag_bag = DagBag(os.path.expanduser(dir))

    if dag_bag:
        for dag_id, dag in dag_bag.dags.items():
            globals()[dag_id] = dag