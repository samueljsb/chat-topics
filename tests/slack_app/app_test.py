import attrs
import fastapi
import pytest

from chat_topics.slack_app import app
from chat_topics.slack_app import slack


@attrs.frozen
class FakeReporter:
    conversations_reported: list[slack.Conversation] = attrs.field(
        factory=list, init=False
    )

    async def report_topics_for_conversation(
        self, conversation_id: slack.Conversation
    ) -> None:
        self.conversations_reported.append(conversation_id)


@pytest.mark.asyncio
class TestHandleEvent:
    async def test_unexpected_events_are_errors(self) -> None:
        reporter = FakeReporter()

        event = app.Event(
            type='app_mention',
            message=app.Message(
                text='Hi, <@U0LAN0Z89>!', thread_ts='1482960137.003543'
            ),
            channel='C123ABC456',
            ts='1515449522.000016',
        )
        with pytest.raises(fastapi.HTTPException) as exc_info:
            await app.handle_event(event, topic_reporter=reporter)

        assert exc_info.value.status_code == 400
        assert reporter.conversations_reported == []

    async def test_message_event_does_not_report_if_not_triggered(
        self,
    ) -> None:
        reporter = FakeReporter()

        event = app.Event(
            type='message',
            message=app.Message(
                text='Hi, <@U0LAN0Z89>!', thread_ts='1482960137.003543'
            ),
            channel='C123ABC456',
            ts='1515449522.000016',
        )
        await app.handle_event(event, topic_reporter=reporter)

        assert reporter.conversations_reported == []

    async def test_message_event_reports_when_triggered(self) -> None:
        reporter = FakeReporter()

        event = app.Event(
            type='message',
            message=app.Message(
                text='topics plz', thread_ts='1482960137.003543'
            ),
            channel='C123ABC456',
            ts='1515449522.000016',
        )
        await app.handle_event(event, topic_reporter=reporter)

        assert reporter.conversations_reported == [
            slack.Conversation(
                channel_id='C123ABC456', timestamp='1482960137.003543'
            )
        ]
