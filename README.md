# pygdo-lup-connector

Signed LinkUUp ↔ PyGDO/Dog bridge.

## Flow

1. LinkUUp delivers one room message to `lup.to_dog` with `room`, `user`,
   `username`, `displayname`, `lang`, `message`, and the shared `secret`.
2. The method maps that event to a virtual `LinkUUp` server, `room-<id>`
   channel, and `user-<id>` identity, then injects it into Dog.
3. Mira sees and handles it as an ordinary channel event.
4. A reply through `say.in <LinkUUp channel id>` is posted by the LUP connector
   to the configured LinkUUp callback URL as JSON: `{ "room": "<id>",
   "message": "..." }`.

The connector intentionally only supports room broadcasts. LinkUUp implements
the separate private-user-message direction itself.

After `lup_dog_chill`, LinkUUp sends its last `lup_dog_backlog` room lines to
`lup.backlog`; Mira receives one compact context event and replies to the same
virtual room. The connector broadcasts that response through `FromDog`.

The module is disabled by default. Set `lup_enabled`, `lup_shared_secret`, and
`lup_callback_url` before connecting a real LinkUUp instance. LinkUUp must use
the same secret and configure `lup_dog_url` for `lup.to_dog` plus
`lup_dog_backlog_url` for `lup.backlog`.
PyGDO connector for LinkUUp.
