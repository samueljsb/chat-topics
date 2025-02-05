import fastapi

from . import conversations


def create_app() -> fastapi.FastAPI:
    app = fastapi.FastAPI(
        title='chat-topics',
        summary=None,
        version='',
        # Disable automatic documentation.
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
        swagger_ui_oauth2_redirect_url=None,
    )

    app.get('/conversations/')(conversations.list_conversations)

    return app
