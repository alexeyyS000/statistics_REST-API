import json

from requests import get
from requests import post


def make_request(
    headers,
    request_id,
    subject,
    page=None,
    count_per_page=50,
    filter=["active", "passed", "old"],
):
    payload = {"count_per_page": count_per_page, "filter": filter, "page_number": page}

    url = f"https://ag.mos.ru/api/service/site/{subject}/select?request_id={request_id}"

    q = post(url, headers=headers, json=payload)

    return json.loads(q.text)


def make_specific_request(subject_id, request_id, subject):
    url = f"https://ag.mos.ru/api/service/site/{subject}/get?{subject}_id={subject_id}&request_id={request_id}"

    q = get(url)

    return json.loads(q.text)
