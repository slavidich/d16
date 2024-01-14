from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView
from .models import Post, Category
from .forms import AddPostForm
# Create your views here.
class PostList(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'

def addpost(request):
    form = AddPostForm()
    if request.method =='POST':
        form = AddPostForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = request.user
            obj.save()
            return redirect('posts')
    content = dict(form=form)

    return render(request, 'addpost.html', content)

def postview(request, id):
    post = Post.objects.get(id=id)
    content = dict(post=post)
    content['title'] = 'test'
    return render(request, 'post.html', content)

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
    content = dict(form=form)
    return render(request, 'postchange.html', content)

def handler403(request, e):
    return render(request, 'handler403.html')