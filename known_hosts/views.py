from django.shortcuts import render

from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
import json


@api_view(['GET', 'PATCH'])
def fileaccess(request):
    if request.method == 'GET':
        pass

    elif request.method == 'PUT':
        pass
