from django.shortcuts import get_object_or_404
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

    Args:
        request (Request): request object of the http request

    Returns:
        JsonResponse: returns JSON object and HTTP status code
    """

    if request.method == 'GET':
        # get known hosts file content
        known_host = get_object_or_404(KnownHost, user=request.user)

        try:
            # open and read file, then return the content
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
        # get known hosts file content
        known_host = get_object_or_404(KnownHost, user=request.user)

        if not 'content' in request.data.keys():
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        try:
            # overwrite content of the known hosts file
            with open(known_host.file.path, mode='w') as f:
                f.truncate()
                f.write(request.data['content'])
        except FileNotFoundError:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
