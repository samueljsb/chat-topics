"""Tests that a summary of topics can be posted to Slack when requested."""

import os
import unittest.mock

import pytest
import pytest_httpx
from fastapi.testclient import TestClient

from chat_topics.slack_app import app


def test_does_nothing_when_not_triggered(
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """If not triggered, the app should do nothing."""
    web_client = TestClient(app.create_app())

    event = """\
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
"""

    with unittest.mock.patch.dict(
        os.environ, {'SLACK_AUTH_TOKEN': 'xxxx-xxxxxxxxx-xxxx'}
    ):
        response = web_client.post('/events/', content=event)

    assert response.status_code == 200

    assert httpx_mock.get_requests() == []


@pytest.mark.xfail
def test_posts_report_when_triggered(
    httpx_mock: pytest_httpx.HTTPXMock,
) -> None:
    """The app should be triggered by the trigger phrase "topics plz".

    The app should fetch the messages in the thread and post a summary of the
    topics to the same thread.
    """
    httpx_mock.add_response(url='...')  # get messages
    httpx_mock.add_response(url='...')  # post a message

    web_client = TestClient(app.create_app())

    event = """\
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
"""

    with unittest.mock.patch.dict(
        os.environ, {'SLACK_AUTH_TOKEN': 'xxxx-xxxxxxxxx-xxxx'}
    ):
        response = web_client.post('/events/', content=event)

    assert response.status_code == 200

    post_request = httpx_mock.get_request(url='...', method='post')
    assert post_request is not None
    assert (
        post_request.content
        == """\
"""
    )
