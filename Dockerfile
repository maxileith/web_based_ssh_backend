# pull the official base image
FROM python:3.8.8-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
# don't create __pycache__/* files
ENV PYTHONDONTWRITEBYTECODE 1
# output straight to terminal
ENV PYTHONUNBUFFERED 1

# install dependencies for bcrypt, PyNaCl, cryptography
RUN apk add --update musl-dev gcc libffi-dev make cargo libressl-dev

# install dependencies
RUN python -m pip install --upgrade pip 
COPY ./requirements.txt /usr/src/app
RUN python -m pip install -r requirements.txt

# copy project
COPY . /usr/src/app

# make startup script executable
RUN chmod +x start_docker.sh

EXPOSE 80

CMD ["./start_docker.sh"]