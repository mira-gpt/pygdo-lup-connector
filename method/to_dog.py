from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UInt import GDT_UInt
from gdo.lup_connector.ChatQueue import ChatQueue
from gdo.lup_connector.connector.LUP import LUP


class to_dog(Method):
    """Append one LinkUUp room event to Dog's IBDES hand-off queue."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'lup.to_dog'

    def gdo_method_hidden(self) -> bool:
        return True

    def gdo_user_permission(self) -> str | None:
        return None

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_UInt('room').not_null(),
            GDT_UInt('user').not_null(),
            GDT_String('username').not_null().maxlen(64),
            GDT_String('displayname').maxlen(96),
            GDT_String('lang').not_null().minlen(2).maxlen(2).initial('en'),
            GDT_RestOfText('message').not_null(),
        ]

    def module_lup(self):
        from gdo.lup_connector.module_lup_connector import module_lup_connector
        return module_lup_connector.instance()

    def gdo_before_execute(self):
        if not self.module_lup().cfg_enabled():
            raise PermissionError('LinkUUp connector is disabled')

    async def gdo_execute(self) -> GDT:
        room_id = self.param_value('room')
        channel = LUP.get_server().get_or_create_channel(f'room-{room_id}', f'LinkUUp #{room_id}')
        language = self.param_val('lang')
        channel.save_val('chan_language', language)
        ChatQueue.enqueue(
            room_id, channel.get_id(), self.param_val('displayname') or self.param_val('username'),
            language, self.param_val('message'))
        return self.empty()
