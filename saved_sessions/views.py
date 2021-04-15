from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from .models import SSHSession
from .serializers import SSHSessionSerializer
import json


@api_view(['GET', 'POST'])
@login_required(redirect_field_name=None)
@csrf_exempt
def sessions(request):
    """sessions [summary]

    - returns all SSH sessions saved for the user on HTTP GET Request
    - create new SSH session based on HTTP POST Request

    Args:
        request (Request): request object of the http request

    Returns:
        JsonResponse: returns JSON object and HTTP status code
    """
    if request.method == 'GET':
        sessions = SSHSession.objects.filter(user=request.user)

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
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        print(body)

        session_serializer = SSHSessionSerializer(
            data=body, context={'user': request.user})

        print(session_serializer.error_messages)

        if session_serializer.is_valid():
            session_serializer.save()

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


@api_view(['GET', 'PATCH', 'DELETE'])
def details(request, id):
    """details [summary]

    - returns a specific SSH sessions on HTTP GET Request
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
        session = SSHSession.objects.filter(pk=id, user=request.user).first()

        if not session:
            # Session doesn't not exist
            return JsonResponse(
                {
                    'message': 'session does not exist',
                    'details': {}
                },
                status=status.HTTP_404_NOT_FOUND
            )

        session_serializer = SSHSessionSerializer(session)
        return JsonResponse({
            "message": "operation was successful",
            "details": session_serializer.data
        }, status=status.HTTP_200_OK)

    # update a saved session
    elif request.method == 'PATCH':
        selected_session = SSHSession.objects.filter(
            pk=id, user=request.user).first()

        if not selected_session:
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
            return JsonResponse(
                {
                    'message': 'something went wrong',
                    'details': {}
                },
                status=status.HTTP_409_CONFLICT
            )

    # delete a saved session
    elif request.method == 'DELETE':
        selected_session = SSHSession.objects.filter(
            pk=id, user=request.user).first()

        # Session doesn't not exist
        if not selected_session:
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
