import asyncio
import json
import logging
from configparser import SectionProxy
from typing import Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ..smartmeter.meter_data import MeterDataPoint
from .data_sink import DataSink


LOGGER = logging.getLogger("goe")


class GoEDataSink(DataSink):
    def __init__(self, host: str, token: Optional[str] = None, repeat_delay: float = 4.0) -> None:
        self._url = host.rstrip("/") + "/api/set"
        self._token = token
        self._repeat_delay = repeat_delay
        self._power_consumed = 0.0
        self._power_supplied = 0.0
        self._repeat_task: Optional[asyncio.Task] = None

    @staticmethod
    def from_sink_config(config: SectionProxy) -> "GoEDataSink":
        return GoEDataSink(
            host=config.get("host"),
            token=config.get("token") or None,
            repeat_delay=config.getfloat("repeat_delay", fallback=4.0),
        )

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        if self._repeat_task:
            self._repeat_task.cancel()
            try:
                await self._repeat_task
            except asyncio.CancelledError:
                pass
            self._repeat_task = None

    async def send(self, data_point: MeterDataPoint) -> None:
        if data_point.type.identifier == "ACTIVE_POWER_P":
            self._power_consumed = data_point.value
        elif data_point.type.identifier == "ACTIVE_POWER_N":
            self._power_supplied = data_point.value
        else:
            return

        if data_point.type.identifier != "ACTIVE_POWER_N":
            return

        p_grid = self._power_consumed - self._power_supplied
        if self._repeat_task:
            self._repeat_task.cancel()

        await self._send_grid_power_async(p_grid)
        self._repeat_task = asyncio.create_task(self._repeat_grid_power(p_grid))

    async def _repeat_grid_power(self, p_grid: float) -> None:
        try:
            await asyncio.sleep(self._repeat_delay)
            await self._send_grid_power_async(p_grid)
        except asyncio.CancelledError:
            pass

    async def _send_grid_power_async(self, p_grid: float) -> None:
        await asyncio.get_running_loop().run_in_executor(None, self._send_grid_power, p_grid)

    def _send_grid_power(self, p_grid: float) -> None:
        query = urlencode({"ids": json.dumps({"pGrid": p_grid}, separators=(",", ":"))})
        headers = {"Authorization": f"Bearer {self._token}"} if self._token else {}
        request = Request(f"{self._url}?{query}", headers=headers)
        LOGGER.debug("Sending pGrid=%s W to %s", p_grid, self._url)
        try:
            with urlopen(request, timeout=3) as response:
                if response.status >= 300:
                    LOGGER.error("go-e API returned HTTP %s", response.status)
        except OSError as ex:
            LOGGER.error("Could not send grid power to go-e: %s", ex)