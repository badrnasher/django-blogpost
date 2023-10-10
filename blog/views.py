from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.shortcuts import render, redirect
from .forms import RegisterForm, PostForm, CommentForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout
from django.contrib.auth.models import User, Group
from .models import BlogPost
from rest_framework import generics, permissions, status, viewsets, pagination, mixins
from rest_framework.response import Response
from .models import BlogPost, Comment
from .serializers import BlogPostSerializer, CommentSerializer, RegistrationSerializer, LoginSerializer, CommentCreateUpdateSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are allowed for superusers and staff
        if request.user.is_superuser or request.user.is_staff:
            return True

        # Write permissions are only allowed to the owner of the post
        return obj.author == request.user
    
class RegistrationView(APIView):
    serializer_class = RegistrationSerializer
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    serializer_class = LoginSerializer
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            login(request, user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            # Get the user's token
            token = Token.objects.get(user=request.user)
            # Delete the token to log the user out
            token.delete()
            logout(request)
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"message": "Token not found"}, status=status.HTTP_404_NOT_FOUND)


class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    pagination_class = pagination.PageNumberPagination  # Add pagination class here


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

    
class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentCreateUpdateSerializer
    def post(self, request, post_id):
        # Check if the post with the given post_id exists
        try:
            post = BlogPost.objects.get(pk=post_id)
        except BlogPost.DoesNotExist:
            return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        # Create a new comment associated with the post
        serializer = CommentCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=self.request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class CommentListView(generics.RetrieveAPIView):
    pagination_class = PageNumberPagination  # Use the default PageNumberPagination
    serializer_class = CommentSerializer  # Use the CommentSerializer
    queryset = Comment.objects.all()  # Get all Comment objects
    def get(self, request):
        queryset = Comment.objects.all()  # Get all Comment objects
        page = self.paginate_queryset(queryset)  # Paginate the queryset

        if page is not None:
            serializer = CommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)

# class CommentViewSet(viewsets.ModelViewSet):
#     serializer_class = CommentSerializer
#     queryset = Comment.objects.all()
#     permission_classes = [IsAuthenticated]  # Add the custom permission class here
#     authentication_classes = [SessionAuthentication, BasicAuthentication]
#     pagination_class = pagination.PageNumberPagination  # Add pagination class here

#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user)

# class PostAPIView(APIView):
#     pagination_class = PageNumberPagination
#     serializer_class = BlogPostSerializer
#     permission_classes = [IsAuthorOrReadOnly]

#     def get(self, request, pk=None):
#         if pk:
#             try:
#                 post = BlogPost.objects.get(pk=pk)
#                 serializer = BlogPostSerializer(post)
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             except BlogPost.DoesNotExist:
#                 return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             posts = BlogPost.objects.all()
#             serializer = BlogPostSerializer(posts, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
        
#     def post(self, request):
#         serializer = BlogPostSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(author=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk):
#         try:
#             post = BlogPost.objects.get(pk=pk)
#             # if post.author != request.user and not request.user.is_staff:
#             #     return Response({"message": "You do not have permission to update this post"}, status=status.HTTP_403_FORBIDDEN)
#         except BlogPost.DoesNotExist:
#             return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

#         serializer = BlogPostSerializer(post, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         try:
#             post = BlogPost.objects.get(pk=pk)
#             # if post.author != request.user:
#             #     return Response({"message": "You do not have permission to delete this post"}, status=status.HTTP_403_FORBIDDEN)
#         except BlogPost.DoesNotExist:
#             return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

#         post.delete()
#         return Response({"message": "Post deleted"}, status=status.HTTP_204_NO_CONTENT)


# class BlogPostCRUDView(generics.GenericAPIView):
#     queryset = BlogPost.objects.all()
#     serializer_class = BlogPostSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     authentication_classes = [SessionAuthentication, BasicAuthentication]
#     pagination_class = PageNumberPagination  # Add pagination class here

