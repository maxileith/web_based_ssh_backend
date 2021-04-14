from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view
from .models import SSHSession
from .serializers import SSHSessionSerializer
import json


@api_view(['GET', 'POST'])
@login_required
def sessions(request):
    """sessions [summary]

    - returns all SSH sessions saved for the user on HTTP GET Request
    - create new SSH session based on HTTP POST Request

    Args:
        request (request): request object of the http request

    Returns:
        JsonResponse: returns JSON object and HTTP status code
    """
    user = request.user
    if request.method == 'GET':
        sessions = SSHSession.objects.all()

        size = len(sessions)

        if size == 0:
            status_code = status.HTTP_404_NOT_FOUND
            message = 'no sessions are saved'
        else:
            status_code = status.HTTP_200_OK
            message = 'operation was successful'

        sessions_serializer = SSHSessionSerializer(sessions, many=True)

        return JsonResponse({
            "message": message,
            "count": size,
            "sessions": sessions_serializer.data
        }, status=status_code)

    elif request.method == 'POST':
        json_body = json.loads(request.body)
        session_serializer = SSHSessionSerializer(data=json_body)

        if session_serializer.is_valid():
            created_session = session_serializer.create(validated_data=session_serializer.validated_data)
            created_session.user = request.user
            created_session.save()

            return JsonResponse(
                {
                    'message': 'operation was successful',
                    'details': session_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return JsonResponse(
                {
                    'message': 'something went wrong',
                    'details': {}
                },
                status=status.HTTP_409_CONFLICT
            )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def details(request, id):
    """details [summary]

    - returns a specific SSH sessions on HTTP GET Request
    - creates a SSH session on HTTP PUT Request
    - updates a SSH session on HTTP PATCH Request
    - deletes a SSG session on HTTP DELETE Request

    Args:
        request (request): request object of the http request
        id (Integer): identifier of the SSH session 

    Returns:
        JsonResponse: returns JSON object and HTTP status code
    """

    # load details of a saved session
    if request.method == 'GET':

        try:
            session = SSHSession.objects.get(pk=id)
            session_serializer = SSHSessionSerializer(session)
            return JsonResponse({
                "message": "operation was successful",
                "details": session_serializer.data
            },
                status=status.HTTP_200_OK)
        except SSHSession.DoesNotExist:
            # Session doesn't not exist
            return JsonResponse(
                {
                    'message': 'session does not exist',
                    'details': {}
                },
                status=status.HTTP_404_NOT_FOUND
            )

    # create a new saved session
    elif request.method == 'PUT':
        # deserialize json
        json_body = json.loads(request.body)
        session_serializer = SSHSessionSerializer(data=json_body)

        if session_serializer.is_valid():
            new_instance = session_serializer.create(validated_data=session_serializer.validated_data)

            new_instance_serializer = SSHSessionSerializer(new_instance)

            return JsonResponse(
                {
                    'message': 'operation was successful',
                    'details': new_instance_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        else:
            print(session_serializer.errors)
            return JsonResponse(
                {
                    'message': 'something went wrong',
                    'details': {}
                },
                status=status.HTTP_409_CONFLICT
            )


        # request body in dictionary
        # {
        #     'title': 'Debian Buster Server',
        #     'hostname': 'example.org',
        #     'port': 22,
        #     'username': 'root',
        #     'description': 'explaining text',
        #     'password': 'iaspdgf'
        # }
        (request.data)

            # successfull (return of the saved session)

    # update a saved session
    elif request.method == 'PATCH':
        try:
            selected_session = SSHSession.objects.get(pk=id)
        except SSHSession.DoesNotExist:
            # Session doesn't not exist
            return JsonResponse(
                {
                    'message': 'specified session does not exist',
                    'details': {}
                },
                status=status.HTTP_404_NOT_FOUND
            )
        json_body = json.loads(request.body)
        session_serializer = SSHSessionSerializer(data=json_body)

        if session_serializer.is_valid():
            print(session_serializer.validated_data)
            updated_session_object = session_serializer.update(selected_session,
                                                               validated_data=session_serializer.validated_data)

            # TODO: check whether it is necessary to create a new serializer
            result_serializer = SSHSessionSerializer(updated_session_object)
            # need to add partial
            # successfull (return of the saved session)
            # the password should probably removed from the response
            return JsonResponse(
                {
                    "message": "operation was successful",
                    'details': result_serializer.data
                },
                status=status.HTTP_200_OK)
        else:
            print(session_serializer.errors)
            return JsonResponse(
                {
                    'message': 'something went wrong',
                    'details': {}
                },
                status=status.HTTP_409_CONFLICT
            )

    # delete a saved session
    elif request.method == 'DELETE':
        try:
            selected_session = SSHSession.objects.get(pk=id)
        except SSHSession.DoesNotExist:
            # Session doesn't not exist
            return JsonResponse(
                {
                    'message': 'session does not exist',
                    'details': {}
                },
                status=status.HTTP_404_NOT_FOUND)

        # delete session
        (amount, _) = selected_session.delete()

        if amount == 1:
            return JsonResponse(
                {
                    'message': 'deletion successful'
                },
                status=status.HTTP_200_OK)
        else:
            return JsonResponse(
                {
                    'message': 'deletion failed'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
