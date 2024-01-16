from django.utils import timezone
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView
from .models import Post, Category, Response
from .forms import AddPostForm, ResponseForm
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile
from django.db.models import Q
# Create your views here.
class PostList(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    ordering = '-time_create'
    def get_context_data(self, **kwargs):
        context = super().get_context_data( **kwargs)
        context['timenow'] = timezone.now()
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
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.post = post
            obj.save()

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
    content['title'] = 'Ваши отклики'
    content['responses'] = Response.objects.filter(post__author=request.user) # это входящие отклики
    #content['responses'] = Response.objects.filter(sender=request.user) # исходящие отклики
    return render(request, 'responses.html', content)

@login_required
def sentresponsesview(request):
    content = {}
    content['title'] = 'Исходящие отклики'
    content['responses'] = Response.objects.filter(sender=request.user) # исходящие отклики
    return render(request, 'sentresponses.html', content)

def handler403(request, e):
    return render(request, 'handler403.html')