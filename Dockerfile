# pull the official base image
FROM python:3.8-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN python -m pip install --upgrade pip 
COPY ./requirements.txt /usr/src/app
RUN python -m pip install -r requirements.txt
RUN python -m pip install daphne

# copy project
COPY . /usr/src/app

# make startup script executable
RUN chmod +x start_docker.sh

EXPOSE 80

CMD ["./start_docker.sh"]