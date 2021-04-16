from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
import os


@api_view(['GET', 'PATCH'])
def details(request):
    def request.method == 'GET':
        pass

    def request.method == 'PATCH':
        pass
