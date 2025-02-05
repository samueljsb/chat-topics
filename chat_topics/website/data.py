from __future__ import annotations

import datetime

import attrs


@attrs.frozen
class Conversation:
    id: str
    title: str
    date: datetime.date
    topics: tuple[Topic, ...]


@attrs.frozen
class Topic:
    title: str
    votes: int


def get_conversations() -> tuple[Conversation, ...]:
    return (
        Conversation(
            'BC1',
            'Book Club 1',
            datetime.date(2025, 1, 1),
            (
                Topic('Was it good?', 4),
                Topic('What about my pony?', 1),
                Topic("What's next?", 3),
            ),
        ),
        Conversation(
            'BC2',
            'Book Club 2',
            datetime.date(2025, 1, 8),
            (
                Topic('PSC: what did we do last week?', 1),
                Topic('Wtf is "complexity"?', 7),
            ),
        ),
    )
