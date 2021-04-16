from django.contrib.auth import authenticate, logout
from django.http import HttpResponse, JsonResponse
import json
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from rest_framework import status
from rest_framework.decorators import api_view

# Create your views here.
from auth.serializers import UserSerializer
import jwt
from datetime import datetime, timedelta

from web_based_ssh_backend import settings


@api_view(['POST'])
def login(request):

    if request.method == "POST":
        content = request.data

        user = authenticate(
            username=content['username'], password=content['password'])

        if user is not None:
            expires = datetime.utcnow() + timedelta(minutes=120)
            payload = {
                "username": content['username'],
                "exp": expires,
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
            return JsonResponse(
                {
                    'token': token
                },
                status=status.HTTP_202_ACCEPTED
            )
        else:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return HttpResponse(status=204)
    return HttpResponse(status=405)


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
