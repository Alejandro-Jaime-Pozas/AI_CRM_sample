from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "curp",
            "date_joined",
        )
        read_only_fields = (
            "id",
            "date_joined",
        )
