from __future__ import annotations

import os
from collections.abc import Collection
from collections.abc import Generator

import attrs
import fastapi
import pydantic

from chat_topics.slack_app import client


def create_app() -> fastapi.FastAPI:
    app = fastapi.FastAPI(
        title='chat-topics',
        summary=None,
        version='',
        # Disable automatic documentation.
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
        swagger_ui_oauth2_redirect_url=None,
    )

    app.post('/events/')(handle_event)

    return app


# ---


class Event(pydantic.BaseModel):
    type: str
    message: Event.Message
    channel: str
    ts: str

    class Message(pydantic.BaseModel):
        text: str
        thread_ts: str


async def handle_event(event: Event) -> None:
    if event.message.text != 'topics plz':
        return

    slack_client = client.SlackClient(
        auth_token=os.environ['SLACK_AUTH_TOKEN'],
    )
    conversation = Conversation(
        channel_id=event.channel, timestamp=event.message.thread_ts
    )
    await report_topics(conversation, slack_client)


@attrs.frozen
class Conversation:
    channel_id: str
    timestamp: str


async def report_topics(
    conversation: Conversation,
    slack_client: client.SlackClient,
) -> None:
    messages = await slack_client.get_messages(conversation)
    topics = tuple(_filter_topics(messages))
    report = _format_message(topics)
    await slack_client.send_message(report, conversation)


@attrs.frozen
class Topic:
    title: str
    votes: int


def _filter_topics(messages: Collection[client.Message]) -> Generator[Topic]:
    for message in messages:
        is_topic = any(
            message.text.startswith(marker) for marker in ('PSC', ':psc:')
        )
        votes = sum(
            count
            for reaction, count in message.reactions.items()
            if reaction in {'psc+1', 'psc'}
        )

        if not (is_topic or votes):
            continue

        yield Topic(
            message.text,
            votes + 1,  # add a vote for the message author
        )


def _format_message(topics: Collection[Topic]) -> str:
    return '\n'.join(
        (
            'Topics to discuss:',
            '',
            *(
                f"""\
{rank}. {topic.title} ({topic.votes} {'vote' if topic.votes == 1 else 'votes'})
"""
                for rank, topic in enumerate(
                    sorted(topics, key=lambda t: t.votes, reverse=True),
                    start=1,
                )
            ),
        )
    )