#     def get(self, request, pk=None):
#         if pk:
#             try:
#                 post = self.queryset.get(pk=pk)
#             except BlogPost.DoesNotExist:
#                 return Response({'detail': 'Blog post not found.'}, status=status.HTTP_404_NOT_FOUND)
#             serializer = self.serializer_class(post)
#             return Response(serializer.data)
#         else:
#             # Handle pagination for the list of blog posts
#             paginated_queryset = self.paginate_queryset(self.queryset)
#             serializer = self.serializer_class(paginated_queryset, many=True)
#             return self.get_paginated_response(serializer.data)
        
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             serializer.save(author=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk):
#         try:
#             post = self.queryset.get(pk=pk)
#         except BlogPost.DoesNotExist:
#             return Response({'detail': 'Blog post not found.'}, status=status.HTTP_404_NOT_FOUND)

#         self.check_object_permissions(request, post)

#         serializer = self.serializer_class(post, data=request.data)
#         if serializer.is_valid():
#             serializer.save(author=request.user)
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         try:
#             post = self.queryset.get(pk=pk)
#         except BlogPost.DoesNotExist:
#             return Response({'detail': 'Blog post not found.'}, status=status.HTTP_404_NOT_FOUND)

#         self.check_object_permissions(request, post)
#         post.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)



# class CommentCreateView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = CommentSerializer
#     def post(self, request, post_id):
#         # Check if the post with the given post_id exists
#         try:
#             post = BlogPost.objects.get(pk=post_id)
#         except BlogPost.DoesNotExist:
#             return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

#         # Create a new comment associated with the post
#         serializer = CommentSerializer(data=request.data)
#         print(request)
#         if serializer.is_valid():
#             serializer.save(author=self.request.user, post=post)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
# class CommentListView(generics.RetrieveAPIView):
#     pagination_class = PageNumberPagination  # Use the default PageNumberPagination
#     serializer_class = CommentSerializer  # Use the CommentSerializer
#     queryset = Comment.objects.all()  # Get all Comment objects
#     def get(self, request):
#         queryset = Comment.objects.all()  # Get all Comment objects
#         page = self.paginate_queryset(queryset)  # Paginate the queryset

#         if page is not None:
#             serializer = CommentSerializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
        
#         serializer = CommentSerializer(queryset, many=True)
#         return Response(serializer.data)

# @login_required(login_url="/login")
# def home(request):
#     posts = BlogPost.objects.all()

#     if request.method == "POST":
#         post_id = request.POST.get("post-id")
#         user_id = request.POST.get("user-id")

#         if post_id:
#             post = BlogPost.objects.filter(id=post_id).first()
#             if post and (post.author == request.user or request.user.has_perm("main.delete_post")):
#                 post.delete()
#         elif user_id:
#             user = User.objects.filter(id=user_id).first()
#             if user and request.user.is_staff:
#                 try:
#                     group = Group.objects.get(name='default')
#                     group.user_set.remove(user)
#                 except:
#                     pass

#                 try:
#                     group = Group.objects.get(name='mod')
#                     group.user_set.remove(user)
#                 except:
#                     pass

#     return render(request, 'main/home.html', {"posts": posts})


# @login_required(login_url="/login")
# @permission_required("main.add_post", login_url="/login", raise_exception=True)
# def create_post(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.author = request.user
#             post.save()
#             return redirect("/home")
#     else:
#         form = PostForm()

#     return render(request, 'main/create_post.html', {"form": form})


# def sign_up(request):
#     if request.method == 'POST':
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('/home')
#     else:
#         form = RegisterForm()

#     return render(request, 'registration/sign_up.html', {"form": form})

# @login_required(login_url="/login")
# def post_detail(request, post_id):
#     post = BlogPost.objects.get(pk=post_id)
#     comments = Comment.objects.filter(post=post)

#     if request.method == 'POST':
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.author = request.user
#             comment.post = post
#             comment.save()
#             return redirect('post_detail', post_id=post_id)

#     else:
#         form = CommentForm()

#     return render(request, 'post_detail.html', {"form": form})