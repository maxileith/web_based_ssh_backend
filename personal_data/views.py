from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from django.forms.models import model_to_dict
from django.contrib.auth import password_validation as validator
from django.core.exceptions import ValidationError
import re

from django.contrib.auth.models import User


@api_view(['GET', 'PATCH'])
@login_required(redirect_field_name=None)
def details(request):
    if request.method == 'GET':
        user = model_to_dict(request.user, fields=[
            'username', 'first_name', 'last_name', 'email'])
        return JsonResponse(user, status=status.HTTP_200_OK)

    if request.method == 'PATCH':
        user: User = request.user

        if 'password' in request.data.keys() and 'old_password' in request.data.keys():
            if not user.check_password(request.data['old_password']):
                return JsonResponse(
                    {
                        'message': 'The old password is incorrect.'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            try:
                validator.validate_password(
                    password=request.data['password'], user=user)
            except ValidationError:
                return JsonResponse(
                    {
                        'message': 'Password does not meet the password policies.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(request.data['password'])
            request.data.pop('password')
            request.data.pop('old_password')
        elif 'password' in request.data.keys() or 'old_password' in request.data.keys():
            return JsonResponse(
                {
                    'message': 'To change the password, you need to provide both the old and the new password.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if 'email' in request.data.keys():
            pattern = re.compile(
                '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            if not pattern.match(request.data['email']):
                return JsonResponse(
                    {
                        'message': 'E-Mail is not valid.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.email = request.data['email']
            request.data.pop('email')

        if 'last_name' in request.data.keys():
            if request.data['last_name'] == '':
                return JsonResponse(
                    {
                        'message': 'Last name cannot be empty.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.last_name = request.data['last_name']
            request.data.pop('last_name')

        if 'first_name' in request.data.keys():
            if request.data['first_name'] == '':
                return JsonResponse(
                    {
                        'message': 'First name cannot be empty.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.first_name = request.data['first_name']
            request.data.pop('first_name')

        if len(request.data.keys()):
            return JsonResponse(
                {
                    'message': 'Unknown attributes.'
                },
                status=status.HTTP_409_CONFLICT
            )

        user.save()

        return JsonResponse(
            {
                'message': 'The changes were successfully adopted.'
            },
            status=status.HTTP_200_OK
        )
