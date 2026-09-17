import tomllib

from gdo.base.GDO_Module import GDO_Module
from gdo.base.Application import Application
from gdo.base.Events import Events
from gdo.base.GDT import GDT
from gdo.core.Connector import Connector
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDT_Bool import GDT_Bool
from gdo.lup_connector.connector.LUP import LUP


class module_lup_connector(GDO_Module):
    """The signed LinkUUp <-> Dog message bridge."""

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Bool('lup_enabled').not_null().initial('0'),
        ]

    def cfg_enabled(self) -> bool:
        return self.get_config_value('lup_enabled')

    def cfg_callback_url(self) -> str:
        return self._secret_value('callback_url')

    def cfg_shared_secret(self) -> str:
        return self._secret_value('shared_secret')

    def _secret_value(self, key: str) -> str:
        try:
            with open(self.file_path('secret.toml'), 'rb') as handle:
                return str(tomllib.load(handle).get(key, ''))
        except FileNotFoundError:
            return ''

    def gdo_init(self):
        Connector.register(LUP)
        if Application.IS_DOG:
            Application.EVENTS.add_timer_async(3.14, LUP().poll_chat_queue, Events.FOREVER)

    async def gdo_install(self):
        if not GDO_Server.get_by_connector('lup'):
            GDO_Server.blank({
                'serv_name': 'LinkUUp',
                'serv_connector': 'lup',
                'serv_trigger': '$',
            }).insert()
