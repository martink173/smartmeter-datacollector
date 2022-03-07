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
VZ_KWH = 1000

class VolkszaehlerSink(DataSink):
    def __init__(self, vz_name: str) -> None:
        self._vz = logging.getLogger(vz_name)
        #self._vz.setLevel(logging.INFO)
        self._vz.info("Setting up Volkszaehler sink")
        self._vz_host = "http://127.0.0.1/api/data/"
        self._UUID_power_consumed = "33753cb0-60d0-11eb-84c2-33d111946db0"
        self._UUID_power_supplied = "6f539360-60d0-11eb-97c8-e7dff8db1d3c"
        self._UUID_energy_consumed = "4760a870-4d41-11eb-aa31-e5a92da51201"
        self._UUID_energy_supplied = "76e502d0-4d41-11eb-90f3-395dbb74c0fc"
        self._UUID_reactive_power_p = "171a1f20-724d-11ec-9717-19a1c60c1567"
        self._UUID_reactive_power_n = "65df0c00-724d-11ec-8bec-ff3b7acccd64"
        self._UUID_reactive_energy_p = "8e805d20-724c-11ec-a261-a3a0d3470eb0"
        self._UUID_reactive_energy_n = "ca283300-724c-11ec-9d50-d5fe74a81bef"

        self._power_p = 0
        self._power_n = 0
        self._power_p_set = False
        self._power_n_set = False
        self._power_timestamp = 0

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    def curl_output(self, curl_debug_type, curl_debug_msg):
        #self._vz.debug("CURL %d output: %s" % (curl_debug_type, curl_debug_msg))
        return

    def curl_output2(self, log):
        #self._vz.debug("CURL: %s" % log)
        return

    async def send(self, data_point: MeterDataPoint) -> None:
        self._vz.debug(str(data_point))
        # grab needed data points for sending to volkszaehler
        if data_point.type.identifier == "ACTIVE_POWER_P":
            self._power_p = data_point.value
            self._power_timestamp = data_point.timestamp
            self._power_p_set = True
        elif data_point.type.identifier == "ACTIVE_POWER_N":
            self._power_n = data_point.value
            self._power_n_set = True
        elif data_point.type.identifier == "ACTIVE_ENERGY_P_TOTAL":
            link1 = self._vz_host + self._UUID_energy_consumed + ".json?operation=add&ts=" + "%.0f"%(data_point.timestamp.timestamp()*VZ_MILLISECONDS) + "&value=" + "%.3f"%(data_point.value / VZ_KWH)
        elif data_point.type.identifier == "ACTIVE_ENERGY_N_TOTAL":
            link1 = self._vz_host + self._UUID_energy_supplied + ".json?operation=add&ts=" + "%.0f"%(data_point.timestamp.timestamp()*VZ_MILLISECONDS) + "&value=" + "%.3f"%(data_point.value / VZ_KWH)
        elif data_point.type.identifier == "REACTIVE_POWER_P":
            link1 = self._vz_host + self._UUID_reactive_power_p + ".json?operation=add&ts=" + "%.0f"%(data_point.timestamp.timestamp()*VZ_MILLISECONDS) + "&value=" + "%.3f"%(data_point.value / VZ_KWH)
        elif data_point.type.identifier == "REACTIVE_POWER_N":
            link1 = self._vz_host + self._UUID_reactive_power_n + ".json?operation=add&ts=" + "%.0f"%(data_point.timestamp.timestamp()*VZ_MILLISECONDS) + "&value=" + "%.3f"%(data_point.value / VZ_KWH)
        elif data_point.type.identifier == "REACTIVE_ENERGY_P_TOTAL":
            link1 = self._vz_host + self._UUID_reactive_energy_p + ".json?operation=add&ts=" + "%.0f"%(data_point.timestamp.timestamp()*VZ_MILLISECONDS) + "&value=" + "%.3f"%(data_point.value / VZ_KWH)
        elif data_point.type.identifier == "REACTIVE_ENERGY_N_TOTAL":
            link1 = self._vz_host + self._UUID_reactive_energy_n + ".json?operation=add&ts=" + "%.0f"%(data_point.timestamp.timestamp()*VZ_MILLISECONDS) + "&value=" + "%.3f"%(data_point.value / VZ_KWH)
        else:
            pass # not relevant for sending to vz

        if self._power_p_set and self._power_n_set:
            power = self._power_p - self._power_n
            if power > 0:
                link1 = self._vz_host + self._UUID_power_consumed + ".json?operation=add&ts=" + "%.0f"%(self._power_timestamp.timestamp()*VZ_MILLISECONDS) + "&value=" + "%.3f"%(power / VZ_KW)
                link2 = self._vz_host + self._UUID_power_supplied + ".json?operation=add&ts=" + "%.0f"%(self._power_timestamp.timestamp()*VZ_MILLISECONDS) + "&value=" + "%.3f"%(0 / VZ_KW)
            else:
                link1 = self._vz_host + self._UUID_power_consumed + ".json?operation=add&ts=" + "%.0f"%(self._power_timestamp.timestamp()*VZ_MILLISECONDS) + "&value=" + "%.3f"%(0 / VZ_KW)
                link2 = self._vz_host + self._UUID_power_supplied + ".json?operation=add&ts=" + "%.0f"%(self._power_timestamp.timestamp()*VZ_MILLISECONDS) + "&value=" + "%.3f"%(abs(power) / VZ_KW)
            
            self._power_p_set = False
            self._power_n_set = False

        # Send to volkszaehler through curl
        if 'link1' in locals():
            self.send_link(link1)

        if 'link2' in locals():
            self.send_link(link2)

            #self._vz.debug("Send to: " + link)
            #try:
            #    c = pycurl.Curl()
            #except pycurl.error as e:
            #    self._vz.error("Failed to send to: " + link)
            #c.setopt(c.URL, link)
            #c.setopt(c.VERBOSE, False)
            #c.setopt(c.DEBUGFUNCTION, self.curl_output)
            #c.setopt(c.WRITEFUNCTION, self.curl_output2)
            #c.setopt(c.HEADERFUNCTION, self.curl_output2)
            #result = c.perform()
            #c.close()

    def send_link(self, link):
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
