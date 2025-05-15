from ai4netops.generator.fault.injector_base import BaseFaultInjector
from ai4netops.tools.bmv2_thrift_api import Bmv2ThriftAPI

class BMv2FaultInjector(BaseFaultInjector):
    """Fault injector for BMv2 devices."""
    def __init__(self, bmv2_thrift_port=9090, bmv2_thrift_ip="localhost"):
        super().__init__()
        self.bmv2_thrift_api = Bmv2ThriftAPI(thrift_port=bmv2_thrift_port, thrift_ip=bmv2_thrift_ip)

    # def inject_