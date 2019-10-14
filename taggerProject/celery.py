#! /usr/bin/env python

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

from celery.schedules import crontab

# This file explained well on https://docs.celeryproject.org/en/latest/django/first-steps-with-django.html 

# if not settings.configured:
#     settings.configure()

# In order to launch Celery from command line, we need to do:
# $ export DJANGO_SETTINGS_MODULE=taggerProject.settings
# This makes the 'settings' work well.
# To run command line: 
# celery -A taggerProject worker -l info

# Need a celery worker running, then open 
# python manage.py shell
# from filepopulator import tasks
# a = tasks.<whatever>.delay(<args>)
# a.get()
print(settings.CELERY_BROKER_URL)
print("huh...")
# Set the default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taggerProject.settings')
app = Celery('taggerProject',
	broker = settings.CELERY_BROKER_URL,
	backend='amqp://',
	include=['filepopulator.tasks'])

app.config_from_object('django.conf:settings', namespace='CELERY')

print('here?')
# Discover the 'tasks.py' modules
app.autodiscover_tasks()# lambda: settings.INSTALLED_APPS)
print('tasks')

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request) )

app.conf.beat_schedule = {
    'log_time': {
        'task': 'filepopulator.tasks.log_time',
        'schedule': 30.0#,
        # 'args': (16, 16)
    },
}

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    print('main')
    app.start()