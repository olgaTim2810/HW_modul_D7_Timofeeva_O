import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPaper.settings')

app = Celery('NewsPaper')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

#app.conf.beat_schedule = {    #запуск счетчика от 1 до N как периодическая задача
#    'print_every_5_seconds': {
#        'task': 'news.tasks.printer',
#        'schedule': 5,
#        'args': (5,),
#    },
#}

#app.conf.beat_schedule = {   #проверка еженедельной рассылки каждые 10 сек
#    'when_week': {
#        'task': 'news.tasks.notify_weekly',
#        'schedule': 10,
#    },
#}

app.conf.beat_schedule = {  #для еженедельной рассылки (каждый понедельник в 8:00 утра)
     'when_week': {
         'task': 'news.tasks.notify_weekly',
         'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
     },
 }