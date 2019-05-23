from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that the shared_task will use this app

# Import the 'app' variable from celery.py
from .celery import app as celery_app

__all__ = ('celery_app',)
