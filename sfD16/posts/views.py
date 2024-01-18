import datetime
import posts.tasks as tasks
from django.conf import settings
from django.shortcuts import render, redirect

from django.utils.timezone import make_aware
from django.views.generic import ListView
from .models import Post, Response
from .forms import AddPostForm, ResponseForm, PostFilter
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile
from django.core.mail import send_mail, EmailMultiAlternatives


class PostList(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    ordering = '-time_create'
    paginate_by = 3
    #def get_ordering(self):
    def get_queryset(self):
        if self.request.GET.get('category', None):
            catid = self.request.GET.get('category')
            return Post.objects.filter(category__id=catid).order_by('-time_create')
        else:
            return super().get_queryset()
    def get_context_data(self, **kwargs):
        context = super().get_context_data( **kwargs)
        if self.request.user.is_anonymous==False:
            context['usertimezone'] = UserProfile.objects.get(user=self.request.user).timezone
        if self.request.GET.get('category', None):
            context['form'] = PostFilter(initial={'category':self.request.GET.get('category')})
        context.setdefault('form', PostFilter())
        tasks.maildelivery.delay()
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
            obj.save()
            tasks.msgrespcreate.delay(postid = post.id) # отправка письма после создания отклика
            content['response'] = Response.objects.filter(post=post, sender=request.user).first()
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
        if respaccepted:
            tasks.msgrespaccept.delay(respid=respid) # celery отправка письма создателю отклика что его отклик подтвердили
    if request.GET.get('send',None):
        content['title'] = 'Исходящие отклики'
        content.setdefault('responses', Response.objects.filter(sender=request.user))   # исходящие отклики
    elif request.GET.get('postfilter',None): #входящие отклики с фильтром
        content['title'] = 'Входящие отклики'
        content.setdefault('responses', Response.objects.filter(post__id=request.GET.get('postfilter')))
        content['postlist'] = Post.objects.filter(author=request.user)
        content['choosenpost'] = int(request.GET.get('postfilter'))
    else:
        content['title'] = 'Входящие отклики'
        content.setdefault('responses', Response.objects.filter(post__author=request.user))  # это входящие отклики
        content['postlist'] = Post.objects.filter(author=request.user)

    content['usertimezone'] = UserProfile.objects.get(user=request.user).timezone
    return render(request, 'responses.html', content)


def handler403(request, e):
    return render(request, 'handler403.html')