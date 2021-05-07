from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
import os
from .models import KnownHost


@api_view(['GET', 'PUT'])
@login_required(redirect_field_name=None)
def fileaccess(request):
    """fileaccess [summary]

    - returns the known hosts file associated with the user on HTTP GET request.
    - overwrites the known hists file associated with the user on HTTP PUT request.
    - if the known hosts file does not exist, a new one is created.

    Args:
        request (Request): request object of the http request

    Returns:
        JsonResponse: returns JSON object and HTTP status code
    """

    if request.method == 'GET':
        """
            # get known hosts file content, otherwise create a new one
            try:
                with open(path, mode='r') as f:
                    file_content = f.read()
                    status_code = status.HTTP_200_OK
            except FileNotFoundError:
                f = open(path, mode='x')
                f.close()
                file_content = ''
                status_code = status.HTTP_201_CREATED
        """
        # get known hosts file content, otherwise create a new one
        known_host = get_object_or_404(KnownHost, user=request.user)

        try:
            with open(known_host.file.path, mode='r') as f:
                file_content = f.read()

                return JsonResponse(
                    {
                        'content': file_content,
                    },
                    status=status.HTTP_200_OK
                )
        except FileNotFoundError:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'PUT':
        known_host = get_object_or_404(KnownHost, user=request.user)

        try:
            with open(known_host.file.path, mode='w') as f:
                f.truncate()
                f.write(request.data['content'])
        except FileNotFoundError:
            return HttpResponse(status=404)

        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
