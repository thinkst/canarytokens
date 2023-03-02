
FROM python:3.10.6@sha256:745efdfb7e4aac9a8422bd8c62d8bc35a693e8979a240d29677cb03e6aa91052
ARG COMMIT_SHA
ARG CANARYTOKENS_WHEEL_VERSION=canarytokens-0.3.0-py3-none-any.whl

RUN :\
    && apt update \
    && apt install -y osslsigncode \
    &&:

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VENV_PATH=/venv \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100


RUN echo $COMMIT_SHA >> /COMMIT_SHA

WORKDIR /

COPY requirements.txt .
COPY ${CANARYTOKENS_WHEEL_VERSION} /tmp

RUN :\
    && python -m venv /venv \
    && . /venv/bin/activate \
    && python -m pip install --no-deps -r requirements.txt --no-cache \
    && python -m pip install /tmp/${CANARYTOKENS_WHEEL_VERSION}[web,twisted] \
    &&:

COPY app.py .
COPY templates templates
#TODO: Package `root-ca.conf` with canarytokens module.
COPY root-ca.conf root-ca.conf
