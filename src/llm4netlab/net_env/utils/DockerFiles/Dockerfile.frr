FROM kathara/base:latest

RUN apt-get update && \
    apt-get install -y --no-install-recommends stress-ng isc-dhcp-server isc-dhcp-relay && \
    apt-get clean && rm -rf /var/lib/apt/lists/*