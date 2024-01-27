FROM python:3.10

WORKDIR /usr/app/back

RUN pip

COPY . /usr/app/back

RUN pip install pipenv

COPY requirements.txt ./

EXPOSE 5050