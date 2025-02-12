import attrs

from chat_topics.slack_app import slack


@attrs.frozen
class Messages:
    async def get_messages(
        self, conversation_id: slack.Conversation
    ) -> tuple[slack.Message, ...]:
        return (
            slack.Message('This is a message', {'interesting': 1}),
            slack.Message('What is the goal of this?', {'psc': 2, 'this': 3}),
            slack.Message('Is this a thing?', {'ooo': 1, 'psc': 3}),
        )
