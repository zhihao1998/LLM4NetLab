import asyncio

from llm4netlab.service.kathara import KatharaAPIALL
from llm4netlab.utils.logger import system_logger


class FaultInjectorService:
    def __init__(self, lab_name: str):
        super().__init__()
        self.kathara_api = KatharaAPIALL(lab_name)
        self.logger = system_logger

    async def _renew_dhcp_on_host(self, host: str):
        command = "dhclient -r eth0"
        result = await self.kathara_api.exec_cmd_async(host, command)
        command = "dhclient -v eth0"
        result += await self.kathara_api.exec_cmd_async(host, command)
        return result

    async def _renew_dhcp_on_all_hosts(self):
        hosts = self.kathara_api.get_hosts()
        await asyncio.gather(*(self._renew_dhcp_on_host(h) for h in hosts))
        self.logger.info("Released and renewed DHCP leases on all hosts")

    def inject_wrong_gateway(self, dhcp_server: str, subnet: str, wrong_gw: str):
        sub_escaped = subnet.replace(".", "\\.")
        cmd = (
            f"sed -i '/subnet {sub_escaped} netmask 255\\.255\\.255\\.0/,/}}/ "
            f"s/option routers .*/option routers {wrong_gw};/' /etc/dhcp/dhcpd.conf"
        )
        self.kathara_api.exec_cmd(dhcp_server, cmd)
        self.kathara_api.exec_cmd(dhcp_server, "systemctl restart isc-dhcp-server")
        self.logger.info(f"Injected wrong gateway {wrong_gw} in subnet {subnet}")

        # release address from every host
        asyncio.run(self._renew_dhcp_on_all_hosts())

    def recover_wrong_gateway(self, dhcp_server: str, subnet: str, correct_gw: str):
        sub_escaped = subnet.replace(".", "\\.")
        cmd = (
            f"sed -i '/subnet {sub_escaped} netmask 255\\.255\\.255\\.0/,/}}/ "
            f"s/option routers .*/option routers {correct_gw};/' /etc/dhcp/dhcpd.conf"
        )
        self.kathara_api.exec_cmd(dhcp_server, cmd)
        self.kathara_api.exec_cmd(dhcp_server, "systemctl restart isc-dhcp-server")
        self.logger.info(f"Recovered correct gateway {correct_gw} in subnet {subnet}")

        # release address from every host
        asyncio.run(self._renew_dhcp_on_all_hosts())

    def inject_wrong_dns(self, dhcp_server: str, subnet: str, wrong_dns: str):
        sub_escaped = subnet.replace(".", "\\.")
        cmd = (
            f"sed -i '/subnet {sub_escaped} netmask 255\\.255\\.255\\.0/,/}}/ "
            f"s/option domain-name-servers .*/option domain-name-servers {wrong_dns};/' /etc/dhcp/dhcpd.conf"
        )
        self.kathara_api.exec_cmd(dhcp_server, cmd)
        self.kathara_api.exec_cmd(dhcp_server, "systemctl restart isc-dhcp-server")
        self.logger.info(f"Injected wrong DNS {wrong_dns} in subnet {subnet}")

        # release address from every host
        asyncio.run(self._renew_dhcp_on_all_hosts())

    def recover_wrong_dns(self, dhcp_server: str, subnet: str, correct_dns: str):
        sub_escaped = subnet.replace(".", "\\.")
        cmd = (
            f"sed -i '/subnet {sub_escaped} netmask 255\\.255\\.255\\.0/,/}}/ "
            f"s/option domain-name-servers .*/option domain-name-servers {correct_dns};/' /etc/dhcp/dhcpd.conf"
        )
        self.kathara_api.exec_cmd(dhcp_server, cmd)
        self.kathara_api.exec_cmd(dhcp_server, "systemctl restart isc-dhcp-server")
        self.logger.info(f"Recovered correct DNS {correct_dns} in subnet {subnet}")

        # release address from every host
        asyncio.run(self._renew_dhcp_on_all_hosts())

    def inject_delete_subnet(self, dhcp_server: str, subnet: str):
        sub_escaped = subnet.replace(".", "\\.")
        backup_path = "/etc/dhcp/dhcpd.conf.bak"

        cmd = f"cp /etc/dhcp/dhcpd.conf {backup_path}"
        self.kathara_api.exec_cmd(dhcp_server, cmd)
        cmd = f"sed -i '/subnet {sub_escaped} netmask 255\\.255\\.255\\.0/,/}}/d' /etc/dhcp/dhcpd.conf"
        self.kathara_api.exec_cmd(dhcp_server, cmd)
        self.kathara_api.exec_cmd(dhcp_server, "systemctl restart isc-dhcp-server")

        self.logger.info(f"Deleted subnet {subnet}/24 and saved backup to {backup_path}")

        asyncio.run(self._renew_dhcp_on_all_hosts())

    def recover_deleted_subnet(self, dhcp_server: str):
        backup_path = "/etc/dhcp/dhcpd.conf.bak"

        cmd = f"cp {backup_path} /etc/dhcp/dhcpd.conf"
        self.kathara_api.exec_cmd(dhcp_server, cmd)
        self.kathara_api.exec_cmd(dhcp_server, "systemctl restart isc-dhcp-server")

        self.logger.info(f"Recovered subnet missing from backup {backup_path}")

        asyncio.run(self._renew_dhcp_on_all_hosts())

    def inject_ab_attack(self, attacker_host: str, website: str):
        cmd = f"while true ; do ab -n 200000000 -c 1000 -k http://{website}/ > /dev/null 2>&1; done &"
        self.kathara_api.exec_cmd(attacker_host, cmd)
        self.logger.info(f"Started AB attack from {attacker_host} to {website}")

    def recover_ab_attack(self, attacker_host: str):
        cmd = "pkill ab"
        self.kathara_api.exec_cmd(attacker_host, cmd)
        self.logger.info(f"Stopped AB attack from {attacker_host}")
