import attrs
import pytest

from chat_topics.services import topics
from chat_topics.slack_app import reporting
from chat_topics.slack_app import slack


@attrs.frozen
class FakeClient:
    sent_messages: list[tuple[slack.Conversation, str]] = attrs.field(
        factory=list, init=False
    )

    async def send_message(
        self, message: str, conversation_id: slack.Conversation
    ) -> None:
        self.sent_messages.append((conversation_id, message))


@pytest.mark.asyncio
class TestSlackReporter:
    async def test_report_topics(self) -> None:
        client = FakeClient()
        reporter = reporting.SlackReporter(client)

        await reporter.report_topics(
            (
                topics.Topic('Somewhere, over the rainbow', 1),
                topics.Topic('Way up high', 2),
            ),
            slack.Conversation(channel_id='channel', timestamp='123'),
        )

        assert client.sent_messages == [
            (
                slack.Conversation(channel_id='channel', timestamp='123'),
                """\
Topics to discuss:

1. Way up high (2 votes)
2. Somewhere, over the rainbow (1 vote)""",
            )
        ]
