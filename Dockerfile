FROM python:3.7-alpine

RUN adduser -D application

WORKDIR /home/application

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN python -m pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt

COPY app app
COPY migrations migrations
COPY application.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP application.py

RUN chown -R application:application ./
USER application

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]