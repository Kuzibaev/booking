## Getting started

1) install [poetry](https://python-poetry.org/docs/#installation) ```python -m pip install poetry```
2) clone project
3) enter project base directory `cd booking`
4) change `.env.dist` to `.env` and change environment variables to yours
5) install project `poetry install`
6) run `alembic upgrade head`
7) to start project run `python manage.py runserver`

### Management commands

```shell 
python manage.py <command> --help
```

- `runserver` - To run project

- `makemessages` - To extract messages

- `compilemessages` - To compile translated messages

- `createsuperuser` - To create superuser

### Generating Secret Key

```shell
openssl rand -hex 32
```

### Migration

Migration commands can be found in alembic directory

### Poetry commands

- To add a new package

```shell
poetry add package_name
```

- To remove a package

```shell
poetry remove package_name
```

### Migration commands

Migration commands can be found in `alembic` directory

### .env file

```dotenv
SECRET_KEY=
DB_USER=
DB_PASSWORD=
DB_NAME=
DB_HOST=
DB_PORT=
REDIS_URL=
ESKIZ_EMAIL=
ESKIZ_PASSWORD=
SITE_URL=
GOOGLE_CLIENT_ID=
GOOGLE_SECRET_KEY=
GOOGLE_WEBHOOK_OAUTH_REDIRECT_URI=
FACEBOOK_CLIENT_ID=
FACEBOOK_SECRET_KEY=
FACEBOOK_WEBHOOK_OAUTH_REDIRECT_URI=
ESKIZ_TOKEN=
MERCHANT_PASS=
```