from django.urls import path
from . import views
from .views import RegistrationView, LoginView, LogoutView, CommentCreateView, CommentListView, BlogPostCRUDView

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('register/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # List all posts and create a new post
    path('posts/', BlogPostCRUDView.as_view(), name='post-list'),
    # Retrieve, update, or delete a specific post by ID
    path('posts/<int:pk>/', BlogPostCRUDView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/comments/', CommentCreateView.as_view(), name='comment-create'),
    path('comments/', CommentListView.as_view(), name='comment-list'),
]