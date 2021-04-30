from django.core.mail import send_mail
from django.template import loader
from django.utils.html import strip_tags
from web_based_ssh_backend.settings import URL_BACKEND


def send_verify_mail(adress, token):

    html_message = loader.render_to_string(
        'app_auth/verify.html',
        {
            'url': f'http://{URL_BACKEND}/auth/email/verify/{token}'
        }
    )

    send_mail(
        'Web SSH verification email',
        strip_tags(html_message),
        'webssh@leith.de',
        [adress],
        html_message=html_message
    )
