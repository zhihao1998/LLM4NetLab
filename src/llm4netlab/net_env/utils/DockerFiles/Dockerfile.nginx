FROM kathara/base:latest

RUN apt-get update && \
    apt-get install -y --no-install-recommends stress-ng nginx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*