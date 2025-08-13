from llm4netlab.service.kathara.base import KatharaBaseAPI

# TODO: add iperf, hping3, scapy, etc.


class KatharaWorkloadPing:
    """
    Class to manage workloads in Kathara.
    """

    def __init__(self, lab_name: str):
        self.kathara_api = KatharaBaseAPI(lab_name)
        self.result = None

    def start_workload(self, host: str, dst_ip: str, count: int = 4, interval: int = 1):
        """
        Get the host object for a given host name.
        """
        self.result = self.kathara_api.host_ping(host, dst_ip)
        return self.result

    def check_result(self):
        """
        Check the result of the workload.
        """
        if self.result is None:
            raise ValueError("No result to check.")
        elif isinstance(self.result, str):
            if " 0% packet loss" in self.result:
                return True
            else:
                return False
        elif isinstance(self.result, list):
            for line in self.result:
                if " 0% packet loss" in line:
                    return True
            return False


if __name__ == "__main__":
    # Example usage
    lab_name = "l2_basic_forwarding"
    workload = KatharaWorkloadPing(lab_name)
    result = workload.start_workload("pc1", "10.0.0.6")
    print(result)
    print(workload.check_result())
