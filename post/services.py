from django.shortcuts import get_object_or_404
from .models import Post


class PostService:

    @staticmethod
    def get_queryset(filters=None):
        posts = Post.objects.all()
        if filters:
            content = filters.get("content")
            title = filters.get("title")
            if content:
                posts = posts.filter(content__icontains=content)
            if title:
                posts = posts.filter(title__icontains=title)
        return posts

    @staticmethod
    def get_by_id(pk):
        return get_object_or_404(Post, pk=pk)

    @staticmethod
    def create(author, validated_data):
        return Post.objects.create(author=author, **validated_data)

    @staticmethod
    def update(post, validated_data):
        for attr, value in validated_data.items():
            setattr(post, attr, value)
        post.save()
        return post

    @staticmethod
    def delete(post):
        post.delete()
