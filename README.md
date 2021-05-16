# Webssh Backend

This is a backend for an application that provides users with an SSH client in the browser.

## Before you start

-   Copy `.env.example` to `.env` and change the attributes to fit your needs.
-   Create the file `db.sqlite3` by running the command `touch db.sqlite3`.

## Development version

### Installation

```
pip install -r requirements.txt
```

Installs dependencies.

### Start the server

Make sure that `start.sh` is executable by running `chmod +x start.sh`

```
./start.sh
```

Runs the app in the development mode.\
It can be accessed via [http://localhost:8000](http://localhost:8000).

The server will reload if you make edits.

## Production Version

The production version is rolled out using Docker.

### Installation

```
docker-compose build
```

Creates a container based on Alpine Linux and Python \
to host the production version of the application.

### Start

```
docker-compose up -d
```

Starts the Docker stack in detached mode.

By default the stack listens to port 8000 bound localhost. \
The stack was designed to be used behind the reverse proxy [Traefik](https://github.com/traefik/traefik).
