#!/bin/sh

sleep 10

if test ! -f /opt/django_graphql/.first.txt;
then
    touch /opt/django_graphql/.first.txt;

    /usr/bin/pip3 install -r /opt/django_graphql/requirements.txt

    rm -rf /opt/django_graphql/django_graphql/migrations
    python3 /opt/django_graphql/django_graphql/manage.py collectstatic --no-input
    python3 /opt/django_graphql/django_graphql/manage.py flush --no-input
    python3 /opt/django_graphql/django_graphql/manage.py makemigrations
    python3 /opt/django_graphql/django_graphql/manage.py migrate
    python3 /opt/django_graphql/django_graphql/manage.py makemigrations user
    python3 /opt/django_graphql/django_graphql/manage.py migrate user
    python3 /opt/django_graphql/django_graphql/manage.py makemigrations social
    python3 /opt/django_graphql/django_graphql/manage.py migrate social

    python3 /opt/django_graphql/django_graphql/manage.py loaddata /opt/django_graphql/django_graphql/user/fixtures/users.json
    python3 /opt/django_graphql/django_graphql/manage.py loaddata /opt/django_graphql/django_graphql/social/fixtures/idea.json
    python3 /opt/django_graphql/django_graphql/manage.py loaddata /opt/django_graphql/django_graphql/social/fixtures/follow.json

else
    /usr/bin/pip3 install -r /opt/django_graphql/requirements.txt
    python3 /opt/django_graphql/django_graphql/manage.py collectstatic --no-input
fi

exec "$@"
