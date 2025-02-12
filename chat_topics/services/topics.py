from collections.abc import Collection
from typing import Protocol

import attrs


@attrs.frozen
class Topic:
    title: str
    votes: int


class Messages[TConversationId, TMessage](Protocol):
    async def get_messages(
        self, conversation_id: TConversationId
    ) -> tuple[TMessage, ...]: ...


class VoteCounter[TMessage](Protocol):
    def extract_topics(
        self, messages: Collection[TMessage]
    ) -> tuple[Topic, ...]: ...


class Reporter[TConversationId](Protocol):
    async def report_topics(
        self, topics: Collection[Topic], conversation_id: TConversationId
    ) -> None: ...


@attrs.frozen
class TopicReporter[TConversationId, TMessage]:
    """
    Report topics raised in a conversation.

    The vote counter is responsible for determining which messages represent
    topics and how they have been voted for.
    """

    messages: Messages[TConversationId, TMessage]
    vote_counter: VoteCounter[TMessage]
    reporter: Reporter[TConversationId]

    async def report_topics_for_conversation(
        self, conversation_id: TConversationId
    ) -> None:
        messages = await self.messages.get_messages(conversation_id)
        topics = self.vote_counter.extract_topics(messages)
        await self.reporter.report_topics(topics, conversation_id)
