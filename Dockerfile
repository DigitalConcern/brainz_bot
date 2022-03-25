

FROM postgres:10.0-alpine

USER postgres

RUN chmod 0700 /var/lib/postgresql/data &&\
    initdb /var/lib/postgresql/data &&\
    echo "host all  all    0.0.0.0/0  md5" >> /var/lib/postgresql/data/pg_hba.conf &&\
    echo "listen_addresses='*'" >> /var/lib/postgresql/data/postgresql.conf &&\
    pg_ctl start &&\
    psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'main'" | grep -q 1 || psql -U postgres -c "CREATE DATABASE main" &&\
    psql -c "ALTER USER postgres WITH ENCRYPTED PASSWORD 'mysecurepassword';"

EXPOSE 5432


# Берем нужный базовый образ
FROM python:3.8-alpine
RUN apk add python-dev
RUN apk update && apk add --virtual build-deps gcc python-dev musl-dev && apk add postgresql-dev
# Копируем все файлы из текущей директории в /app контейнера
COPY . ./app
# Устанавливаем все зависимости
RUN apk update  && pip install -r /app/requirements.txt --no-cache-dir
# Устанавливаем приложение (Подробнее смотри Distutils)
RUN pip install -e /app
# Говорим контейнеру какой порт слушай
EXPOSE 8080
# Запуск нашего приложения при старте контейнера
CMD web_server

# В качестве альтернативы distutils можно просто указать что выполнить
#CMD python /app/src/app.py