import attrs
import httpx

from chat_topics.slack_app import slack


@attrs.frozen
class SlackClient:
    auth_token: str

    async def get_messages(
        self, conversation_id: slack.Conversation
    ) -> tuple[slack.Message, ...]:
        response = httpx.get(
            'https://slack.com/api/conversations.replies',
            headers={
                'Authorization': f'Bearer {self.auth_token}',
            },
            params={
                'channel': conversation_id.channel_id,
                'ts': conversation_id.timestamp,
            },
            # TODO: timeout
        )

        data = response.json()
        assert data['ok'] is True

        return tuple(
            slack.Message(
                message['text'],
                reactions={
                    reaction['name']: reaction['count']
                    for reaction in message.get('reactions', [])
                },
            )
            for message in data['messages']
        )

    async def send_message(
        self, message: str, conversation_id: slack.Conversation
    ) -> None:
        httpx.post(
            'https://slack.com/api/chat.postMessage',
            headers={
                'Authorization': f'Bearer {self.auth_token}',
            },
            params={
                'channel': conversation_id.channel_id,
                'thread_ts': conversation_id.timestamp,
                'text': message,
            },
        )
