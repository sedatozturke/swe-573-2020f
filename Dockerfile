FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT=8888

WORKDIR /code

COPY Pipfile Pipfile.lock /code/
RUN pip install pipenv && pipenv install --system

COPY . /code/

WORKDIR /code/pandemic_response_analyzer

RUN python /code/pandemic_response_analyzer/manage.py collectstatic --noinput

CMD gunicorn pandemic_response_analyzer.wsgi:application --bind 0.0.0.0:$PORT