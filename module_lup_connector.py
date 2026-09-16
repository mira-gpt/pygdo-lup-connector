from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.Connector import Connector
from gdo.core.GDO_Server import GDO_Server
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Secret import GDT_Secret
from gdo.core.GDT_String import GDT_String
from gdo.lup_connector.connector.LUP import LUP


class module_lup_connector(GDO_Module):
    """The signed LinkUUp <-> Dog message bridge."""

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Bool('lup_enabled').not_null().initial('0'),
            GDT_Secret('lup_shared_secret').not_null().initial(''),
            GDT_String('lup_callback_url').ascii().maxlen(512).initial(''),
        ]

    def cfg_enabled(self) -> bool:
        return self.get_config_value('lup_enabled')

    def cfg_shared_secret(self) -> str:
        return self.get_config_val('lup_shared_secret')

    def cfg_callback_url(self) -> str:
        return self.get_config_val('lup_callback_url')

    def gdo_init(self):
        Connector.register(LUP)

    async def gdo_install(self):
        if not GDO_Server.get_by_connector('lup'):
            GDO_Server.blank({
                'serv_name': 'LinkUUp',
                'serv_connector': 'lup',
                'serv_trigger': '$',
            }).insert()
