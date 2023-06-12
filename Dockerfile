#FROM python:3.9.5-slim-buster
#
#WORKDIR /opt
#
#ENV TERM xterm
#ENV DEBIAN_FRONTEND noninteractive
#
#RUN apt-get update --fix-missing -qq && apt-get install -qqy postgresql-client \
#    git \
#    gdal-bin \
#    libgdal-dev \
#    python3-gdal
#
#RUN mkdir -p /root/.ssh
#ADD assets/private_key /root/.ssh/id_rsa
#
#RUN chmod 600 /root/.ssh/id_rsa \
#    && eval "$(ssh-agent -s)" \
#    && ssh-add /root/.ssh/id_rsa \
#    && ssh-keyscan -p 8822 git.picopac.ir >> ~/.ssh/known_hosts
#
#ADD assets/requirements.txt /opt/requirements.txt
#RUN pip install -r requirements.txt
#RUN rm /opt/requirements.txt
#RUN rm /root/.ssh/id_rsa
#
#ADD assets/entrypoint.sh /opt/entrypoint.sh
#ADD project /opt/project
#
#ENTRYPOINT [ "/bin/sh", "/opt/entrypoint.sh" ]