from collections.abc import Collection
from typing import Protocol

import attrs

from chat_topics.services import topics
from chat_topics.slack_app import slack


class SlackClient(Protocol):
    async def send_message(
        self, message: str, conversation_id: slack.Conversation
    ) -> None: ...


@attrs.frozen
class SlackReporter:
    client: SlackClient

    async def report_topics(
        self,
        topics: Collection[topics.Topic],
        conversation_id: slack.Conversation,
    ) -> None:
        message = self._format_message(topics)
        await self.client.send_message(message, conversation_id)

    def _format_message(self, topics: Collection[topics.Topic]) -> str:
        return '\n'.join(
            (
                'Topics to discuss:',
                '',
                *(
                    f'{rank}. {topic.title} ({topic.votes} '
                    + ('vote' if topic.votes == 1 else 'votes')
                    + ')'
                    for rank, topic in enumerate(
                        sorted(topics, key=lambda t: t.votes, reverse=True),
                        start=1,
                    )
                ),
            )
        )
