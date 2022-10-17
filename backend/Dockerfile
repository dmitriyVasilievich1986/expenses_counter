FROM python:3.9

LABEL author="dmitriyvasil@gmail.com"

ENV DB_PASSWORD=root
ENV DB_NAME=expenses
ENV DB_USER=root
ENV DB_PORT=5432
ENV DEBUG=False
ENV DB_HOST=db

WORKDIR /app
COPY . /app

RUN python -m pip install -r /app/requirements.txt

CMD python runserver.py