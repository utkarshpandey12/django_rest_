# distribution_plan

## Local Development

### Install Pre-commit git hook -- Mandatory*
      $ git init
      $ pre-commit install

### Build Stack

- To Build Django & Postgress docker images:

      $ docker-compose -f local.yml build

### Run the Stack

- To Build Django & Postgress docker images:

      $ docker-compose -f local.yml up

### Running Migrations

- To run **makemigrations**, use this command:

      $ docker-compose -f local.yml run --rm django python manage.py makemigrations

- To run **migrate**, use this command:

      $ docker-compose -f local.yml run --rm django python manage.py migrate

### Setting Up Your Users

- To create an **superuser account**, use this command:

      $ docker-compose -f local.yml run --rm django python manage.py createsuperuser


### Service Links & Ports

- Django Admin Page Available on:

      http://127.0.0.1:8000/admin/

- API Documentation:

      http://127.0.0.1:8000/api/docs

- Celery Flower:

      http://127.0.0.1:5555
      Username & Password -> .envs/local/django


### Folder Structure

- Detail Folder Structure:

        .
        └── mbx_be_auth/
            ├── .envs
            ├── core - (core app - all apis lives here)/
            │   ├── urls.py
            │   ├── task.py
            │   ├── models.py
            │   ├── utils.py
            │   └── views.py
            ├── mbx_be_auth
            ├── compose
            ├── configs/
            │   ├── settings/
            │   │   ├── base.py -> base settings
            │   │   ├── local.py -> settings applicable only for development
            │   │   └── production.py
            │   └── urls.py -> starting point
            ├── requirements
            ├── local.yml
            └── manage.py
