## Build Images for InfluxDB (database for INT data)

```shell
cd llm4netlab/net_env/kathara/p4_int
docker build -t kathara/influxdb .
```

docker run -d --name influxdb kathara/influxdb
docker exec -it influxdb bash

curl http://localhost:8086/health

echo -n "hello" | nc -u -w1 10.0.0.2 5000

```python
from influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi
token='int_token'
org='int_org'
bucket='int_bucket'
url="http://localhost:8086"
with InfluxDBClient(url=url, token=token, org=org) as client:
    query_api: QueryApi = client.query_api()

    # read flow_stat: flow latency and flow path
    query = f'''
        from(bucket: "{bucket}")
        |> range(start: -1h) 
        |> filter(fn: (r) => r["_measurement"] == "flow_stat")
        '''
    tables = query_api.query(query, org=org)
    print("=== flow_stat ===")
    for table in tables:
        for record in table.records:
            print(f"time={record.get_time()}, "
                    f"src_ip={record.values.get('src_ip')}, "
                    f"dst_ip={record.values.get('dst_ip')}, "
                    f"field={record.get_field()}, "
                    f"value={record.get_value()}")

    # read flow_hop_latency
    query = f'''
    from(bucket: "{bucket}")
    |> range(start: -1h)
    |> filter(fn: (r) => r["_measurement"] == "flow_hop_latency")
    '''
    tables = query_api.query(query, org=org)
    print("=== flow_hop_latency ===")
    for table in tables:
        for record in table.records:
            print(f"time={record.get_time()}, sw_id={record.values.get('sw_id')}, "
                f"field={record.get_field()}, value={record.get_value()}")

    # read port_tx_utilization
    query = f'''
    from(bucket: "{bucket}")
    |> range(start: -1h)
    |> filter(fn: (r) => r["_measurement"] == "port_tx_utilization")
    '''
    tables = query_api.query(query, org=org)
    print("=== port_tx_utilization ===")
    for table in tables:
        for record in table.records:
            print(f"time={record.get_time()}, sw_id={record.values.get('sw_id')}, "
                f"egress_id={record.values.get('egress_id')}, "
                f"value={record.get_value()}")

    # read sw_queue_occupancy
    query = f'''
    from(bucket: "{bucket}")
    |> range(start: -1h)
    |> filter(fn: (r) => r["_measurement"] == "sw_queue_occupancy")
    '''
    tables = query_api.query(query, org=org)
    print("=== sw_queue_occupancy ===")
    for table in tables:
        for record in table.records:
            print(f"time={record.get_time()}, sw_id={record.values.get('sw_id')}, "
                f"queue_id={record.values.get('queue_id')}, "
                f"value={record.get_value()}")
```