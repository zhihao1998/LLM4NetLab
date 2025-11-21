FROM kathara/pox:latest

RUN apt-get update && \
    apt-get install -y --no-install-recommends stress-ng && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    python3.9 -m pip install --no-cache-dir --break-system-packages ryu eventlet==0.30.2
    