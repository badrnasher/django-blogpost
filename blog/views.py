from django.shortcuts import render, redirect
from .forms import RegisterForm, PostForm, CommentForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout
from django.contrib.auth.models import Group
from .models import BlogPost, Tag, User
from .models import BlogPost, Comment


@login_required(login_url="/login")
def home(request):
    posts = BlogPost.objects.all()
    comments = Comment.objects.all()

    if request.method == "POST":
        post_id = request.POST.get("post-id")
        user_id = request.POST.get("user-id")

        if post_id:
            post = BlogPost.objects.filter(id=post_id).first()
            if post and (post.author == request.user or request.user.has_perm("main.delete_post")):
                post.delete()
        elif user_id:
            user = User.objects.filter(id=user_id).first()
            if user and request.user.is_staff:
                try:
                    group = Group.objects.get(name='default')
                    group.user_set.remove(user)
                except:
                    pass

                try:
                    group = Group.objects.get(name='mod')
                    group.user_set.remove(user)
                except:
                    pass

        
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user
                comment.save()
                
            
    else:
        form = CommentForm()


    return render(request, 'main/home.html', {"posts": posts,"comments":comments, "form": form})

@login_required(login_url="/login")
# @permission_required("main.add_post", login_url="/login", raise_exception=True)
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("/home")
    else:
        form = PostForm()

    return render(request, 'main/create_post.html', {"form": form})


def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()

    return render(request, 'registration/signup.html', {"form": form})

@login_required(login_url="/login")
def post_detail(request, post_id):
    post = BlogPost.objects.get(pk=post_id)
    comments = Comment.objects.filter(post=post)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', post_id=post_id)

    else:
        form = CommentForm()

    return render(request, 'main/post_detail.html', {"post": post, "form": form})

@login_required(login_url="/login")
def profile(request):
    post = BlogPost.objects.filter(author=request.user)
    return render(request, 'main/profile.html', {"posts": post})


@login_required(login_url="/login")
def edit_post(request, post_id):
    post = BlogPost.objects.get(pk=post_id)
    form = PostForm(instance=post)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post.save()
            return redirect('post-detail', post_id=post_id) 

    return render(request, 'main/create_post.html', {"form": form})