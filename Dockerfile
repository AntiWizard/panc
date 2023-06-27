FROM python:3.9.5-slim-buster


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt

RUN mkdir -p /root/.ssh
ADD assets/private_key /root/.ssh/id_rsa

RUN chmod 600 /root/.ssh/id_rsa

ADD assets/requirements.txt /opt/requirements.txt

RUN pip install -r requirements.txt
RUN rm /opt/requirements.txt

ADD assets/entrypoint.sh /opt/entrypoint.sh
ADD project /opt/project

ENTRYPOINT [ "/bin/sh", "/opt/entrypoint.sh" ]