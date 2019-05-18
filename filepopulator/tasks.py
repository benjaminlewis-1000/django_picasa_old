from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.conf import settings

from celery import shared_task

import os
settings.configure()

@shared_task
def load_images_into_db2():
    base_directory = settings.SERVER_IMG_DIR
    for root, dirs, files in os.walk(base_directory, topdown=False):
        for name in files:
            print(os.path.join(root, name))