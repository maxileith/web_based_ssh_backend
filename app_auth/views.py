from django.contrib.auth import authenticate, logout
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core.files.uploadedfile import SimpleUploadedFile

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import password_validation as validator
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view

import re
import uuid
import jwt

# Create your views here.
from app_auth.models import UserProfile
from datetime import datetime, timedelta

from web_based_ssh_backend.settings import URL_FRONTEND, SECRET_KEY
from known_hosts.models import KnownHost
from .models import Token
from .serializers import UserSerializer

from app_auth.mail import send_verify_mail


def list_content_matches(list1, list2):
    return set(list1) == set(list2)


@api_view(['POST'])
def login(request):
    """login [summary]

            Enables the login for a user. Creates a new JWT Token for the user and transmits the newly generated
            token to the user.

            Args:
                request:  request object passed by Django

            Returns: HttpResponse or JsonResponse
            """

    if request.method == "POST":

        if not list_content_matches(request.data.keys(), ['username', 'password']):
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(
            username=request.data['username'], password=request.data['password'])

        if user is not None and user.is_active == True:
            expires = datetime.utcnow() + timedelta(minutes=120)
            payload = {
                "username": request.data['username'],
                "exp": expires,
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

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
    """logout_view [summary]

            Enables the logout of a user. Disables the used JWT Token and logs the user out.

            Args:
                request:  request object passed by Django

            Returns: HttpResponse
            """

    if request.method == "POST":
        t = request.headers["Token"]
        if t:
            token = Token.objects.filter(token=t).first()
            if token:
                token.active = False
                token.save()
        logout(request)
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def register(request):
    """register [summary]

            Enables registration of new users. Creates new entry in DB, a new empty
            known_host file, a new user profile and sends verification email.

            Args:
                request:  request object passed by Django

            Returns: JsonResponse - returns status message
            """

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

        # check email syntax
        pattern = re.compile(
            '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        if not pattern.match(request.data['email']):
            return JsonResponse(
                {
                    'message': 'E-Mail is not valid.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            request.data['username'], request.data['email'], request.data['password'])
        user.last_name = request.data['last_name']
        user.first_name = request.data['first_name']
        user.is_active = False

        user.save()

        known_host = KnownHost.objects.create(user=user)
        known_host.file = SimpleUploadedFile(content="", name="empty")
        known_host.save()

        # create new profile
        profile, _ = UserProfile.objects.get_or_create(user=user)

        # create random string
        profile.email_token = str(uuid.uuid4())
        profile.save()

        try:
            send_verify_mail(user.email, profile.email_token)
        except:
            return JsonResponse(
                {
                    'message': 'Could not send verification email.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = UserSerializer(user)

        return JsonResponse(
            {
                'message': 'You have successfully registered. Verify your E-Mail.'
            },
            status=status.HTTP_201_CREATED
        )


@api_view(['GET'])
@login_required(redirect_field_name=None)
def verify(request):
    """verify [summary]

            Checks whether user is logged in.

            Args:
                request:  request object passed by Django

            Returns: JsonResponse - login status
            """

    if request.method == 'GET':
        return JsonResponse(
            {
                'success': True
            },
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
def verify_email(request, token):
    """verify_email [summary]

            Verifies the email address of a user and enables the user.

            Args:
                request:  request object passed by Django
                token: token used to identify user

            Returns: HttpResponseRedirect - redirect to login page
            """

    user_profile = get_object_or_404(UserProfile, email_token=token)
    user = user_profile.user
    user.is_active = True
    user.save()

    user_profile.email_token = None
    user_profile.save()

    return HttpResponseRedirect(redirect_to=f'http://{URL_FRONTEND}/login')
