from datetime import timedelta
from logging import INFO, basicConfig, getLogger

import requests
from generating_dag_dynamically.template_job import templated

default_args = {"owner": "admin"}

basicConfig(level=INFO)
logger = getLogger(__name__)


def get_all_response(headers, n=0, item_list=[]):
    base_url = "something"
    rows_val = 100
    page_val = n
    target_url = f"{base_url}?page={page_val}&rows={rows_val}"
    response = requests.get(target_url, headers=headers)
    item = response.json()
    item_list.extend(item)
    fetched = len(item)
    if fetched >= rows_val:
        item_list.extend(get_all_response(headers, n + 1, item_list))
    return item_list


headers = {"Content-Type": "application/json", "Authorization": "jwt token"}
response = get_all_response(headers, 0)
"""
Example:
response = [
    {
        "id": uuid,
        "name": "sample_name",
        "frequency": 600
    }
]
"""

for record in response:
    res_id = record["id"]
    schedule = timedelta(record["frequency"])
    name = record["name"]
    dag_id = f"Sample_dag_{id}_{name}"
    globals()[dag_id] = templated.sample_job(
        dag_id, schedule, default_args, res_id, name
    )
