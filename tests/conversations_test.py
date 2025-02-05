from __future__ import annotations

import datetime

import attrs
import fastapi
import pytest

from chat_topics.website import conversations


@attrs.frozen
class ConversationStorage:
    conversations: tuple[Conversation, ...]

    def get_conversations(self) -> tuple[Conversation, ...]:
        return self.conversations


@attrs.frozen
class Conversation:
    title: str
    date: datetime.date
    topics: tuple[Topic, ...]


@attrs.frozen
class Topic:
    title: str
    votes: int


@pytest.mark.asyncio
class TestListConversations:
    async def test_no_conversations(self) -> None:
        conversations_storage = ConversationStorage(
            (
                Conversation(
                    'Conversation One',
                    datetime.date(2025, 1, 1),
                    (
                        Topic('Four', 4),
                        Topic('One', 1),
                        Topic('Three', 3),
                    ),
                ),
                Conversation(
                    'Conversation Two',
                    datetime.date(2025, 1, 2),
                    (
                        Topic('Three', 3),
                        Topic('Two', 2),
                        Topic('Five', 5),
                    ),
                ),
            )
        )

        request = fastapi.Request(scope={'type': 'http'})
        response = await conversations.list_conversations(
            request,
            templates=conversations.get_templates(),
            conversation_storage=conversations_storage,
        )

        assert response.status_code == 200
        assert response.context['conversations'] == (  # type: ignore[attr-defined]
            {
                'title': 'Conversation Two',
                'date': '2025-01-02',
                'topics': (
                    {'title': 'Five', 'votes': 5},
                    {'title': 'Three', 'votes': 3},
                    {'title': 'Two', 'votes': 2},
                ),
            },
            {
                'title': 'Conversation One',
                'date': '2025-01-01',
                'topics': (
                    {'title': 'Four', 'votes': 4},
                    {'title': 'Three', 'votes': 3},
                    {'title': 'One', 'votes': 1},
                ),
            },
        )
