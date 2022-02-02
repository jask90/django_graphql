# Django GraphQL

To build the project in a closed environment you only need to have docker installed on your computer.

When you have the cloned repository and you are in the root of the project, create the docker containers:
> docker-compose -f docker-compose.yml up

This will create the images and raise the corresponding containers, if we want to enter in the main container we can execute the following command:
> docker exec -ti django_graphql_web bash

# Execute tests

Once inside the container we can launch the unit tests with the following command:
> python3 /opt/django_graphql/django_graphql/manage.py test user

> python3 /opt/django_graphql/django_graphql/manage.py test social

This executes the tests located in user and social apps.

# Other details

The web will run at http://localhost:8000/

When you create the containers, a series of fixtures will be automatically loaded with the minimum data of users, Ideas and Follows. This is a minimum information to be able to test all the features of the project as soon as possible.

Fixture user data:
* admin / 123456
* api_user / EJH2y8dBMCvfVq2W
* dani / aTzQrDP84D
* dani2 / aTzQrDP84D
* dani3 / aTzQrDP84D
* dani4 / aTzQrDP84D
* dani5 / aTzQrDP84D
* dani6 / aTzQrDP84D

In the root of the project you can find a file called 'GraphQL.postman_collection.json', this is a json that you can import in Postman to test all the features with JWT.
