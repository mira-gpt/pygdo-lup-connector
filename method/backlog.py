import hmac

from gdo.base.Exceptions import GDOError
from gdo.base.GDT import GDT
from gdo.base.Message import Message
from gdo.base.Method import Method
from gdo.base.Render import Mode
from gdo.core.GDT_JSON import GDT_JSON
from gdo.core.GDT_Secret import GDT_Secret
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UInt import GDT_UInt
from gdo.core.GDT_UserType import GDT_UserType
from gdo.lup_connector.connector.LUP import LUP


class backlog(Method):
    """Receive a quiet LinkUUp room transcript for Mira to answer."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'lup.backlog'

    def gdo_method_hidden(self) -> bool:
        return True

    def gdo_user_permission(self) -> str | None:
        return None

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Secret('secret').not_null(),
            GDT_UInt('room').not_null(),
            GDT_String('room_name').not_null().maxlen(128),
            GDT_String('lang').not_null().exact_len(2).initial('en'),
            GDT_JSON('backlog').not_null(),
        ]

    def module_lup(self):
        from gdo.lup_connector.module_lup_connector import module_lup_connector
        return module_lup_connector.instance()

    def gdo_before_execute(self):
        module = self.module_lup()
        if not module.cfg_enabled() or not hmac.compare_digest(self.param_val('secret'), module.cfg_shared_secret()):
            raise GDOError('err_permission')

    async def gdo_execute(self) -> GDT:
        server = LUP.get_server()
        room_id = self.param_val('room')
        channel = server.get_or_create_channel(f'room-{room_id}', self.param_val('room_name'))
        channel.save_val('chan_language', self.param_val('lang'))
        user = await server.get_or_create_user('lup-backlog', 'LinkUUp', GDT_UserType.BOT)
        await server.on_user_joined(user, channel)
        await channel.on_user_joined(user)
        lines = self.param_val('backlog')
        transcript = '\n'.join(f"{line['name']}: {line['message']}" for line in lines)
        prompt = f"Quiet LinkUUp room backlog for {self.param_val('room_name')}:\n{transcript}\n\nReply with one warm, concise comment."
        message = (Message(prompt, Mode.render_txt).
                   env_server(server).
                   env_channel(channel).
                   env_user(user, True))
        await message.execute()
        return self.empty()
