from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Message import Message
from gdo.base.Method import Method
from gdo.base.Render import Mode
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UInt import GDT_UInt
from gdo.core.GDT_UserType import GDT_UserType
from gdo.lup_connector.connector.LUP import LUP


class ipc_message(Method):
    """Dog-only consumer for one queued LinkUUp room message."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return ''

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_UInt('room').not_null().positional(),
            GDT_UInt('user').not_null().positional(),
            GDT_String('username').not_null().maxlen(64).positional(),
            GDT_String('displayname').not_null().maxlen(96).positional(),
            GDT_String('lang').not_null().minlen(2).maxlen(2).positional(),
            GDT_RestOfText('message').not_null().positional(),
        ]

    async def gdo_execute(self) -> GDT:
        if not Application.IS_DOG:
            return self.empty()
        server = LUP.get_server()
        room_id = self.param_value('room')
        user_id = self.param_value('user')
        channel = server.get_or_create_channel(f'room-{room_id}', f'LinkUUp #{room_id}')
        channel.save_val('chan_language', self.param_val('lang'))
        user = await server.get_or_create_user(
            f'user-{user_id}', self.param_val('displayname'), GDT_UserType.MEMBER)
        await server.on_user_joined(user, channel)
        await channel.on_user_joined(user)
        Application.MESSAGES.put(
            Message(self.param_val('message'), Mode.render_txt).
            env_server(server).env_channel(channel).env_user(user, True))
        return self.empty()
