FROM python:3.9-slim
LABEL Memo rendering image

#RUN apt-get update \
#    && apt-get install -y --no-install-recommends postgresql-client
#    && apt-get install -y gcc python3-dev \
#    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/local/rendering
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt

# install dependencies
RUN pip install --upgrade pip \
    && pip install -qr /tmp/requirements.txt

# copy project
#COPY . .

#EXPOSE 8000
#ENTRYPOINT ["python", "./app/my_script.py", "my_var"]
# Инструкция ENTRYPOINT позволяет задавать команду с аргументами, которая должна выполняться при запуске контейнера. Она похожа на команду CMD,
# но параметры, задаваемые в ENTRYPOINT, не перезаписываются в том случае, если контейнер запускают с параметрами командной строки.
# Например, после выполнения команды вида docker run my_image bash аргумент bash добавится в конец списка аргументов, заданных с помощью ENTRYPOINT
#CMD gunicorn --bind 0.0.0.0:8000 --workers 3 rendering.wsgi

EXPOSE 8000
EXPOSE 80 443
#EXPOSE 53/tcp 53/udp

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
#VOLUME /usr/local/renders
