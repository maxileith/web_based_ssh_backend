from django.contrib.auth import authenticate, logout
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse, JsonResponse
import json
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import password_validation as validator
from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.decorators import api_view

# Create your views here.
from app_auth.serializers import UserSerializer
import jwt
from datetime import datetime, timedelta

from known_hosts.models import KnownHost
from web_based_ssh_backend import settings
from .models import Token


def list_content_matches(list1, list2):
    return set(list1) == set(list2)


@api_view(['POST'])
def login(request):

    if request.method == "POST":

        if not list_content_matches(request.data.keys(), ['username', 'password']):
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(
            username=request.data['username'], password=request.data['password'])

        if user is not None:
            expires = datetime.utcnow() + timedelta(minutes=120)
            payload = {
                "username": request.data['username'],
                "exp": expires,
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

            token_object = Token.objects.create(user=user, token=token)
            token_object.save()

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
        t = request.headers["Token"]
        if t:
            token = Token.objects.filter(token=t).first()
            if token:
                token.active = False
                token.save()
        logout(request)
        return HttpResponse(status=204)
    return HttpResponse(status=405)


@api_view(['POST'])
def register(request):
    if request.method == "POST":

        if not list_content_matches(request.data.keys(), ['username', 'password', 'email', 'last_name', 'first_name']):
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=request.data['username']).exists():
            return JsonResponse(
                {
                    'message': 'User already exists.'
                },
                status=status.HTTP_409_CONFLICT
            )

        try:
            validator.validate_password(password=request.data['password'])
        except ValidationError:
            return JsonResponse(
                {
                    'message': 'Password does not meet the password policies.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            request.data['username'], request.data['email'], request.data['password'])
        user.last_name = request.data['last_name']
        user.first_name = request.data['first_name']

        user.save()

        known_host = KnownHost.objects.create(user=user)
        known_host.file = SimpleUploadedFile(content="", name="empty")
        known_host.save()

        serializer = UserSerializer(user)

        return JsonResponse(
            {
                'message': 'You have successfully registered.'
            },
            status=status.HTTP_201_CREATED
        )


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
