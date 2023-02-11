from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
#from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.db.models.signals import m2m_changed

from .models import PostCategory


def send_notifications(preview, pk, title, subscribers):
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

@receiver(m2m_changed, sender=PostCategory)
def notify_about_new_post(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        print('Я сигнал!')

        categories = instance.postCategory.all()
        print(f'{categories = }')

        subscribers: list[str] = []
        for postCategory in categories:
            subscribers += postCategory.subscribers.all()
        print(f'{subscribers = }')

        subscribers = [s.email for s in subscribers]
        print(f'{subscribers = }')

        send_notifications(instance.preview(), instance.pk, instance.title, subscribers)


