from typing import Protocol

import attrs
import httpx


class Conversation(Protocol):
    @property
    def channel_id(self) -> str: ...

    @property
    def timestamp(self) -> str: ...


@attrs.frozen
class Message:
    text: str
    reactions: dict[str, int]


@attrs.frozen
class SlackClient:
    auth_token: str

    def _get_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url='https://slack.com/api/',
            headers={'Authorization': f'Bearer {self.auth_token}'},
        )

    async def get_messages(
        self, conversation: Conversation
    ) -> tuple[Message, ...]:
        async with self._get_client() as client:
            response = await client.get(
                '/conversations.replies',
                params={
                    'channel': conversation.channel_id,
                    'ts': conversation.timestamp,
                },
            )

        data = response.json()

        return tuple(
            Message(
                message['text'],
                reactions={
                    reaction['name']: reaction['count']
                    for reaction in message.get('reactions', [])
                },
            )
            for message in data['messages']
        )

    async def send_message(
        self, message: str, conversation: Conversation
    ) -> None:
        async with self._get_client() as client:
            await client.post(
                '/chat.postMessage',
                json={
                    'channel': conversation.channel_id,
                    'thread_ts': conversation.timestamp,
                    'markdown_text': message,
                },
            )
