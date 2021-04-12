from django.shortcuts import render

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view


@api_view(['GET'])
def all(request):

    # load all session
    if request.method == 'GET':

        is_empty = False

        if is_empty:
            # no saved sessions
            return JsonResponse(
                {
                    'message': 'no sessions are saved',
                    'count': 0,
                    'sessions': []
                },
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            # successfull
            return JsonResponse(
                {
                    'message': 'operation was successful',
                    'count': 2,
                    'sessions': [
                        {
                            'id': 0,
                            'title': 'Debian Buster Server',
                            'hostname': 'example.org',
                            'port': 22,
                            'username': 'root',
                            'description': 'explaining text'
                        },
                        {
                            'id': 1,
                            'title': 'Raspberry Pi',
                            'hostname': '10.34.173.123',
                            'port': 69,
                            'username': 'pi',
                            'description': 'I like raspberries'
                        }
                    ]
                },
                status=status.HTTP_200_OK
            )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def details(request, id):

    # load details of a saved session
    if request.method == 'GET':

        exists = True

        if not exists:
            # session does not exist
            return JsonResponse(
                {
                    'message': 'session does not exist',
                    'details': {}
                },
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            # successfull
            return JsonResponse(
                {
                    'message': 'operation was successful',
                    'details': {
                        'id': 0,
                        'title': 'Debian Buster Server',
                        'hostname': 'example.org',
                        'port': 22,
                        'username': 'root',
                        'description': 'explaining text'
                    }
                },
                status=status.HTTP_200_OK
            )

    # create a new saved session
    elif request.method == 'PUT':

        # request body in dictionary
        # {
        #     'title': 'Debian Buster Server',
        #     'hostname': 'example.org',
        #     'port': 22,
        #     'username': 'root',
        #     'description': 'explaining text',
        #     'password': 'iaspdgf'
        # }
        print(request.data)

        successful = True

        if not successful:
            # something went wrong
            return JsonResponse(
                {
                    'message': 'something went wrong',
                    'details': {}
                },
                status=status.HTTP_409_CONFLICT
            )
        else:
            # successfull (return of the saved session)
            return JsonResponse(
                {
                    'message': 'operation was successful',
                    'details': {
                        'id': 0,
                        'title': 'Debian Buster Server',
                        'hostname': 'example.org',
                        'port': 22,
                        'username': 'root',
                        'description': 'explaining text'
                    }
                },
                status=status.HTTP_201_CREATED
            )

    # update a saved session
    elif request.method == 'PATCH':

        # request body in dictionary
        # {
        #     'title': 'Debian Buster Server',
        #     'hostname': 'example.org',
        #     'port': 22,
        #     'username': 'root',
        #     'description': 'explaining text',
        #     'password': 'iaspdgf'
        # }
        print(request.data)

        successful = True

        if not successful:
            # something went wrong
            return JsonResponse(
                {
                    'message': 'something went wrong',
                    'details': {}
                },
                status=status.HTTP_409_CONFLICT
            )
        else:
            # successfull (return of the saved session)
            return JsonResponse(
                {
                    'message': 'operation was successful',
                    'details': {
                        'id': 0,
                        'title': 'Debian Buster Server',
                        'hostname': 'example.org',
                        'port': 22,
                        'username': 'root',
                        'description': 'explaining text'
                    }
                },
                status=status.HTTP_200_OK
            )

    # delete a saved session
    elif request.method == 'DELETE':

        exists = True

        if not exists:
            # session does not exist
            return JsonResponse(
                {
                    'message': 'session does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        deleted_successful = True

        if not deleted_successful:
            return JsonResponse(
                {
                    'message': 'deletion failed'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        else:
            return JsonResponse(
                {
                    'message': 'deletion successful'
                },
                status=status.HTTP_200_OK
            )
