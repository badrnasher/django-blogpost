from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from .models import BlogPost, User, Comment


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class PostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ["title", "content"]



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
