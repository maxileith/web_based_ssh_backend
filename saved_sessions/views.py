from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view

from .models import SSHSession
from .serializers import SSHSessionSerializer, RedactedSSHSessionSerializer
import json

from ssh.ssh_client import is_private_host


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
            message = 'No sessions are saved.'
        else:
            status_code = status.HTTP_200_OK
            message = 'Session were returned successfully.'

        sessions_serializer = RedactedSSHSessionSerializer(sessions, many=True)

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

        session_serializer = SSHSessionSerializer(
            data=body, context={'user': request.user})

        if session_serializer.is_valid():

            if is_private_host(body['hostname']):
                return JsonResponse(
                    {
                        'message': 'Private Hosts are not allowed.',
                        'details': {}
                    },
                    status=status.HTTP_409_CONFLICT
                )

            saved_session = session_serializer.save()

            result_serializer = RedactedSSHSessionSerializer(saved_session)

            return JsonResponse(
                {
                    'message': 'Session added successfully.',
                    'details': result_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return JsonResponse(
                {
                    'message': 'Something went wrong.',
                    'details': {}
                },
                status=status.HTTP_409_CONFLICT
            )


@api_view(['GET', 'PATCH', 'DELETE'])
@login_required(redirect_field_name=None)
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
                    'message': 'Session does not exist.',
                    'details': {}
                },
                status=status.HTTP_404_NOT_FOUND
            )

        session_serializer = RedactedSSHSessionSerializer(session)

        return JsonResponse({
            "message": "Session details returned successfully.",
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
                    'message': 'Specified session does not exist.',
                    'details': {}
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            json_body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {
                    'message': 'Something went wrong.',
                    'details': {}
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        session_serializer = SSHSessionSerializer(data=json_body, partial=True)

        if session_serializer.is_valid():

            try:
                if is_private_host(json_body['hostname']):
                    return JsonResponse(
                        {
                            'message': 'Private Hosts are not allowed.',
                            'details': {}
                        },
                        status=status.HTTP_409_CONFLICT
                    )
            except KeyError:
                pass

            updated_session_object = session_serializer.update(selected_session,
                                                               validated_data=session_serializer.validated_data)

            result_serializer = RedactedSSHSessionSerializer(
                updated_session_object)

            return JsonResponse(
                {
                    "message": "Session updated successfully.",
                    'details': result_serializer.data
                },
                status=status.HTTP_200_OK)
        else:
            return JsonResponse(
                {
                    'message': 'Something went wrong.',
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
                    'message': 'Session does not exist.',
                    'details': {}
                },
                status=status.HTTP_404_NOT_FOUND)

        # delete session
        (amount, _) = selected_session.delete()

        if amount == 1:
            return JsonResponse(
                {
                    'message': 'Deletion successful.'
                },
                status=status.HTTP_200_OK)
        else:
            return JsonResponse(
                {
                    'message': 'Deletion failed.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(["POST", "DELETE"])
@login_required(redirect_field_name=None)
def ssh_key(request, session_id):
    session = SSHSession.objects.filter(
        pk=session_id, user=request.user).first()

    if request.method == 'POST':

        if not session:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        if 'key_file' not in request.FILES:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['key_file']

        if session.key_file:
            session.key_file.delete()

        session.key_file = file
        session.save()

        return HttpResponse(status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'DELETE':
        if session.key_file:
            session.key_file.delete()
        else:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
