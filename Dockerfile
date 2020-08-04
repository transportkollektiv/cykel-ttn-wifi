FROM python:3.7-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV TTN_APP_ID ""
ENV TTN_ACCESS_KEY ""
ENV ENDPOINT "http://cykel/api/bike/updatelocation"
ENV ENDPOINT_AUTH_HEADER ""
ENV MOZLOC_KEY ""

WORKDIR /code

COPY requirements.txt /code/

RUN set -eux \
    # build-base is required to build grpcio, libstdc++ while running
    && apk add --no-cache libstdc++ \
    && apk add --no-cache --virtual .build-deps build-base \
    && apk add --no-cache --virtual .build-deps build-base linux-headers \
    && pip install -r requirements.txt \
    # Remove build dependencies to reduce layer size
    && apk del .build-deps

COPY . /code/

EXPOSE 8080
CMD ["python", "app.py"]
