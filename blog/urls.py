# from django.urls import path
# from .views import RegistrationView, LoginView, LogoutView, CommentCreateView, CommentListView, BlogPostCRUDView

# urlpatterns = [
#     # path('', views.home, name='home'),
#     # path('home', views.home, name='home'),
#     path('register/', RegistrationView.as_view(), name='registration'),
#     path('login/', LoginView.as_view(), name='login'),
#     path('logout/', LogoutView.as_view(), name='logout'),
#     # List all posts and create a new post
#     path('posts/', BlogPostCRUDView.as_view(), name='post-list'),
#     # Retrieve, update, or delete a specific post by ID
#     path('posts/<int:pk>/', BlogPostCRUDView.as_view(), name='post-detail'),
#     path('posts/<int:post_id>/comments/', CommentCreateView.as_view(), name='comment-create'),
#     path('comments/', CommentListView.as_view(), name='comment-list'),
# ]

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BlogPostViewSet, RegistrationView, LoginView, LogoutView, CommentCreateView, CommentListView

# Create a router and register the viewset with it.
router = DefaultRouter()
router.register('posts', BlogPostViewSet)
# router.register(r'comments', CommentViewSet)

urlpatterns = [
    # Your other URL patterns go here
    path('register/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/', include(router.urls)),
    path('api/posts/<int:post_id>/comments/', CommentCreateView.as_view(), name='comment-create'),
    path('api/comments/', CommentListView.as_view(), name='comment-list'),
]