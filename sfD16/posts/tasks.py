from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post, Response
from django.conf import settings
import time
from django.contrib.auth.models import User
from datetime import datetime, timedelta, time, timezone

@shared_task
def msgrespcreate(postid:int):
    post = Post.objects.get(id=postid)
    html_content = render_to_string(
        template_name='msgrespcreate.html',
        context={
            'post': post,
            'link': settings.SITE_URL
        }
    )
    msg = EmailMultiAlternatives(
        subject='Новый отклик на Ваше объявление!',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[post.author.email, ]
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

@shared_task
def msgrespaccept(respid:int):
    resp = Response.objects.get(id=respid)
    html_content = render_to_string(
        template_name='msgrespaccept.html',
        context={
            'post': resp.post,
            'link': settings.SITE_URL
        }
    )
    msg = EmailMultiAlternatives(
        subject='Ваш отклик одобрил автор объявления!',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[resp.sender.email, ]
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

@shared_task
def maildelivery():
    #posts = Post.objects.filter()
    week_ago = datetime.combine(datetime.today() - timedelta(days=7), time.min).replace(tzinfo=timezone.utc)
    now = datetime.combine(datetime.today() - timedelta(days=1), time.max).replace(tzinfo=timezone.utc)
    posts = Post.objects.filter(time_create__gte=week_ago, time_create__lte=now)
    emails = User.objects.filter(is_active=True, email__isnull=False).values_list('email', flat=True)
    print(emails)
    html_content = render_to_string(
        template_name='msgmaildelivery.html',
        context={
            'posts': posts,
            'link': settings.SITE_URL
        }
    )
    msg = EmailMultiAlternatives(
        subject='Новые объявления за прошедшую неделю!',
        body='',
        from_email=settings.EMAIL_HOST_USER,
        to=emails
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
