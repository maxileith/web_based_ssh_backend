from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse
import json
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from rest_framework import status
from rest_framework.decorators import api_view

# Create your views here.
from auth.serializers import UserSerializer
import jwt
import datetime


@api_view(['POST'])
def login(request):

    if request.method == "POST":
        content = request.data

        user = authenticate(
            username=content['username'], password=content['password'])

        if user is not None:
            payload = {
                "username": content['username'],
            }
            #  {expiresIn: "4hr"}
            token = jwt.encode(payload, "ha", algorithm="HS256",
                               headers={"expiresIn": "4hr"})
            response = HttpResponse(status=status.HTTP_202_ACCEPTED)
            response.set_cookie(key='token', value=token,
                                max_age=86400, samesite='strict')
            return response
        else:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def register(request):
    if request.method == "POST":
        content = request.data

        # TODO: clean input

        if not User.objects.filter(username=content['username']).exists():
            user = User.objects.create_user(
                content['username'], content['email'], content['password'])
            user.last_name = content['last_name']
            user.first_name = content['first_name']
            user.save()

            serializer = UserSerializer(user)
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

        return HttpResponse(status=status.HTTP_409_CONFLICT)


@api_view(['GET'])
@login_required(redirect_field_name=None)
def verify(request):
    if request.method == 'GET':
        return JsonResponse(
            {
                'success': True
            },
            status=status.HTTP_200_OK
        )
