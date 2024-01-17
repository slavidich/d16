from django.urls import path

from .views import *

urlpatterns = [
    path('', PostList.as_view(), name='posts'),
    path('addpost', addpost, name='addpost'),
    path('post/<int:id>', postview, name='post'),
    path('post/<int:id>/change', postchange, name='postchange'),
    path('responses', responsesview, name='responses'),

]