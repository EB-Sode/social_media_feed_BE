from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY0NjExODg5LCJpYXQiOjE3NjQzNTI2ODksImp0aSI6ImI0MTQwZTQ3NzZmODQzZjNiZjgxY2JlNDU4YTQ5MWYwIiwidXNlcl9pZCI6IjEifQ.zylTbmc3XnpfqunzDn7nu6_QJlc3o160HbJXEU-vv8k