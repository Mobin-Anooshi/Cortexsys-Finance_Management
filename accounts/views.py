from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserRegisterSerializers,UserLoginSerializers
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken




class UserRegisterAPIView(APIView):
    serializer_class = UserRegisterSerializers
    def post(self,request):
        ser_data = UserRegisterSerializers(data=request.data)
        if ser_data.is_valid():
            ser_data.create(ser_data.validated_data)
            return Response(data=ser_data.data,status=status.HTTP_201_CREATED)
        return Response(data=ser_data.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserLoginAPIView(APIView):
#     def post(self,request):
#         ser_data = UserLoginSerializers(data=request.POST)
#         if ser_data.is_valid():
#             user = ser_data.validated_data
#             refresh = RefreshToken.for_user(user)
#
#             return Response ({
#                 'access-token':str(refresh.access_token),
#                 'refresh-token':str(refresh),
#                 'username':user.username
#
#             },status=status.HTTP_200_OK)
#         return Response (ser_data.errors,status=status.HTTP_400_BAD_REQUEST)