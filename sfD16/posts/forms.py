from django import forms
from .models import *
from allauth.account.forms import SignupForm




class AddPostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'content', 'category']