
import re
import math
import socket
from ansible.errors import AnsibleError, AnsibleParserError

class FilterModule(object):
    def filters(self):
        return {
            'nb_vrf_or_default': self.nb_vrf_or_default,
        }

    def nb_vrf_or_default(self, lookup_result, default_vrf):

        vrf = default_vrf

        # debug "nonetype is not subscriptable" error
        try:
            if len(lookup_result) > 0:
                vrf = lookup_result[-1]['value']['vrf']['name']
        except:
            pass

        return vrf
