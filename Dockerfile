from ubuntu:20.04
# install dependencies for the project
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN apt-get update

RUN set -ex && \
    apt install -y \
        software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt install -y \
        python3.9 \
        python3.9-distutils \
        python3.9-venv && \
    python3.9 --version && \
    python3.9 -m ensurepip && \
    pip3.9 --version

RUN pip3.9 install --upgrade pip

# install the project dependencies in requirements.txt
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt
RUN pip3 install install --editable .
# copy the project files into the container
COPY . /app
WORKDIR /app

RUN peddy -h
CMD ["peddy"]
