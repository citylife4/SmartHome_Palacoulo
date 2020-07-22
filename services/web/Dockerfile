FROM python:3.8-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && \
    apk add --no-cache openssl

RUN mkdir -p /usr/src/.ssh
RUN openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 \
                -keyout /usr/src/.ssh/key.pem -out /usr/src/.ssh/cert.pem \
                -subj "/C=UK/ST=Warwickshire/L=Leamington/O=OrgName/OU=IT Department/CN=example.com"

#pip if required
WORKDIR /usr/src/app

# copy project
COPY . /usr/src/app

CMD [ @ ]