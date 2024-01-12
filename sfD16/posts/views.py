from django.shortcuts import render
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
    content = dict(form=form)
    return render(request, 'addpost.html', content)

def postview(request, id):
    post = Post.objects.get(id=id)
    content = dict(post=post)
    content['title'] = 'test'
    return render(request, 'post.html', content)