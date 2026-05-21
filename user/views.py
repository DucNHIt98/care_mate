from core.response import success_response, error_response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import RegisterSerializer
from .services import AuthService
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, message="Đăng ký thất bại!")
        user = AuthService.register(serializer.validated_data)
        return success_response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }, message="Đăng ký thành công!", status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
