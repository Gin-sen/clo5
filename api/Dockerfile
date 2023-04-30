FROM python:3.11 as build
ARG SOURCEFOLDER=hotel
ENV ENV_SOURCEFOLDER=$SOURCEFOLDER

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./$SOURCEFOLDER /code/$SOURCEFOLDER

FROM build as test
RUN pip install --no-cache-dir --upgrade httpx requests pytest
CMD pytest


FROM build as final
RUN rm /code/**/test_*.py
# shell CMD pour injection de variable
CMD uvicorn ${ENV_SOURCEFOLDER}.main:app --host 0.0.0.0 --port 80