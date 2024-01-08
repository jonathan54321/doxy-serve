FROM nginx:latest

RUN apt-get update
RUN apt-get -y install python3-venv python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install wheel gunicorn flask
EXPOSE 5000
EXPOSE 80
