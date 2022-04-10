from workers import celery
from datetime import datetime
from celery.schedules import crontab


@celery.on_after_finalize.connect
def setup_periodic_tasks(sender,**kwargs):
    sender.add_periodic_task


@celery.task()
def just_say_hello(name):
  print("Inside task")
  ret="Hello"+ name
  print(ret)
  return ret