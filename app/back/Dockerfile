FROM python:3.10
FROM sonarsource/sonar-scanner-cli:latest

WORKDIR /usr/app/back

RUN pip

COPY . /usr/app/back


#CMD [ "python", "./your-daemon-or-script.py" ]
RUN pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv --upgrade
RUN pipenv lock
RUN pipenv install --dev --deploy --system
RUN make setup

ENTRYPOINT ["sonar-scanner"]

EXPOSE 5000
EXPOSE 9000
