from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
import os


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

    WAY_TO_KNOWN_HOSTS = '../ssh/known_hosts/'

    working_dir = os.path.dirname(os.path.realpath(__file__))
    file_name = f'{request.user.id}.keys'
    path = os.path.join(working_dir, WAY_TO_KNOWN_HOSTS, file_name)

    if request.method == 'GET':

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

        return JsonResponse(
            {
                'content': file_content
            },
            status=status_code
        )

    elif request.method == 'PUT':

        with open(path, mode='w') as f:
            f.truncate()
            f.write(request.data['content'])

        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
