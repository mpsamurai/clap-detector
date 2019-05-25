FROM mpsamurai/neochi-dev-base:20190424-raspbian

WORKDIR /tmp

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y libasound2-dev

RUN wget -O pyalsaaudio.zip https://github.com/larsimmisch/pyalsaaudio/archive/0.8.4.zip && \
    unzip pyalsaaudio.zip && \
    mv pyalsaaudio-0.8.4 pyalsaaudio && \
    rm pyalsaaudio.zip && \
    cd /tmp/pyalsaaudio && \
    python3 setup.py build && \
    python3 setup.py install && \
    rm -Rf /tmp/*

RUN apt-get autoclean

WORKDIR /code
COPY ./src /code

#CMD ["python", "main.py"]
