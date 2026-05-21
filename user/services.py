from django.contrib.auth.models import User


class AuthService:

    @staticmethod
    def register(validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
