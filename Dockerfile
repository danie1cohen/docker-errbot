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
  python3-pip \
  python3-dev

RUN ln -s $(which python3) /usr/local/bin/python
RUN ln -s $(which pip3) /usr/local/bin/pip

RUN python --version

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
