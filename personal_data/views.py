from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from django.forms.models import model_to_dict
from django.contrib.auth import password_validation as validator
from django.core.exceptions import ValidationError
import re
import os
from web_based_ssh_backend.settings import KNOWN_HOSTS_DIRECTORY

from django.contrib.auth.models import User


@api_view(['GET', 'PATCH', 'DELETE'])
@login_required(redirect_field_name=None)
def details(request):
    """details [summary]

    this endpoint manages the personal details of a user
    - returns all personal details on HTTP GET request
    - updates the personal details specified as JSON on a HTTP PATCH request
        - to change password 'password' and 'old_password' has to be given
    - deletes a user on HTTP DELETE request

    Args:
        request (Request): request object of the HTTP request

    Returns:
        JsonResponse: returns JSON object and HTTP status code
    """

    if request.method == 'GET':
        user = model_to_dict(request.user, fields=[
            'username', 'first_name', 'last_name', 'email'])
        return JsonResponse(user, status=status.HTTP_200_OK)

    if request.method == 'PATCH':
        user: User = request.user

        if 'password' in request.data.keys() and 'old_password' in request.data.keys():
            # check if old password is correct
            if not user.check_password(request.data['old_password']):
                return JsonResponse(
                    {
                        'message': 'The old password is incorrect.'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            # check if new password meets the password policy
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
            # update password
            user.set_password(request.data['password'])
            request.data.pop('password')
            request.data.pop('old_password')
        elif 'password' in request.data.keys() or 'old_password' in request.data.keys():
            # password or old_password is missing
            return JsonResponse(
                {
                    'message': 'To change the password, you need to provide both the old and the new password.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if 'email' in request.data.keys():
            # make sure 'email' is actually an email
            pattern = re.compile(
                '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            if not pattern.match(request.data['email']):
                return JsonResponse(
                    {
                        'message': 'E-Mail is not valid.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            # save new email
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
            # if there are still unprocessed attributes in the request, unknown
            # attributes have been specified. This may be due to a spelling error
            # in the request, for example.
            return JsonResponse(
                {
                    'message': 'Unknown attributes.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # save the changes to the user
        user.save()

        return JsonResponse(
            {
                'message': 'The changes were successfully adopted.'
            },
            status=status.HTTP_200_OK
        )

    if request.method == 'DELETE':
        user: User = request.user

        user.delete()

        return JsonResponse(
            {
                'message': 'The user was deleted successfully.'
            },
            status=status.HTTP_200_OK
        )
