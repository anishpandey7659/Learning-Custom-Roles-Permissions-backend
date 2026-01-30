from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializer import *
from django.contrib.auth import authenticate

from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group, Permission

class AuthViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def register(self,request):
        serializer =RegisterSeriliazer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSeriliazer(user).data, status=201) 
        return Response(serializer.errors)
    
    @action(detail=False, methods=['post'])
    def login(self,request):
        serializer =LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate( 
                username = serializer.validated_data['username'], 
                password = serializer.validated_data['password']
                )
            if user:
                token,_= Token.objects.get_or_create(user=user)
                data =UserSeriliazer(user).data
                data['token']=token.key
                return Response(data)
            return Response({"message":"Invalid credientials"})
        return Response(serializer.errors)


from .permission import *
class StaffViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated,IsAdmin] 

    @action(detail=False, methods=['post'])
    def create_staff(self, request):
        serializer = StaffSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSeriliazer(user).data)
        return Response(serializer.errors, status=400)


class PatientViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAccountant]

    @action(detail=False, methods=["post"])
    def create_patient(self, request):
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"id": user.id, "username": user.username, "role": user.role})
        return Response(serializer.errors, status=400)

            
        
        
