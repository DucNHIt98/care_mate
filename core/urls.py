from django.urls import path, include
from web.views import (
    LoginPageView, RegisterPageView, PostsPageView,
    PostCreatePageView, PostDetailPageView, PostEditPageView,
)

urlpatterns = [
    path('', include('post.urls')),
    path('auth/', include('user.urls')),
    path('web/', LoginPageView.as_view(), name='web-login'),
    path('web/register/', RegisterPageView.as_view(), name='web-register'),
    path('web/posts/', PostsPageView.as_view(), name='web-posts'),
    path('web/posts/create/', PostCreatePageView.as_view(), name='web-post-create'),
    path('web/posts/<int:pk>/', PostDetailPageView.as_view(), name='web-post-detail'),
    path('web/posts/<int:pk>/edit/', PostEditPageView.as_view(), name='web-post-edit'),
]
