from django import forms
from .models import *
from allauth.account.forms import SignupForm

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['text']


class AddPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category']

class PostFilter(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['category']