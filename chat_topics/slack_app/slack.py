import attrs


@attrs.frozen
class Conversation:
    channel_id: str
    timestamp: str


@attrs.frozen
class Message:
    text: str
    reactions: dict[str, int]
