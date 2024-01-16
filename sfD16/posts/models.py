from django.contrib.auth.models import User
from django.db import models
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import  RichTextUploadingField

# Create your models here.
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return (self.name)

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = RichTextUploadingField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    time_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (self.title)

    def get_absolute_url(self):
        return reverse('post', kwargs={'id':self.pk})

class Response(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(default=None, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    accepted_datetime = models.DateTimeField(default=None, null=True)


