from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import json
from django.contrib.auth.models import User

# Create your views here.
from auth.serializers import UserSerializer
import jwt


def login(request):
    if request.method == "POST":
        content = json.loads(request.body)
        username = content["username"]
        password = content["password"]

        user = authenticate(username=username, password=password)

        if user is not None:
            payload = {
                "username": username,
            }
            #  {expiresIn: "4hr"}
            token = jwt.encode(payload, "ha", algorithm="HS256", headers={"expiresIn": "4hr"})
            return HttpResponse(json.dumps({
                "token": token
            }))
        else:
            return HttpResponse(status=403)


def register(request):
    if request.method == "POST":
        content = json.loads(request.body)

        username = content["username"]
        password = content["password"]
        email = content["email"]
        first_name = content["first_name"]
        last_name = content["last_name"]

        # TODO: clean input

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username, email, password)
            user.last_name = last_name
            user.first_name = first_name
            user.save()

            serializer = UserSerializer(user)
            return JsonResponse(serializer.data)

    return HttpResponse(status=403)
