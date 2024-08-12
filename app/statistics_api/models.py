from django.contrib.postgres.fields import ArrayField
from django.db import models


class Poll(models.Model):
    title = models.CharField(max_length=256, null=False)
    start_date = models.DateTimeField(null=False)
    end_date = models.DateTimeField(null=True)
    number_of_answers = models.IntegerField(null=True)
    is_active = models.BooleanField(null=False)  # generated column для это поля
    created = models.DateTimeField(auto_now_add=True)


class PollAnswer(models.Model):
    poll = models.ForeignKey(Poll, related_name="answer", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    number_of_answers = models.IntegerField(default=False)


class Novelty(models.Model):
    title = models.CharField(max_length=256, null=False)
    start_date = models.DateTimeField(null=False)
    end_date = models.DateTimeField(null=True)
    answers = ArrayField(models.IntegerField(), null=True)
    is_active = models.BooleanField(null=False)
    created = models.DateTimeField(auto_now_add=True)
