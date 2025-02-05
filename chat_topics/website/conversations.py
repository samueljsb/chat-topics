from __future__ import annotations

import datetime
from typing import Annotated, Protocol

import fastapi
import fastapi.responses
import fastapi.templating


def get_templates() -> fastapi.templating.Jinja2Templates:
    return fastapi.templating.Jinja2Templates(
        directory='chat_topics/website/templates'
    )


class ConversationStorage(Protocol):
    def get_conversations(self) -> tuple[Conversation, ...]: ...


class Conversation(Protocol):
    @property
    def title(self) -> str: ...

    @property
    def date(self) -> datetime.date: ...

    @property
    def topics(self) -> tuple[Topic, ...]: ...


class Topic(Protocol):
    @property
    def title(self) -> str: ...

    @property
    def votes(self) -> int: ...


def get_conversation_storage() -> ConversationStorage:
    from . import data

    return data


async def list_conversations(
    request: fastapi.Request,
    templates: Annotated[
        fastapi.templating.Jinja2Templates,
        fastapi.Depends(get_templates),
    ],
    conversation_storage: Annotated[
        ConversationStorage,
        fastapi.Depends(get_conversation_storage),
    ],
) -> fastapi.responses.HTMLResponse:
    conversations = conversation_storage.get_conversations()

    context = {
        'conversations': tuple(
            {
                'title': conversation.title,
                'date': conversation.date.isoformat(),
                'topics': tuple(
                    {'title': topic.title, 'votes': topic.votes}
                    for topic in sorted(
                        conversation.topics,
                        key=lambda t: t.votes,
                        reverse=True,
                    )
                ),
            }
            for conversation in sorted(
                conversations, key=lambda c: c.date, reverse=True
            )
        ),
    }

    return templates.TemplateResponse(
        request,
        'conversations.html',
        context=context,
    )
