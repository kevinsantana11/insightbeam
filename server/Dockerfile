FROM python:3.10-bullseye

ADD requirements.txt /tmp
RUN ["pip", "install", "-r", "/tmp/requirements.txt"]

RUN ["useradd", "-r", "insightbeam-runner"]
WORKDIR /home/insightbeam-runner/service

COPY --chown=insightbeam-runner insightbeam insightbeam

COPY .env .env

COPY --chown=insightbeam-runner data/server data
EXPOSE 8000

USER insightbeam-runner
CMD ["python3", "-m", "insightbeam"]
