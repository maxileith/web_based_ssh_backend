# pull the official base image
FROM python:3.8-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt update
RUN apt install gcc -y

RUN pip install --upgrade pip 
COPY ./requirements.txt /usr/src/app
RUN pip install -r requirements.txt
RUN pip install uwsgi==2.0.19

# copy project
COPY . /usr/src/app

# make startup script executable
RUN chmod +x start_docker.sh

EXPOSE 80

CMD ["./start_docker.sh"]