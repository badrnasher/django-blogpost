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

# from django.urls import path, include
# from rest_framework.routers import DefaultRouter

# from .views import BlogPostViewSet, RegistrationView, LoginView, LogoutView, CommentCreateView, CommentListView,CommentUpdateView, CommentDeleteView, TagViewSet

# # Create a router and register the viewset with it.
# router = DefaultRouter()
# router.register('posts', BlogPostViewSet)

# urlpatterns = [
#     # Your other URL patterns go here
#     path('register/', RegistrationView.as_view(), name='registration'),
#     path('login/', LoginView.as_view(), name='login'),
#     path('logout/', LogoutView.as_view(), name='logout'),
#     path('api/', include(router.urls)),
#     path('api/post/<int:post_id>/comments/', CommentListView.as_view(), name='comment-list'),
#     path('api/post/<int:post_id>/comment/', CommentCreateView.as_view(), name='comment-create'),
#     path('api/post/<int:post_id>/comment/<int:comment_id>', CommentUpdateView.as_view(), name='comment-update'),
#     path('api/post/<int:post_id>/comment/<int:comment_id>', CommentDeleteView.as_view(), name='comment-delete'),
#     path('api/post/<int:post_id>/tags/', TagViewSet.as_view({'get':'list','put': 'update','delete': 'destroy'}), name='tag-list'),
#     path('api/post/<int:post_id>/tags/<int:pk>', TagViewSet.as_view({'get':'retrieve', 'delete': 'destroy'}), name='tag-detail'),
# ]