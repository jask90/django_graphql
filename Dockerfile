FROM django_graphql_base
ARG DEBIAN_FRONTEND=noninteractive

# Set locale
ENV LANG es_ES.UTF-8  
ENV LANGUAGE es_ES.UTF-8
ENV LC_ALL es_ES.UTF-8    

# Copy the file from your host to your current location
COPY . /opt/django_graphql
WORKDIR /opt/django_graphql

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Inform Docker that the container is listening on the specified port at runtime.
EXPOSE 8000

RUN chmod +x /opt/django_graphql/entrypoint.sh

# Run the specified command within the container.
ENTRYPOINT ["/opt/django_graphql/entrypoint.sh"]
