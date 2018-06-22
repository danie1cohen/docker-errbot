#
# errbot container
#
FROM python:3
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
