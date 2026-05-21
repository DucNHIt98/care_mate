from django.views.generic import TemplateView


class LoginPageView(TemplateView):
    template_name = "web/login.html"


class RegisterPageView(TemplateView):
    template_name = "web/register.html"


class PostsPageView(TemplateView):
    template_name = "web/posts.html"


class PostCreatePageView(TemplateView):
    template_name = "web/post_create.html"


class PostDetailPageView(TemplateView):
    template_name = "web/post_detail.html"


class PostEditPageView(TemplateView):
    template_name = "web/post_edit.html"
