import os
from celery import Celery
from celery.schedules import crontab
from flask import Blueprint, redirect, render_template, request
import time

tasks = Blueprint('tasks', __name__)

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379")


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(60.0, check.s('hello'), name='add every 10')

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        test.s('Happy Mondays!'),
    )


@celery.task
def check(arg):
    print(arg)


@celery.task
def test(arg):
    print(arg)

@celery.task
def add(x, y):
    z = x + y
    print(z)


@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(10)
    print("hello from celery")
    return True
