FROM node:20 AS front-build

COPY ./frontend /app
WORKDIR /app
RUN npm install && npm run build

FROM python:3.9

LABEL author="dmitriyvasil@gmail.com"

ENV DJANGO_SETTINGS_MODULE=expense_counter.settings
ENV DB_PASSWORD=root
ENV DB_NAME=expenses
ENV DB_USER=root
ENV DB_PORT=5432
ENV DEBUG=False
ENV DB_HOST=db

COPY ./backend /app
COPY --from=front-build /app/dist /app/static/js

RUN python -m pip install --upgrade pip
RUN python -m pip install -r /app/requirements.txt

CMD cd /app && python runserver.py