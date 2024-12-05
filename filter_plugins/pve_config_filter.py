
import re
import math
import socket
from ansible.errors import AnsibleError, AnsibleParserError

class FilterModule(object):
    def filters(self):
        return {
            'pve_parse_disks': self.pve_parse_disks,
            'pve_parse_interfaces': self.pve_parse_interfaces
        }

    def pve_parse_disks(self, config):
        disks = []

        for key in config:
            if re.match(r"^(scsi|virtio|ide|sata)\d+$", key):
                # Skip cdroms
                if "media=cdrom" in config[key]:
                     continue
                # Skip if no size is defined
                if "size=" not in config[key]:
                    continue
                # Parse size
                size = re.search(r"size=(\d+)([KMGT]?)", config[key])
                # calculate size in GByte

                if size.group(2) == "K":
                    size = int(size.group(1)) / 1024 / 1024
                elif size.group(2) == "M":
                    size = int(size.group(1)) / 1024
                elif size.group(2) == "T":
                    size = int(size.group(1)) * 1024
                else:
                    size = int(size.group(1))

                disks.append({
                    "name": key,
                    "size": math.ceil(size)
                })

        return disks

    def pve_parse_interfaces(self, json):
        interfaces = []
        if json["data"] is None:
            return interfaces


        for iface in json["data"]["result"]:
            if "name" not in iface:
                continue
            # Skip docker bridges
            if iface["name"].startswith("docker"):
                continue

            if "ip-addresses" in iface:
                for ip in iface["ip-addresses"]:
                    # Filter out localhost addresses
                    if ip["ip-address"].startswith("127."):
                        continue
                    if ip["ip-address"].startswith("::1"):
                        continue
                    if ip["ip-address"].startswith("fe80:"):
                        continue

                    # Lookup hostname
                    try:
                        hostname = socket.gethostbyaddr(ip["ip-address"])
                    except socket.herror:
                        hostname = None

                    interfaces.append({
                        "name": iface["name"],
                        "ip": ip["ip-address"],
                        "type": ip["ip-address-type"],
                        "prefix": ip["prefix"],
                        "hostname": hostname[0] if hostname is not None else ""
                    })

        return interfaces



