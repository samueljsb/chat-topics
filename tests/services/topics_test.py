from collections.abc import Collection

import attrs
import pytest

from chat_topics.services import topics

# Use the topic type for messages to simplify the tests
Message = topics.Topic


@attrs.frozen
class MessageStore:
    messages: tuple[Message, ...] = ()

    async def get_messages(self, conversation_id: str) -> tuple[Message, ...]:  # noqa: ARG002
        return self.messages


@attrs.frozen
class Voting:
    def extract_topics(
        self, messages: Collection[Message]
    ) -> tuple[topics.Topic, ...]:
        return tuple(messages)


@attrs.frozen
class Reporter:
    sent_reports: list[tuple[str, str]] = attrs.field(factory=list, init=False)

    async def report_topics(
        self, topics: Collection[topics.Topic], conversation_id: str
    ) -> None:
        self.sent_reports.append(
            (conversation_id, '\n'.join(str(topic) for topic in topics))
        )


@pytest.mark.asyncio
class TestTopicReporter:
    async def test_no_messages_in_conversation(self) -> None:
        reporter = Reporter()
        use_case = topics.TopicReporter(
            messages=MessageStore(messages=()),
            vote_counter=Voting(),
            reporter=reporter,
        )

        await use_case.report_topics_for_conversation('conversation-id')

        assert reporter.sent_reports == [('conversation-id', '')]

    async def test_reports_messages(self) -> None:
        reporter = Reporter()
        use_case = topics.TopicReporter(
            messages=MessageStore(
                messages=(
                    Message('Somewhere, over the rainbow', 1),
                    Message('Way up high', 2),
                )
            ),
            vote_counter=Voting(),
            reporter=reporter,
        )

        await use_case.report_topics_for_conversation('conversation-id')

        assert reporter.sent_reports == [
            (
                'conversation-id',
                "Topic(title='Somewhere, over the rainbow', votes=1)\n"
                + "Topic(title='Way up high', votes=2)",
            )
        ]
