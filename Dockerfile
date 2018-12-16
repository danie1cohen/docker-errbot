#      ___           ___           ___
#     /  /\         /  /\         /  /\
#    /  /:/_       /  /::\       /  /::\
#   /  /:/ /\     /  /:/\:\     /  /:/\:\
#  /  /:/ /:/_   /  /:/~/:/    /  /:/~/:/
# /__/:/ /:/ /\ /__/:/ /:/___ /__/:/ /:/___
# \  \:\/:/ /:/ \  \:\/:::::/ \  \:\/:::::/
#  \  \::/ /:/   \  \::/~~~~   \  \::/~~~~
#   \  \:\/:/     \  \:\        \  \:\
#    \  \::/       \  \:\        \  \:\
#     \__\/         \__\/         \__\/
#
FROM resin/rpi-raspbian:latest

RUN apt-get -q update && apt-get -qy install \
  build-essential \
  libffi-dev \
  libssl-dev \
  curl

RUN curl -o /tmp/Python-3.6.0.tar.xz https://www.python.org/ftp/python/3.6.0/Python-3.6.0.tar.xz && \
  cd /tmp && \
  tar xvf Python-3.6.0.tar.xz && \
  cd Python-3.6.0/ && \
  ./configure && \
  make install

RUN python3 --version
RUN ln -s $(which python3) /usr/local/bin/python
RUN ln -s $(which pip3) /usr/local/bin/pip

RUN which python
RUN which python3

RUN mkdir -p /errbot /plugins /data /log
WORKDIR /errbot

RUN export LANG=utf-8
ENV PYTHONUTF8=1

RUN pip install -U setuptools pip

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN errbot --init
COPY config.py /errbot/config.py

COPY plugins/* /plugins/

CMD ["errbot", "-c", "/errbot/config.py"]
