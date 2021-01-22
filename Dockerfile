FROM python:3.6-slim-buster
RUN apt-get update
RUN apt-get install -y bc
RUN apt-get install -y imagemagick
RUN apt-get install -y libspatialindex-dev

RUN apt-get install -y gcc
ENV MAGICK_THREAD_LIMIT 1

RUN apt-get install -y python3-numpy 

COPY requirements.txt /
RUN pip3 install -r requirements.txt

COPY requirementindocker.txt /
RUN pip3 install -r requirementindocker.txt

COPY policy.xml /etc/ImageMagick-6/

ENV ENV_CONFIG "/app/config.ini"

EXPOSE 80
COPY . /app
WORKDIR /app
