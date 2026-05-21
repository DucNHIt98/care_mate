from core.panigation import CustomPagination
from core.permissions import IsAuthor
from core.response import success_response, error_response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import Post
from .serializers import PostSerializer
from .services import PostService


class PostList(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        posts = PostService.get_queryset(request.query_params)
        paginator = CustomPagination()
        page = paginator.paginate_queryset(posts, request)
        if page is not None:
            serializer = PostSerializer(page, many=True)
            return success_response(serializer.data, is_paginated=True, paginator=paginator)
        serializer = PostSerializer(posts, many=True)
        return success_response(
            CustomPagination.format_non_paginated(serializer.data),
            message="Lấy danh sách bài viết!"
        )


class PostCreate(APIView):
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, message="Tạo bài viết thất bại!")
        post = PostService.create(request.user, serializer.validated_data)
        return success_response(PostSerializer(post).data, message="Tạo bài viết thành công!", status=status.HTTP_201_CREATED)


class PostDetail(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        post = PostService.get_by_id(pk)
        serializer = PostSerializer(post)
        return success_response(serializer.data, message="Lấy chi tiết bài viết!")


class PostUpdate(APIView):
    permission_classes = [IsAuthor]

    def put(self, request, pk):
        post = PostService.get_by_id(pk)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post, data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, message="Cập nhật bài viết thất bại!")
        post = PostService.update(post, serializer.validated_data)
        return success_response(PostSerializer(post).data, message="Cập nhật bài viết thành công!")


class PostDelete(APIView):
    permission_classes = [IsAuthor]

    def delete(self, request, pk):
        post = PostService.get_by_id(pk)
        self.check_object_permissions(request, post)
        PostService.delete(post)
        return success_response(None, message="Xóa bài viết thành công!")
