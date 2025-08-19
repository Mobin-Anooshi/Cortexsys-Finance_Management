from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

class UserRegisterSerializers(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username','email','password')
        extra_kwargs={
            'password':{'write_only':True},
        }

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

    def validate_username(self,value):
        if 'admin' == value:
            raise serializers.ValidationError('username cant be admin')
        return value

class UserLoginSerializers(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True,required=True)

    def validate(self, data):
        user = authenticate(username=data['username'],password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError('username and password is invalid')






    # def validate_username(self,value):
    #     if value == 'admin':
    #         raise serializers.ValidationError('username cant be admin')
    #     return value
    #
    # def validate(self, data):
    #     if data['password'] != data['password2']:
    #         raise serializers.ValidationError('password must match')
    #     return data