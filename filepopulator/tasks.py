from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.conf import settings

from celery import shared_task

import os

if not settings.configured:
    settings.configure()

# If you don’t care about the results of a task, be sure to set the ignore_result option, as storing results wastes time and resources.
@shared_task(ignore_result=True)
# from django.db import transaction
# @transaction.commit_on_success
#(name='filepopulator.load_images_into_db')
def load_images_into_db():
    base_directory = settings.SERVER_IMG_DIR
    flist = []
    for root, dirs, files in os.walk(base_directory, topdown=False):
        for name in files:
            print(os.path.join(root, name))
            flist.append(os.path.join(root, name))

    return flist

# Some test tasks:
@shared_task
#(name='filepopulator.add')
def add(x, y):
    return x + y


@shared_task#(name='filepopulator.mul')
def mul(x, y):
    return x * y


@shared_task#(name='filepopulator.xsum')
def xsum(numbers):
    return sum(numbers)

from datetime import datetime as dt
@shared_task#(name='filepopulator.xsum')
def log_time():
    string = 'Current time: {}'.format(dt.now())
    with open(os.path.join(settings.CODE_DIR, 'timelog.log'), 'a') as fh:
        print(string, file=fh)

