FROM rethinkdb:2.4.2-bullseye-slim as rdb

FROM python:3.11-slim-bullseye

RUN apt update && apt install -y \
    libcurl4-openssl-dev \
    libprotobuf-dev
#   build-essential \
#   protobuf-compiler\
#   libboost-all-dev \
#   libncurses5-dev \
#   libjemalloc-dev \
#   wget m4

COPY --from=rdb /usr/bin/rethinkdb /usr/bin/rethinkdb

RUN mkdir -p /app
COPY . /app
WORKDIR /app

RUN which rethinkdb

RUN pip install pipenv
RUN pipenv install --dev --system --deploy

CMD ["pipenv", "run", "test_live"]
