"""Small, file-backed hand-off queue for LinkUUp room events."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from gdo.base.Application import Application
from gdo.base.Util import Files
from gdo.date.Time import Time


@dataclass(frozen=True)
class QueuedRoomChat:
    room: int
    language: str
    payload: str
    staging_path: Path


class ChatQueue:
    """Append IBDES records in HTTP and atomically consume them in Dog."""

    ROOT = 'dog_mira/LinkUUp/channel'

    @classmethod
    def path(cls, room: int) -> Path:
        return Path(Application.temp_path(f'{cls.ROOT}/room-{room}.ibdes'))

    @staticmethod
    def language(value: str) -> str:
        return value.lower() if re.fullmatch(r'[a-z]{2}', value.lower()) else 'en'

    @staticmethod
    def compact(value: str) -> str:
        return re.sub(r'(?:\r\n|\r|\n)+', ' ', value).strip()

    @classmethod
    def enqueue(cls, room: int, channel_id: int, username: str,
                language: str, message: str) -> None:
        path = cls.path(room)
        mode = int(Application.config('file.mode.dir', "0o0700"))
        Files.create_dir(str(path.parent), mode)
        record = f"{Time.get_date()} #{channel_id} {cls.compact(username)}{{LinkUUp}} {cls.compact(message)}\n"
        with path.open('a', encoding='utf-8') as handle:
            handle.write(record)

    @classmethod
    def enqueue_backlog(cls, room: int, channel_id: int, language: str,
                        backlog: list[dict[str, object]]) -> None:
        """Append a complete remote-room backlog as individual IBDES rows."""
        path = cls.path(room)
        mode = int(Application.config('file.mode.dir', "0o0700"))
        Files.create_dir(str(path.parent), mode)
        with path.open('a', encoding='utf-8') as handle:
            for line in backlog:
                timestamp = cls.compact(str(line.get('time', Time.get_date())))
                username = cls.compact(str(line.get('name', 'LinkUUp')))
                message = cls.compact(str(line.get('message', '')))
                handle.write(f"{timestamp} #{channel_id} {username}{{LinkUUp}} {message}\n")

    @classmethod
    def take_all(cls) -> list[QueuedRoomChat]:
        root = Path(Application.temp_path(cls.ROOT))
        if not root.is_dir():
            return []
        queued: list[QueuedRoomChat] = []
        for path in sorted(root.glob('room-*.ibdes')):
            match = re.fullmatch(r'room-(\d+)\.ibdes', path.name)
            if not match:
                continue
            staging = path.with_suffix('.sending')
            try:
                os.replace(path, staging)
                payload = staging.read_text(encoding='utf-8')
            except OSError:
                continue
            room = int(match.group(1))
            queued.append(QueuedRoomChat(room, 'en', payload, staging))
        return queued

    @staticmethod
    def acknowledge(item: QueuedRoomChat) -> None:
        item.staging_path.unlink(missing_ok=True)

    @classmethod
    def restore(cls, item: QueuedRoomChat) -> None:
        target = cls.path(item.room)
        try:
            with target.open('a', encoding='utf-8') as handle:
                handle.write(item.payload)
        finally:
            item.staging_path.unlink(missing_ok=True)
