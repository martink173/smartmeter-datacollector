#
# This file is part of smartmeter-datacollector.
#
# Added by Martin Krammer, 2022
#
# SPDX-License-Identifier: GPL-2.0-only
# See LICENSES/README.md for more information.
#
import logging

from smartmeter_datacollector.sinks.mqtt_sink import LOGGER

from ..smartmeter.meter_data import MeterDataPoint
from .data_sink import DataSink
import pycurl

VZ_MILLISECONDS = 1000
VZ_KW = 1000

class VolkszaehlerSink(DataSink):
    def __init__(self, vz_name: str) -> None:
        self._vz = logging.getLogger(vz_name)
        self._vz.setLevel(logging.INFO)
        self._vz.info("Setting up Volkszaehler sink")
        self._vz_host = "http://127.0.0.1/api/data/"
        self._UUID_consumed = "33753cb0-60d0-11eb-84c2-33d111946db0"
        self._UUID_supplied = "6f539360-60d0-11eb-97c8-e7dff8db1d3c"

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    def curl_output(self, curl_debug_type, curl_debug_msg):
        self._vz.debug("CURL %d output: %s" % (curl_debug_type, curl_debug_msg))
        return

    def curl_output2(self, log):
        self._vz.debug("CURL: %s" % log)
        return

    async def send(self, data_point: MeterDataPoint) -> None:
        self._vz.debug(str(data_point))
        # grab needed data points for sending to volkszaehler
        if data_point.type.identifier == "ACTIVE_POWER_P":
            link = self._vz_host + self._UUID_consumed + ".json?operation=add&ts=" + "%.0f"%(data_point.timestamp.timestamp()*VZ_MILLISECONDS) + "&value=" + "%.3f"%(data_point.value / VZ_KW)
        elif data_point.type.identifier == "ACTIVE_POWER_N":
            link = self._vz_host + self._UUID_supplied + ".json?operation=add&ts=" + "%.0f"%(data_point.timestamp.timestamp()*VZ_MILLISECONDS) + "&value=" + "%.3f"%(data_point.value / VZ_KW)
        else:
            pass # not relevant for sending to vz

        # Send to volkszaehler through curl
        if 'link' in locals():
            self._vz.debug("Send to: " + link)
            try:
                c = pycurl.Curl()
            except pycurl.error as e:
                self._vz.error("Failed to send to: " + link)
            c.setopt(c.URL, link)
            c.setopt(c.VERBOSE, False)
            c.setopt(c.DEBUGFUNCTION, self.curl_output)
            c.setopt(c.WRITEFUNCTION, self.curl_output2)
            c.setopt(c.HEADERFUNCTION, self.curl_output2)
            result = c.perform()
            c.close()



                        
