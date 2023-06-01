FROM python:3.11 as build

WORKDIR /code

COPY ./requirements.txt /code/hotel/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/hotel/requirements.txt

COPY . /code/hotel

FROM build as test
WORKDIR /code
RUN pip install --no-cache-dir --upgrade httpx requests pytest pysqlite3-binary
CMD pytest


FROM build as final
RUN rm -r /code/hotel/test*
WORKDIR /code
# shell CMD pour injection de variable
CMD uvicorn hotel.main:app --host 0.0.0.0 --port 80