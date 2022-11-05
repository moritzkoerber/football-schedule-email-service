# Build lambda runtime interface client
ARG FUNCTION_DIR="/function"
FROM python:3.9-bullseye as build-image

RUN apt-get update \
    && apt-get install -y -f --no-install-recommends unzip=6.0-26+deb11u1 \
    g++ \
    make \
    cmake \
    libcurl4-openssl-dev

ARG FUNCTION_DIR
RUN mkdir -p ${FUNCTION_DIR}
COPY src/* ${FUNCTION_DIR}

RUN pip install --no-cache-dir --target ${FUNCTION_DIR} awslambdaric==2.0.2

# Build lambda function
FROM python:3.9-bullseye

ARG DEBIAN_FRONTEND=noninteractive
ARG FUNCTION_DIR
WORKDIR ${FUNCTION_DIR}

COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

RUN apt-get update \
    && apt-get install -y -f --no-install-recommends unzip=6.0-26+deb11u1 \
    wget=1.21-1+deb11u1 \
    libnss3-dev=2:3.61-1+deb11u2 \
    libdbus-glib-1-2=0.110-6 \
    libx11-xcb1=2:1.7.2-1 \
    packagekit-gtk3-module=1.2.2-2 \
    libasound2=1.2.4-1.1 \
    libxtst-dev=2:1.2.3-1 \
    libgtk-3-0=3.24.24-4+deb11u2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN wget --progress=dot:giga https://ftp.mozilla.org/pub/firefox/releases/99.0/linux-x86_64/en-US/firefox-99.0.tar.bz2 -P ~/ \
    && tar jxvf ~/firefox-99.0.tar.bz2 -C /opt \
    && ln -s /opt/firefox/firefox /usr/local/bin/firefox

RUN wget --progress=dot:giga https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz -P ~/ \
    && tar zxvf ~/geckodriver-v0.31.0-linux64.tar.gz -C /opt \
    && ln -s /opt/geckodriver /usr/local/bin/geckodriver

RUN pip install --no-cache-dir --target ${FUNCTION_DIR} selenium==4.5.0 boto3==1.21.46 pandas==1.4.2

ENV HOME=/tmp

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "handler.handler" ]
