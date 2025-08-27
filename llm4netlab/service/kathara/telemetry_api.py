from llm4netlab.service.kathara.base_api import KatharaBaseAPI, _SupportsBase


class TelemetryAPIMixin:
    """
    Interfaces to interact with the in-band telemetry (P4 supported) data stored in InfluxDB within Kathara.
    TODO: all apis return all data by default, consider adding parameters to filter data.
    """

    # Keep these parameters consistent with the InfluxDB configuration in the Dockerfile.
    token = "int_token"
    org = "int_org"
    bucket = "int_bucket"

    def query_flow_stat(self: _SupportsBase, machine_name: str = "collector") -> list[str]:
        """
        Query flow latency and flow path of all flows.
        """
        query_cmd = (
            f'curl -sS --request POST "http://localhost:8086/api/v2/query?org={self.org}" '
            f'--header "Authorization: Token {self.token}" '
            '--header "Accept: application/csv" '
            '--header "Content-type: application/vnd.flux" '
            "--data '"
            f'from(bucket: "{self.bucket}")\n'
            "  |> range(start: -1h)\n"
            '  |> filter(fn: (r) => r["_measurement"] == "flow_stat")'
            "'"
        )
        return self._run_cmd(machine_name=machine_name, command=query_cmd)

    def query_flow_hop_latency(self: _SupportsBase, machine_name: str = "collector") -> list[str]:
        """
        Query hop latency for each hop in all flows.
        """
        query_cmd = (
            f'curl -sS --request POST "http://localhost:8086/api/v2/query?org={self.org}" '
            f'--header "Authorization: Token {self.token}" '
            '--header "Accept: application/csv" '
            '--header "Content-type: application/vnd.flux" '
            "--data '"
            f'from(bucket: "{self.bucket}")\n'
            "  |> range(start: -1h)\n"
            '  |> filter(fn: (r) => r["_measurement"] == "flow_hop_latency")'
            "'"
        )
        return self._run_cmd(machine_name=machine_name, command=query_cmd)

    def query_port_tx_utilization(self: _SupportsBase, machine_name: str = "collector") -> list[str]:
        """
        Query port utilization of all collected ports.
        """
        query_cmd = (
            f'curl -sS --request POST "http://localhost:8086/api/v2/query?org={self.org}" '
            f'--header "Authorization: Token {self.token}" '
            '--header "Accept: application/csv" '
            '--header "Content-type: application/vnd.flux" '
            "--data '"
            f'from(bucket: "{self.bucket}")\n'
            "  |> range(start: -1h)\n"
            '  |> filter(fn: (r) => r["_measurement"] == "port_tx_utilization")'
            "'"
        )
        return self._run_cmd(machine_name=machine_name, command=query_cmd)

    def query_sw_queue_occupancy(self: _SupportsBase, machine_name: str = "collector") -> list[str]:
        """
        Query switch queue occupancy of all collected switches.
        """
        query_cmd = (
            f'curl -sS --request POST "http://localhost:8086/api/v2/query?org={self.org}" '
            f'--header "Authorization: Token {self.token}" '
            '--header "Accept: application/csv" '
            '--header "Content-type: application/vnd.flux" '
            "--data '"
            f'from(bucket: "{self.bucket}")\n'
            "  |> range(start: -1h)\n"
            '  |> filter(fn: (r) => r["_measurement"] == "sw_queue_occupancy")'
            "'"
        )
        return self._run_cmd(machine_name=machine_name, command=query_cmd)


class KatharaTelemetryAPI(KatharaBaseAPI, TelemetryAPIMixin):
    """
    Kathara interface API to query telemetry data.
    """

    pass


if __name__ == "__main__":
    lab_name = "p4_int"
    kathara_api = KatharaTelemetryAPI(lab_name)
    for i in eval(kathara_api.query_flow_stat()):
        print(i)
    for i in eval(kathara_api.query_flow_hop_latency()):
        print(i)
    for i in eval(kathara_api.query_port_tx_utilization()):
        print(i)
    for i in eval(kathara_api.query_sw_queue_occupancy()):
        print(i)
