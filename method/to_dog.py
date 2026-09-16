import hmac

from gdo.base.IPC import IPC
from gdo.base.Exceptions import GDOError
from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.core.GDT_Secret import GDT_Secret
from gdo.core.GDT_String import GDT_String
from gdo.core.GDT_UInt import GDT_UInt


class to_dog(Method):
    """Accept one authenticated LinkUUp room event and inject it into Dog."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'lup.to_dog'

    def gdo_method_hidden(self) -> bool:
        return True

    def gdo_user_permission(self) -> str | None:
        return None

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Secret('secret').not_null(),
            GDT_UInt('room').not_null(),
            GDT_UInt('user').not_null(),
            GDT_String('username').not_null().maxlen(64),
            GDT_String('displayname').maxlen(96),
            GDT_String('lang').not_null().exact_len(2).initial('en'),
            GDT_RestOfText('message').not_null(),
        ]

    def module_lup(self):
        from gdo.lup_connector.module_lup_connector import module_lup_connector
        return module_lup_connector.instance()

    def gdo_before_execute(self):
        module = self.module_lup()
        secret = self.param_val('secret')
        if not module.cfg_enabled() or not hmac.compare_digest(secret, module.cfg_shared_secret()):
            raise GDOError('err_permission')

    async def gdo_execute(self) -> GDT:
        # HTTP and Dog are separate processes. Hand the incoming event to the
        # persistent IPC queue; the Dog process then creates and executes the
        # actual channel message in its own runtime.
        IPC.send('lup_connector.ipc_message', (
            self.param_val('room'),
            self.param_val('user'),
            self.param_val('username'),
            self.param_val('displayname') or self.param_val('username'),
            self.param_val('lang'),
            self.param_val('message'),
        ))
        return self.empty()
