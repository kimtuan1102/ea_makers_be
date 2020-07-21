FROM ubuntu:18.04

#ARG ARG_BRANCH
#ARG ARG_VERSION
#ARG ARG_TAG
#ARG ARG_ENV
#ARG ARG_BUILD_DATE
#
#ENV DEBIAN_FRONTEND=noninteractive \
#    LC_ALL=C.UTF-8 \
#    LANG=C.UTF-8

### Install apt packages and Set UTC
RUN apt-get update && apt-get install -y software-properties-common debconf-utils build-essential python3 python3-dev python3-pip supervisor nginx libmysqlclient-dev gettext libssl-dev

# Set alias for 'supervisorctl'
RUN echo "alias s='supervisorctl'" >> ~/.bashrc

WORKDIR /app/source

### COPY dirs and files to run collectstatic
COPY ./ea_makers_be ./
RUN pip3 install pip --upgrade && pip install -r requirements.txt
RUN python3 scripts/manage.py collectstatic --no-input && mv static-root/ /var/www/html/static/

### Run collectstatic and move generated dirs, files

### COPY other dirs and files
COPY ea-makers.conf /etc/nginx/conf.d/
COPY supervisor.conf /etc/supervisor/conf.d/supervisor.conf

#RUN echo "${ARG_VERSION}" >> ./VERSION

# Run supervisord in the foreground
CMD ["/usr/bin/supervisord", "-n"]