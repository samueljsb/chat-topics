"""Test that a summary of topics can be posted to Slack when requested."""

import json
import os
import unittest.mock

import fastapi
import fastapi.testclient
import httpx
import pytest_httpx

from chat_topics.slack_app import app


def _post_slack_event(content: str) -> httpx.Response:
    web_client = fastapi.testclient.TestClient(app.create_app())

    with unittest.mock.patch.dict(
        os.environ, {'SLACK_AUTH_TOKEN': 'xxxx-xxxxxxxxx-xxxx'}
    ):
        return web_client.post('/events/', content=content)


def test_rejects_unexpected_event_types() -> None:
    """Unexpected events should cause an error."""
    response = _post_slack_event(
        """\
{
    "type": "reaction_added",
    "user": "U123ABC456",
    "reaction": "thumbsup",
    "item_user": "U222222222",
    "item": {
        "type": "message",
        "channel": "C123ABC456",
        "ts": "1360782400.498405"
    },
    "event_ts": "1360782804.083113"
}
"""
    )

    assert response.status_code == 422


def test_does_nothing_when_not_triggered(
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """If not triggered by the command phrase, the app should do nothing."""
    response = _post_slack_event("""\
{
        "type": "message",
        "message": {
                "type": "message",
                "user": "U123ABC456",
                "text": "To discuss later: what do we thing about things?",
                "thread_ts": "1482960137.003543",
                "ts": "1482960137.003543"
        },
        "subtype": "message_replied",
        "hidden": true,
        "channel": "C123ABC456",
        "event_ts": "1483037604.017506",
        "ts": "1483037604.017506"
}
""")

    assert response.status_code == 200

    assert httpx_mock.get_requests() == []


def test_posts_report_when_triggered(
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """The app should be triggered by the command phrase "topics plz".

    The app should fetch the messages in the thread and post a summary of the
    topics to the same thread.
    """
    httpx_mock.add_response(  # get messages
        url='https://slack.com/api/conversations.replies?channel=C123ABC456&ts=1482960137.003543',
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
                },
                {
                    "name": "psc",
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
    httpx_mock.add_response(  # post a message
        url='https://slack.com/api/chat.postMessage',
        method='post',
        match_headers={'Authorization': 'Bearer xxxx-xxxxxxxxx-xxxx'},
    )

    response = _post_slack_event("""\
{
        "type": "message",
        "message": {
                "type": "message",
                "user": "U123ABC456",
                "text": "topics plz",
                "thread_ts": "1482960137.003543",
                "ts": "1482960137.003543"
        },
        "subtype": "message_replied",
        "hidden": true,
        "channel": "C123ABC456",
        "event_ts": "1483037604.017506",
        "ts": "1483037604.017506"
}
""")

    assert response.status_code == 200

    [post_request] = httpx_mock.get_requests(
        url='https://slack.com/api/chat.postMessage',
        method='post',
    )
    assert post_request.headers['content-type'] == 'application/json'
    assert json.loads(post_request.content.decode()) == {
        'channel': 'C123ABC456',
        'thread_ts': '1482960137.003543',
        'markdown_text': """\
Topics to discuss:

1. Another message (2 votes)
""",
    }
