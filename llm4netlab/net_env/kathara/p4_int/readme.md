## Build Images for InfluxDB (database for INT data)

```shell
cd llm4netlab/net_env/kathara/p4_int
docker build -t kathara/influxdb .
```

docker run -d --name influxdb kathara/influxdb
docker exec -it influxdb bash

curl http://localhost:8086/health