import os
from celery import Celery
from flask import Blueprint, redirect, render_template, request
import time
celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379")

tasks = Blueprint('tasks', __name__)


@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(10)
    print("hello from celery")
    return True
