from __future__ import annotations

import logging
import os
from typing import Annotated
from typing import Protocol

import fastapi
import pydantic

from chat_topics.services import topics
from chat_topics.slack_app import client
from chat_topics.slack_app import reporting
from chat_topics.slack_app import slack
from chat_topics.slack_app import voting

logger = logging.getLogger(__name__)


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


def create_topic_reporter() -> topics.TopicReporter[
    slack.Conversation, slack.Message
]:
    slack_client = client.SlackClient(
        auth_token=os.environ['SLACK_AUTH_TOKEN']
    )
    return topics.TopicReporter(
        messages=slack_client,
        vote_counter=voting.VoteCounter(
            topic_markers=frozenset({'PSC', ':psc:'}),
            vote_reactions=frozenset({'psc+1', 'psc'}),
        ),
        reporter=reporting.SlackReporter(client=slack_client),
    )


# ---


class Event(pydantic.BaseModel):
    type: str
    message: Message
    channel: str
    ts: str


class Message(pydantic.BaseModel):
    text: str
    thread_ts: str


class TopicReporter(Protocol):
    async def report_topics_for_conversation(
        self, conversation_id: slack.Conversation
    ) -> None: ...


async def handle_event(
    event: Event,
    topic_reporter: Annotated[
        TopicReporter, fastapi.Depends(create_topic_reporter)
    ],
) -> None:
    if event.type == 'message':
        if _should_report_topics(event):
            conversation_id = slack.Conversation(
                channel_id=event.channel, timestamp=event.message.thread_ts
            )
            await topic_reporter.report_topics_for_conversation(
                conversation_id
            )
        else:
            logger.debug('Ignoring event: %r', event)
    else:
        raise fastapi.HTTPException(status_code=400)


def _should_report_topics(event: Event) -> bool:
    return event.message.text == 'topics plz'
