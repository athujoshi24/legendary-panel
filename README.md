# Recipe App using Django

## About this app

- This application is developed using Django and DjangoRestFramework.
- We have used out of the box authentication functionality offer by Django (Token authentication and Basic Authentication).

## Quickstart guide

### Setup the application in your System

Before starting with the following steps, install [python 3](https://www.python.org/ftp/python/3.8.5/python-3.8.5.exe) on your system.

1. RUN "pip install -r requirements.txt"
2. Clone/Download this repository
3. RUN "python manage.py makemigrations".
4. RUN "python manage.py migrate".
5. RUN "python manage.py runserver 0.0.0.0:8000".
    - This will start the application or server on your machine on port "8000", you can then access the app on "http://localhost:8000/"
6. Create the user by clicking on following link: "http://localhost:8000/api/user/create/"
7. Create Tags for recipes by going to following link "http://localhost:8000/api/recipe/tags/".
    - Login using your credentials when prompted to do so.
8. Create Ingredients for recipes by going to following link: "http://localhost:8000/api/recipe/ingredient/"
9. No visit "http://localhost:8000/api/recipe/recipe/" to create recipes

## API Documentation

You can find API documentation [here](http://localhost:8000/).
