# pygdo-lup-connector

TLS-protected LinkUUp ↔ PyGDO/Dog bridge.

## Flow

1. After `lup_dog_chill`, LinkUUp delivers its buffered room transcript to
   `lup_connector.to_dog` with `room`, `room_name`, `lang`, and `backlog`.
2. The method maps that event to a virtual `LinkUUp` server and `room-<id>`
   channel, then places one compact context event into Dog's queue.
3. Mira sees and handles it as an ordinary channel event.
4. A reply through `say.in <LinkUUp channel id>` is posted by the LUP connector
   to the configured LinkUUp callback URL as JSON: `{ "room": "<id>",
   "message": "..." }`.

The connector intentionally only supports room broadcasts. LinkUUp implements
the separate private-user-message direction itself.

The module is disabled by default. Set `lup_enabled` and `lup_callback_url`
before connecting a real LinkUUp instance. LinkUUp configures
`lup_dog_backlog_url` for `lup_connector.to_dog`.
PyGDO connector for LinkUUp.
