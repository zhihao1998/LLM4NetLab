from llm4netlab.service.kathara.base_api import KatharaBaseAPI
from llm4netlab.service.kathara.bmv2_api import BMv2APIMixin, KatharaBMv2API
from llm4netlab.service.kathara.frr_api import FRRAPIMixin, KatharaFRRAPI
from llm4netlab.service.kathara.intf_api import IntfAPIMixin, KatharaIntfAPI
from llm4netlab.service.kathara.nftable_api import KatharaNFTableAPI, NFTableMixin
from llm4netlab.service.kathara.tc_api import KatharaTCAPI, TCMixin
from llm4netlab.service.kathara.telemetry_api import KatharaTelemetryAPI, TelemetryAPIMixin


class KatharaAPIALL(KatharaBaseAPI, BMv2APIMixin, FRRAPIMixin, IntfAPIMixin, NFTableMixin, TCMixin, TelemetryAPIMixin):
    """
    Combined API for all Kathara functionalities.
    """

    pass
