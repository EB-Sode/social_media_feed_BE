import os

if os.environ.get("DJANGO_DEBUG") == "true":
    from .celery_app import app as celery_app


    __all__ = ("celery_app",)
