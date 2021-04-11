from django.shortcuts import render


def index(request, ssh_session):
    return render(request, 'ssh/index.html', {
        'ssh_session': ssh_session
    })
