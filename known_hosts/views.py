from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
import os
from .models import KnownHost
from custom_utils import list_content_matches


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
        try:
            known_host = KnownHost.objects.get(user=request.user)
        except KnownHost.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

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
        if not list_content_matches(request.data.keys(), ['content']):
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        # get known hosts file content
        try:
            known_host = KnownHost.objects.get(user=request.user)
        except KnownHost.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        try:
            # overwrite content of the known hosts file
            with open(known_host.file.path, mode='w') as f:
                f.truncate()
                f.write(request.data['content'])
        except FileNotFoundError:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
