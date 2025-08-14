FROM kathara/base:latest

LABEL maintainer="Zhihao Wang in LLM4NetLab Team <zhihao.wang@polito.it>"

ARG DEBIAN_FRONTEND=noninteractive

# Install InfluxDB2
RUN set -eux; \
    apt-get update && apt-get install -y curl gnupg ca-certificates; \
    curl --silent --location -O https://repos.influxdata.com/influxdata-archive.key; \
    gpg --show-keys --with-fingerprint --with-colons ./influxdata-archive.key 2>&1 \
      | grep -q '^fpr:\+24C975CBA61A024EE1B631787C3D57159FC2F927:$'; \
    cat influxdata-archive.key | gpg --dearmor \
      | tee /etc/apt/trusted.gpg.d/influxdata-archive.gpg > /dev/null; \
    echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive.gpg] https://repos.influxdata.com/debian stable main' \
      | tee /etc/apt/sources.list.d/influxdata.list; \
    apt-get update && apt-get install -y influxdb2; \
    rm -rf /var/lib/apt/lists/* influxdata-archive.key; \
    pip install influxdb-client --break-system-packages

COPY docker-entrypoint.sh docker-entrypoint.sh
RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["/bin/bash", "docker-entrypoint.sh"]

