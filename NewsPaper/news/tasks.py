from celery import shared_task
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed
from django.template.loader import render_to_string

import datetime
import time
from .models import *


@shared_task
def send_notifications(preview, pk, title, subscribers):  #рассылка уведомлений подписчикам после создания новости
    html_content = render_to_string(
        'flatpages/post_created_email.html',
        {
            'text': preview,
            'link': f'http://127.0.0.1:8000/news/{pk}',
        }
    )

    msg = EmailMultiAlternatives(
        subject=title,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()

@shared_task
@receiver(m2m_changed, sender=PostCategory)  #рассылка уведомлений подписчикам после создания новости
def notify_about_new_post(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        categories = instance.postCategory.all()
        subscribers: list[str] = []
        for postCategory in categories:
            subscribers += postCategory.subscribers.all()
        subscribers = [s.email for s in subscribers]

        send_notifications(instance.preview(), instance.pk, instance.title, subscribers)


#@shared_task
#def hello():  #проверка работы программы: отправка на панель selery сообщения "Hello, world!" каждыу 10 сек
#    time.sleep(10)
#    print("Hello, world!")

#@shared_task
#def printer(N):  #проверка работы программы: отправка на панель selery счетчика от 1 до N с периодичностью в 1 сек
#   for i in range(N):
#        time.sleep(1)
#        print(i+1)


@shared_task
def notify_weekly(): #еженедельная рассылка с последними новостями (каждый понедельник в 8:00 утра)
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)
    posts = Post.objects.filter(dateCreation__gte=last_week)
    categories = set(posts.values_list('postCategory__name', flat=True))
    subscribers = set(Category.objects.filter(name__in=categories).values_list('subscribers__email', flat=True))
    html_content = render_to_string(
        'flatpages/daily_post.html',
        {
            'link': settings.SITE_URL,
            'posts': posts,
        }
    )

    msg = EmailMultiAlternatives(
        subject='Статьи за неделю',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,  #список email
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()
