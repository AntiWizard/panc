FROM python:3.9.5-slim-buster


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client openssh-client \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /root/.ssh \
 && mkdir -p /var/services/panc/vault \
 && mkdir -p /var/services/panc/static \
 && ssh-keygen -t rsa -b 4096 -m pem -f /var/services/panc/vault/id_rsa \
 && chmod 600 -R /var/services/panc/

WORKDIR /opt

ADD assets/requirements.txt /opt/requirements.txt

RUN pip install -r requirements.txt
RUN rm /opt/requirements.txt

ADD assets/entrypoint.sh /opt/entrypoint.sh
ADD project /opt/project

RUN chmod +x /opt/entrypoint.sh

ENTRYPOINT ["/opt/entrypoint.sh" ]