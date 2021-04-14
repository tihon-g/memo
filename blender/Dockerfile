#FROM ikester/blender-docker
#LABEL author: tihon
#
#WORKDIR /usr/local/blender/python/bin
#
#COPY ./requirements.txt ./
#
#
#RUN apt-get update \
#    && ./python3.7m -m ensurepip \
#    && ./pip3 install --upgrade pip \
#    && ./pip3 install -r requirements.txt


FROM ubuntu:focal

LABEL authors="tihon"

RUN apt-get update \
    && apt-get install -y \
		curl \
		libfreetype6 \
		libglu1-mesa \
		libxi6 \
		libxrender1 \
#		gcc \
#		python3-dev \
		xz-utils \
    && apt-get -y autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY . ./usr/local

ENV BLENDER_MAJOR 2.82
ENV BLENDER_VERSION 2.82a
ENV BLENDER /usr/local/blender/blender
ENV DJANGO_BASE_DIR /usr/local/rendering
ENV BLENDER_PY ./usr/local/blender.py
ENV QUALITY 1

ENV BLENDER_ARCH blender-${BLENDER_VERSION}-linux64
ENV BLENDER_URL https://download.blender.org/release/Blender${BLENDER_MAJOR}/${BLENDER_ARCH}.tar.xz
ENV PIP /usr/local/blender/${BLENDER_MAJOR}/python/bin/pip3
ENV PYTHON /usr/local/blender/${BLENDER_MAJOR}/python/bin/python3.7m

ENV RABBIT_USER django
ENV RABBIT_PASSWORD memo
ENV RABBIT_HOST 127.0.0.1
ENV RABBIT_PORT 5672
ENV RABBIT_VIRTUALHOST default
ENV RABBIT_QUEUE orders


RUN curl -L ${BLENDER_URL} | tar -xJ -C /usr/local/ \
	&& mv /usr/local/${BLENDER_ARCH} /usr/local/blender \
	# todo rm archive file
    && ${PYTHON} -m ensurepip \
    && ${PIP} install --upgrade pip \
    && ${PIP} install -r /usr/local/requirements.txt
    #&& ${PYTHON} rabbit_queue.py

#WORKDIR /usr/local/blender/python/bin

#WORKDIR /media
#VOLUME /media

# WORKDIR /usr/local
WORKDIR DJANGO_BASE_DIR

CMD ${PYTHON} /usr/local/queue.py
#COPY . /usr/local/
#CMD ["/usr/local/blender/${BLENDER_MAJOR}/python/bin/python3.7m", "/usr/local/rabbit_queue.py"]
#ENTRYPOINT ["/usr/local/blender/blender", "-b", "-noaudio"]

# /usr/local/blender/${BLENDER_MAJOR}/python/bin/python3.7m /usr/local/rabbit_queue.py