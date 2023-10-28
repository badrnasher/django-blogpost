from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('sign-up', views.sign_up, name='sign-up'),
    path('profile', views.profile, name='profile'),
    path('create-post', views.create_post, name='post-create'),
    path('post/<str:post_id>/', views.post_detail, name='post-detail'),
    path('post/<str:post_id>/edit/', views.edit_post, name='post-edit'),

]