from rest_framework import serializers
from .models import CustomUser

# Serializer for CustomUser
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'role', 'balance', 'password')
    
    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data.get('role', 'buyer'),
            balance=validated_data.get('balance', 0.00)
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
