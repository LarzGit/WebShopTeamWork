from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Занятий меіл")
        return value

    def validate(self, data):

        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Різні паролі"})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(

            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=User.Role.CUSTOMER,  
        )
        return user