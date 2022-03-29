# Берем нужный базовый образ
FROM python:3.8-alpine

RUN apk update && apk add --virtual build-deps gcc python3-dev musl-dev && apk add postgresql-dev && apk add bind-tools
# Копируем все файлы из текущей директории в /app контейнера
COPY . ./app
# Устанавливаем все зависимости
RUN apk update  && pip install -r /app/requirements.txt --no-cache-dir
# Устанавливаем приложение (Подробнее смотри Distutils)
#RUN pip install -e /app
CMD python /app/source/manage.py makemigrations
CMD python /app/source/manage.py migrate
CMD python /app/source/objects.py
# Говорим контейнеру какой порт слушай
EXPOSE 8080
# Запуск нашего приложения при старте контейнера
# CMD web_server

# В качестве альтернативы distutils можно просто указать что выполнить
#CMD python /app/src/app.py