# Build Docker images for all services

docker build -f Dockerfile.frr -t kathara/frr-stress .
docker build -f Dockerfile.base -t kathara/base-stress .
docker build -f Dockerfile.ryu -t kathara/ryu-stress .