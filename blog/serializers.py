from rest_framework import serializers
from .models import BlogPost, Comment, User, Tag
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['tag']

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            
            if not user:
                raise serializers.ValidationError("Invalid login credentials")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'")

        data['user'] = user
        return data

class BlogPostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    tags = TagSerializer(many=True)
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'author', 'tags', 'created_at', 'updated_at']


    
class BlogPostDetailSerializer(BlogPostSerializer):

    comments = serializers.SerializerMethodField(read_only=True)

    class Meta(BlogPostSerializer.Meta):
        fields = BlogPostSerializer.Meta.fields + ['content', 'comments']

    def get_comments(self, obj):
        comments = obj.comment_set.all()
        serializer = CommentSerializer(comments, many=True)
        return serializer.data
    
    # def get_tags(self, obj):
    #     tags = obj.tags.all()
    #     serializer = TagSerializer(tags, many=True)
    #     return serializer.data

    

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    post = serializers.ReadOnlyField(source='post.title')
    class Meta:
        model = Comment
        fields = '__all__'




