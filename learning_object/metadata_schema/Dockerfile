FROM python:3.6-alpine
RUN apk add --update alpine-sdk gettext
RUN apk add libffi-dev openssl-dev
ADD requirements.txt /
RUN pip install -r requirements.txt
ADD ./ /code
WORKDIR /code
RUN pip install -e marshmallowjson/
