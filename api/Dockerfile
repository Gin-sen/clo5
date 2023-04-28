FROM python:3.9
ARG SOURCEFOLDER

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./$SOURCEFOLDER /code/$SOURCEFOLDER

WORKDIR /code/$SOURCEFOLDER

CMD ["uvicorn", "main:app ", "--host", "0.0.0.0", "--port", "80"]