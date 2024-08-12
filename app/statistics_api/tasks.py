import json
from datetime import date
from datetime import datetime

from celery import shared_task
from statistics_api.parser.redis_db.client import get_client
from statistics_api.parser.utils import generate_request_id

from .models import Novelty
from .models import Poll
from .models import PollAnswer
from .parser.request import make_request
from .parser.request import make_specific_request


@shared_task
def parse_novelties():
    page_counter = 1
    request_id = generate_request_id()
    headers = json.loads(get_client().get("headers"))
    while True:
        res = make_request(headers, request_id, "novelty", page_counter)

        for i in res["result"]["novelties"]:
            novelty = Novelty.objects.filter(id=i["id"]).first()
            if novelty and not novelty.is_active:
                return
            elif novelty and novelty.is_active and i["status"] == "old":
                answers = make_specific_request(i["id"], request_id, "novelty")["result"]["details"]["rating"]["counts"]
                novelty.update(answers=answers, end_date=i["end_date"], is_active=False)

            elif not novelty and i["status"] == "old":
                specific = make_specific_request(i["id"], request_id)
                Novelty.objects.create(
                    id=i["id"],
                    title=i["title"],
                    start_date=datetime.utcfromtimestamp(i["begin_date"]),
                    end_date=datetime.utcfromtimestamp(i["end_date"]),
                    answers=specific["result"]["details"]["rating"]["counts"],
                    is_active=False,
                )
            elif not novelty and i["status"] == "active":
                Novelty.objects.create(
                    id=i["id"],
                    title=i["title"],
                    start_date=datetime.utcfromtimestamp(i["begin_date"]),
                    end_date=datetime.utcfromtimestamp(i["end_date"]),
                    answers=None,
                    is_active=True,
                )
        if res["result"]["last_page"]:  # сохранить id который был закончен на момент парсинга parsingAttempts
            return
        page_counter += 1


@shared_task
def parse_polls():
    page_counter = 1
    request_id = generate_request_id()
    headers = json.loads(get_client().get("headers"))
    while True:
        res = make_request(headers, request_id, "poll", page_counter)

        for i in res["result"]["polls"]:
            poll = Poll.objects.filter(id=i["id"]).first()
            if poll and not poll.is_active:
                return
            elif poll and poll.is_active and i["status"] == "old":
                answers = make_specific_request(i["id"], request_id, "poll")["result"]["questions"]
                poll.update(number_of_answers=i["voters_count"], is_active=False)
                for question in answers:
                    PollAnswer.objects.create(
                        poll=poll,
                        name=question["question"],
                        number_of_answers=question["voters_count"],
                        id=question["id"],
                    )
                # bulk = [PollAnswer(poll__id = i["id"], title=specific['question'], id =  ]
                # PollAnswer.objects.bulk_create(bulk)

            elif not poll and i["status"] == "old":
                answers = make_specific_request(i["id"], request_id, "poll")

                answers = make_specific_request(i["id"], request_id, "poll")["result"]["questions"]
                Poll.objects.create(
                    id=i["id"],
                    title=i["title"],
                    start_date=datetime.utcfromtimestamp(i["begin_date"]),
                    end_date=datetime.utcfromtimestamp(i["end_date"]),
                    number_of_answers=i["voters_count"],
                    is_active=False,
                )
                for question in answers:
                    PollAnswer.objects.create(
                        poll=poll,
                        name=question["question"],
                        number_of_answers=question["voters_count"],
                        id=question["id"],
                    )

            elif not poll and i["status"] == "active":
                Poll.objects.create(
                    id=i["id"],
                    title=i["title"],
                    start_date=datetime.utcfromtimestamp(i["begin_date"]),  # поменять метод, сохранять в utc
                    end_date=datetime.utcfromtimestamp(i["end_date"]),
                    number_of_answers=None,
                    is_active=True,
                )
        if res["result"]["last_page"]:  # сохранить id который был закончен на момент парсинга parsingAttempts
            return
        page_counter += 1
