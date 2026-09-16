import asyncio
import json
from urllib.request import Request, urlopen

from gdo.base.Logger import Logger
from gdo.base.Message import Message
from gdo.base.Render import Mode
from gdo.core.Connector import Connector
from gdo.core.GDO_Server import GDO_Server


class LUP(Connector):
    """Deliver Dog replies back to the LinkUUp relay endpoint."""

    def get_render_mode(self) -> Mode:
        return Mode.render_txt

    def render_user_connect_help(self) -> str:
        return 'LinkUUp relay'

    def gdo_has_channels(self) -> bool:
        return True

    def gdo_needs_authentication(self) -> bool:
        return False

    @classmethod
    def get_server(cls) -> GDO_Server:
        return GDO_Server.get_by_connector('lup')

    def module_lup(self):
        from gdo.lup_connector.module_lup_connector import module_lup_connector
        return module_lup_connector.instance()

    async def gdo_connect(self) -> bool:
        self._connected = True
        return True

    async def gdo_send_to_channel(self, msg: Message):
        callback = self.module_lup().cfg_callback_url()
        if not callback:
            Logger.warning('LinkUUp reply dropped: lup_callback_url is not configured.')
            return
        room = msg._env_channel.get_name().removeprefix('room-')
        payload = json.dumps({
            'room': room,
            'message': msg._result,
        }).encode()
        request = Request(callback, data=payload, method='POST', headers={
            'Content-Type': 'application/json',
            'X-LUP-Secret': self.module_lup().cfg_shared_secret(),
        })
        try:
            await asyncio.to_thread(urlopen, request, timeout=5)
        except Exception as ex:
            Logger.exception(ex, 'LinkUUp reply delivery failed')

    async def gdo_send_to_user(self, msg: Message, notice: bool = False):
        raise NotImplementedError('LinkUUp only supports room broadcasts.')
