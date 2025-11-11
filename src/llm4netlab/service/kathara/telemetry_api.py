import csv
import io
import json

from llm4netlab.service.kathara.base_api import KatharaBaseAPI, _SupportsBase


class TelemetryAPIMixin:
    """
    Interfaces to interact with the in-band telemetry (P4 supported) data stored in InfluxDB within Kathara.
    """

    # Keep these parameters consistent with the InfluxDB configuration in the Dockerfile.
    token = "int_token"
    org = "int_org"
    bucket = "int_bucket"

    def influx_list_buckets(self: _SupportsBase, machine_name: str = "collector") -> list[str]:
        """List all buckets in the InfluxDB instance."""
        query_cmd = "influx bucket list --json"
        return [self._run_cmd(machine_name=machine_name, command=query_cmd)]

    def influx_get_measurements(self: _SupportsBase, machine_name: str = "collector") -> list[str]:
        """List all measurements (tables) in a database"""
        query_cmd = (
            f"""influx query 'import "influxdata/influxdb/schema" schema.measurements(bucket: "{self.bucket}")'"""
        )
        return [self._run_cmd(machine_name=machine_name, command=query_cmd)]

    def influx_count_measurements(self: _SupportsBase, measurement: str, machine_name: str = "collector") -> list[str]:
        """Count the size of all records in a measurement"""
        query_cmd = (
            f'curl -sS --request POST "http://localhost:8086/api/v2/query?org={self.org}" '
            f'--header "Authorization: Token {self.token}" '
            '--header "Accept: application/csv" '
            '--header "Content-type: application/vnd.flux" '
            "--data '"
            f'from(bucket: "{self.bucket}")\n'
            "  |> range(start: -1h)\n"
            f'  |> filter(fn: (r) => r["_measurement"] == "{measurement}")\n'
            f"  |> group(columns: [])\n"
            f"  |> count()"
            "'"
        )
        result = self._run_cmd(machine_name=machine_name, command=query_cmd)
        jsoned_result = self._csv_to_json(result)
        return [jsoned_result]

    def _csv_to_json(self: _SupportsBase, query_result: str) -> list[dict]:
        """Convert CSV query result to JSON format."""
        lines = [line for line in query_result.splitlines() if line.strip() and not line.startswith("#")]

        header = None
        data_lines = []
        for line in lines:
            if line.startswith(",result,"):
                if header is None:
                    header = line.split(",")
                else:
                    continue
            else:
                data_lines.append(line)

        reader = csv.DictReader(io.StringIO("\n".join(data_lines)), fieldnames=header)
        rows = [row for row in reader]
        return json.dumps(rows, indent=2)

    def influx_query_measurement(
        self: _SupportsBase, measurement: str, limit: int = 10, offset: int = 0, machine_name: str = "collector"
    ) -> list[str]:
        """
        ref: https://github.com/influxdata/influxdb3_mcp_server/blob/3fb86fe505f76fddcab4c7740ad62987beb02c45/src/tools/categories/query.tools.ts#L14
        Execute a SQL query against an InfluxDB database (all versions). Returns results in the specified format (defaults to JSON).
        Large Dataset Warning: InfluxDB might contain massive time-series data. Always use count_measurements() first to check size, then LIMIT/OFFSET for large results (>1000 rows).
        """
        query_cmd = (
            f'curl -sS --request POST "http://localhost:8086/api/v2/query?org={self.org}" '
            f'--header "Authorization: Token {self.token}" '
            '--header "Accept: application/csv" '
            '--header "Content-type: application/vnd.flux" '
            "--data '"
            f'from(bucket: "{self.bucket}")\n'
            "  |> range(start: -1h)\n"
            f'  |> filter(fn: (r) => r["_measurement"] == "{measurement}")\n'
            f"  |> limit(n: {limit}, offset: {offset})"
            "'"
        )
        query_result = self._run_cmd(machine_name=machine_name, command=query_cmd)
        jsoned_result = self._csv_to_json(query_result)
        return [jsoned_result]


class KatharaTelemetryAPI(KatharaBaseAPI, TelemetryAPIMixin):
    """
    Kathara interface API to query telemetry data.
    """

    pass


if __name__ == "__main__":
    lab_name = "p4_int"
    kathara_api = KatharaTelemetryAPI(lab_name)
    # print(kathara_api.influx_list_buckets())
    # print(kathara_api.get_measurements())
    print(kathara_api.count_measurements("flow_hop_latency"))
    print(kathara_api.query_measurement("flow_hop_latency", limit=1))
