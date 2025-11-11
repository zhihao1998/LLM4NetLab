from llm4netlab.service.kathara.base_api import KatharaBaseAPI

# TODO: add iperf, hping3, scapy, etc.


class KatharaWorkloadPingAll:
    """
    Class to create a ping_all workload in a Kathara lab.
    """

    def __init__(self, lab_name: str):
        self.kathara_api = KatharaBaseAPI(lab_name)

    def start_workload(self):
        


if __name__ == "__main__":
    # Example usage
    lab_name = "l2_basic_forwarding"
    workload = KatharaWorkloadPing(lab_name)
    result = workload.start_workload("pc1", "10.0.0.6")
    print(result)
    print(workload.check_result())
