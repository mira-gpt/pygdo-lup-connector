# pygdo-lup-connector

TLS-protected LinkUUp ↔ PyGDO/Dog bridge.

## Flow

1. LinkUUp delivers one room message to `lup_connector.to_dog` with `room`, `user`,
   `username`, `displayname`, `lang`, and `message`.
2. The method maps that event to a virtual `LinkUUp` server, `room-<id>`
   channel, and `user-<id>` identity, then injects it into Dog.
3. Mira sees and handles it as an ordinary channel event.
4. A reply through `say.in <LinkUUp channel id>` is posted by the LUP connector
   to the configured LinkUUp callback URL as JSON: `{ "room": "<id>",
   "message": "..." }`.

The connector intentionally only supports room broadcasts. LinkUUp implements
the separate private-user-message direction itself.

After `lup_dog_chill`, LinkUUp sends its last `lup_dog_backlog` room lines to
`lup_connector.backlog`; Mira receives one compact context event and replies to the same
virtual room. The connector broadcasts that response through `FromDog`.

The module is disabled by default. Set `lup_enabled` and `lup_callback_url`
before connecting a real LinkUUp instance. LinkUUp configures `lup_dog_url` for `lup_connector.to_dog` plus
`lup_dog_backlog_url` for `lup_connector.backlog`.
PyGDO connector for LinkUUp.
