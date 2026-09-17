from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_JSON import GDT_JSON
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UInt import GDT_UInt
from gdo.lup_connector.ChatQueue import ChatQueue
from gdo.lup_connector.connector.LUP import LUP


class backlog(Method):
    """Receive a quiet LinkUUp room transcript for Mira to answer."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'lup_connector.to_dog'

    def gdo_method_hidden(self) -> bool:
        return True

    def gdo_user_permission(self) -> str | None:
        return None

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_UInt('room').not_null(),
            GDT_String('room_name').not_null().maxlen(128),
            GDT_String('lang').not_null().minlen(2).maxlen(2).initial('en'),
            GDT_JSON('backlog').not_null(),
        ]

    def module_lup(self):
        from gdo.lup_connector.module_lup_connector import module_lup_connector
        return module_lup_connector.instance()

    def gdo_before_execute(self):
        if not self.module_lup().cfg_enabled():
            raise PermissionError('LinkUUp connector is disabled')

    async def gdo_execute(self) -> GDT:
        server = LUP.get_server()
        room_id = self.param_val('room')
        channel = server.get_or_create_channel(f'room-{room_id}', self.param_val('room_name'))
        channel.save_val('chan_language', self.param_val('lang'))
        lines = self.param_val('backlog')
        transcript = '\n'.join(f"{line['name']}: {line['message']}" for line in lines)
        prompt = f"Quiet LinkUUp room backlog for {self.param_val('room_name')}:\n{transcript}\n\nReply with one warm, concise comment."
        ChatQueue.enqueue(room_id, channel.get_id(), 'LinkUUp', self.param_val('lang'), prompt)
        return self.empty()
