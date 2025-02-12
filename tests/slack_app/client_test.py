import pytest
import pytest_httpx

from chat_topics.slack_app import client
from chat_topics.slack_app import slack


@pytest.mark.asyncio
class TestGetMessages:
    # Currently assume everything works.
    # TODO: error handling

    async def test_get_messages(
        self,
        httpx_mock: pytest_httpx.HTTPXMock,
    ) -> None:
        httpx_mock.add_response(
            url='https://slack.com/api/conversations.replies?channel=C1234567890&ts=1234567890.123456',
            method='get',
            match_headers={'Authorization': 'Bearer xxxx-xxxxxxxxx-xxxx'},
            # this is not a full response -- minimal data needed for this test
            text="""\
{
    "ok": true,
    "messages": [
        {
            "user": "USLACKBOT",
            "channel": "C1234567890",
            "subtype": "huddle_thread",
            "type": "message",
            "ts": "1234567890.123456",
            "text": "",
            "thread_ts": "1234567890.123456"
        },
        {
            "user": "U1234AB56CD",
            "type": "message",
            "ts": "2345678901.234567",
            "text": "Some message",
            "thread_ts": "1234567890.123456"
        },
        {
            "user": "U1234AB56CD",
            "type": "message",
            "ts": "2345678901.234568",
            "text": "Another message",
            "thread_ts": "1234567890.123456",
            "reactions": [
                {
                    "name": "+1",
                    "users": [
                        "U2345BC78DE"
                    ],
                    "count": 1
                }
            ]
        }
    ],
    "has_more": false
}
""",
        )

        client_ = client.SlackClient(auth_token='xxxx-xxxxxxxxx-xxxx')

        messages = await client_.get_messages(
            slack.Conversation('C1234567890', '1234567890.123456')
        )

        assert messages == (
            slack.Message('', {}),
            slack.Message('Some message', {}),
            slack.Message('Another message', {'+1': 1}),
        )
