import datetime

from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.timezone import make_aware
from django.views.generic import ListView
from .models import Post, Response
from .forms import AddPostForm, ResponseForm
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile
from django.core.mail import send_mail, EmailMultiAlternatives


class PostList(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    ordering = '-time_create'
    def get_context_data(self, **kwargs):
        context = super().get_context_data( **kwargs)
        if self.request.user.is_anonymous==False:
            context['usertimezone'] = UserProfile.objects.get(user=self.request.user).timezone
        return context

@login_required
def addpost(request):
    form = AddPostForm()
    if request.method =='POST':
        form = AddPostForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = request.user
            obj.save()
            return redirect('post', obj.id)
    content = dict(form=form)

    return render(request, 'addpost.html', content)

def postview(request, id):
    post = Post.objects.get(id=id)
    content = {}
    content['post'] = post
    content['title'] = 'test'

    if request.user.is_anonymous==False:
        content['usertimezone'] = UserProfile.objects.get(user=request.user).timezone
        content['response'] = Response.objects.filter(post=post, sender=request.user).first()
    content['form'] = ResponseForm()
    if request.method=='POST':
        form = ResponseForm(request.POST)
        if form.is_valid(): # отправка отклика!
            obj = form.save(commit=False)
            obj.sender = request.user
            obj.post = post
            #obj.save()
            # отправка письма после создания отклика
            html_content = render_to_string(
                template_name='msgrespcreate.html',
                context={
                    'post':post,
                    'link':settings.SITE_URL
                }
            )
            msg = EmailMultiAlternatives(
                subject='Новый отклик на Ваше объявление!',
                body='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[post.author.email,]
            )
            msg.attach_alternative(html_content, 'text/html')
            msg.send()


    return render(request, 'post.html', content)

@login_required
def postchange(request, id):
    post = Post.objects.get(id=id)
    if request.user!=post.author:
        return handler403(request, Exception('Permission Denied'))
    if request.method == 'POST':
        form = AddPostForm(request.POST)
        if form.is_valid():
            post.title = form['title'].value()
            post.content = form['content'].value()
            post.save()
            return redirect('post', post.id)
    form =  AddPostForm(instance=post)
    content = {}
    content['form'] = form
    return render(request, 'postchange.html', content)

@login_required
def responsesview(request):
    content = {}
    if request.method=='POST': # отправка ответа на отклик!!
        respid = request.POST.get('accept', None) or request.POST.get('reject', None)
        respaccepted = True if request.POST.get('accept', None) else False
        resp = Response.objects.get(id=respid)
        resp.accepted = respaccepted
        resp.accepted_datetime = make_aware(datetime.datetime.utcnow())
        resp.save()
    if request.GET.get('send',None):
        content['title'] = 'Исходящие отклики'
        content['responses'] = Response.objects.filter(sender=request.user)  # исходящие отклики
    else:
        content['title'] = 'Входящие отклики'
        content['responses'] = Response.objects.filter(post__author=request.user) # это входящие отклики
    content['usertimezone'] = UserProfile.objects.get(user=request.user).timezone
    return render(request, 'responses.html', content)


def handler403(request, e):
    return render(request, 'handler403.html')