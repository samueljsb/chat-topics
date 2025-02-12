from collections.abc import Collection

import attrs

from chat_topics.services import topics as topics_
from chat_topics.slack_app import slack


@attrs.frozen
class VoteCounter:
    topic_markers: frozenset[str]
    vote_reactions: frozenset[str]

    def extract_topics(
        self, messages: Collection[slack.Message]
    ) -> tuple[topics_.Topic, ...]:
        topics = []

        for message in messages:
            if self.is_topic(message) or self.has_votes(message):
                topics.append(self.to_topic(message))

        return tuple(topics)

    def is_topic(self, message: slack.Message) -> bool:
        return any(
            message.text.startswith(marker) for marker in self.topic_markers
        )

    def has_votes(self, message: slack.Message) -> bool:
        return any(
            reaction in self.vote_reactions for reaction in message.reactions
        )

    def to_topic(self, message: slack.Message) -> topics_.Topic:
        return topics_.Topic(
            message.text,
            sum(
                count
                for reaction, count in message.reactions.items()
                if reaction in self.vote_reactions
            )
            + 1,
        )
