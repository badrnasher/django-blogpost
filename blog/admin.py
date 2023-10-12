from django.contrib import admin
from .models import BlogPost, Comment, User, Tag
from django.contrib.auth.admin import UserAdmin


# class UserAdmin(admin.ModelAdmin):
#     list_display = ('username', 'email', 'is_staff', 'is_superuser')
#     search_fields = ('username', 'email')

admin.site.register(User, UserAdmin)

class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'title': ('title',)}

admin.site.register(BlogPost, BlogPostAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at')
    search_fields = ('author', 'post')

admin.site.register(Comment, CommentAdmin)

admin.site.register(Tag, admin.ModelAdmin)