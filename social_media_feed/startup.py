import sys
from django.core.management import call_command

def run_migrations():
    try:
        call_command("migrate", interactive=False)
    except Exception as e:
        print("Migration error:", e)
