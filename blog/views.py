from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.auth import login, logout
from .models import BlogPost, Tag
from rest_framework import generics, permissions, status, viewsets, pagination, mixins
from rest_framework.response import Response
from .models import BlogPost, Comment
from .serializers import BlogPostSerializer, BlogPostDetailSerializer, CommentSerializer, RegistrationSerializer, LoginSerializer, TagSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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
        serializer = LoginSerializer(data=self.request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            login(request, user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    def get(self, request):
        try:
            # Get the user's token
            token = Token.objects.get(user=self.request.user)
            # Delete the token to log the user out
            token.delete()
            logout(request)
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"message": "Token not found"}, status=status.HTTP_404_NOT_FOUND)


class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostDetailSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    authentication_classes = [SessionAuthentication, BasicAuthentication] 
    pagination_class = pagination.PageNumberPagination  # Add pagination class here

    def get_serializer_class(self):
        if self.action == 'list':
            return BlogPostSerializer
        return BlogPostDetailSerializer

    def perform_create(self, serializer):
        instance = serializer.save(author=self.request.user)
        tags = serializer.validated_data['tags']
        for tag in tags:
            tag, created = Tag.objects.get_or_create(tag=tag['tag'])
            instance.tags.add(tag)

        return instance

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
      
    
    def perform_destroy(self, instance):
        instance.delete()
        return Response({"message": "Post deleted"}, status=status.HTTP_204_NO_CONTENT)

class TagViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet,):
    queryset = Tag.objects.all()  
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    
    def get_queryset(self):
        post_id = self.kwargs['post_id']
        post = BlogPost.objects.get(pk=post_id)
        return post.tags.all()
    
    def retrieve (self, request, *args, **kwargs):
        post_id = self.kwargs['post_id']
        post = BlogPost.objects.get(pk=post_id)
        tag_id = kwargs['pk']
        try:
            tag = Tag.objects.get(pk=tag_id)
        except Tag.DoesNotExist:
            return Response({"message": "Tag not found"}, status=status.HTTP_404_NOT_FOUND)
        if tag in post.tags.all():
            return Response({"message": "Tag found"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Tag not found"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        post_id = self.kwargs['post_id']
        post = BlogPost.objects.get(pk=post_id)
        tag_name = request.data.get('tag', '')
        print("Tag name:", tag_name)
        try:
            if post.author != self.request.user:
                return Response({"message": "You are not authorized to update this tag"}, status=status.HTTP_403_FORBIDDEN)
            tag = Tag.objects.get(tag=tag_name)
        except Tag.DoesNotExist:
            tag = Tag.objects.create(tag=tag_name)
        if tag in post.tags.all():
            post.tags.set([tag])
            print("Updated tags:", post.tags.all())
            return Response({"message": "Tag updated"}, status=status.HTTP_200_OK)
        else:
            post.tags.add(tag)
            print("Updated tags:", post.tags.all())
            return Response({"message": "Tag added"}, status=status.HTTP_200_OK)


    def destroy(self, request, *args, **kwargs):
        post_id = self.kwargs['post_id']
        post = BlogPost.objects.get(pk=post_id)
        tag_id = kwargs['pk']
        try:
            tag = Tag.objects.get(pk=tag_id)
        except Tag.DoesNotExist:
            return Response({"message": "Tag not found"}, status=status.HTTP_404_NOT_FOUND)
        post.tags.remove(tag)
        return Response({"message": "Tag deleted"}, status=status.HTTP_204_NO_CONTENT)
    # def perform_destroy(self, instance):
    #     post_id = self.kwargs['post_id']
    #     post = BlogPost.objects.get(pk=post_id)
    #     post.tags.remove(instance)
    #     return Response({"message": "Tag deleted"}, status=status.HTTP_204_NO_CONTENT)
    
    # def perform_update(self, serializer):
    #     instance = self.get_object()  # Get the tag instance
    #     post_id = self.kwargs['post_id']
    #     post = BlogPost.objects.get(pk=post_id)
    #     post.tags.add(instance)
    #     return Response({"message": "Tag added"}, status=status.HTTP_200_OK)
    

class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer
    def post(self, request, post_id):   
        # Check if the post with the given post_id exists
        try:
            post = BlogPost.objects.get(pk=post_id)
        except BlogPost.DoesNotExist:
            return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        # Create a new comment associated with the post
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            # Grab the content from the validated data
            content = serializer.validated_data['content']

            # Create the new comment
            comment = Comment(content=content, author=self.request.user, post=post)
            comment.save()

            # Return the new comment
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class CommentListView(generics.RetrieveAPIView):
    pagination_class = PageNumberPagination  # Use the default PageNumberPagination
    serializer_class = CommentSerializer  # Use the CommentSerializer
    queryset = Comment.objects.all()  # Get all Comment objects
    def get(self, request, post_id=None):
        try:
            post = BlogPost.objects.get(pk=post_id)
            comments = Comment.objects.filter(post=post)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        except BlogPost.DoesNotExist:    
            return Response({'detail': 'Blog post not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        
class CommentUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def put(self, request, comment_id, post_id):
        # Check if the comment with the given comment_id exists
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response({"message": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if comment.post.id != post_id:
            return Response({"message": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        # Check if the user is the author of the comment
        if request.user != comment.author:
            return Response({"message": "You are not authorized to update this comment"}, status=status.HTTP_403_FORBIDDEN)
        
        # Update the comment
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def delete(self, request, comment_id, post_id):

        # Check if the comment with the given comment_id exists
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response({"message": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        if comment.post.id != post_id:
            return Response({"message": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        # Check if the user is the author of the comment
        if request.user != comment.author:
            return Response({"message": "You are not authorized to delete this comment"}, status=status.HTTP_403_FORBIDDEN)
        # Delete the comment
        comment.delete()
        return Response({"message": "Comment deleted"}, status=status.HTTP_204_NO_CONTENT)

