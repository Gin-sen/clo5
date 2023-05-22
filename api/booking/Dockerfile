FROM python:3.11 as build
WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/booking/requirements.txt

COPY . /code/booking

FROM build as test
RUN pip install --no-cache-dir --upgrade httpx requests pytest pysqlite3-binary
CMD pytest


FROM build as final
RUN rm -r /code/**/tests
WORKDIR /code/booking
# shell CMD pour injection de variable
CMD uvicorn main:app --host 0.0.0.0 --port 80