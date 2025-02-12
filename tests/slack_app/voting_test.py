from chat_topics.services import topics as topics_
from chat_topics.slack_app import slack
from chat_topics.slack_app import voting


class TestVoteCounter:
    def test_no_messages_produces_no_topics(self) -> None:
        counter = voting.VoteCounter(
            topic_markers=frozenset(),
            vote_reactions=frozenset(),
        )

        topics = counter.extract_topics([])

        assert topics == ()

    def test_message_without_trigger_word_is_not_topic(self) -> None:
        counter = voting.VoteCounter(
            topic_markers=frozenset(),
            vote_reactions=frozenset(),
        )
        messages = [
            slack.Message('What are we reading today?', {}),
        ]

        topics = counter.extract_topics(messages)

        assert topics == ()

    def test_message_with_trigger_word_in_title_is_topic_with_one_vote(
        self,
    ) -> None:
        counter = voting.VoteCounter(
            topic_markers=frozenset({'PSC'}),
            vote_reactions=frozenset(),
        )
        messages = [
            slack.Message('PSC: What are we reading today?', {}),
        ]

        topics = counter.extract_topics(messages)

        assert topics == (
            topics_.Topic('PSC: What are we reading today?', votes=1),
        )

    def test_message_with_votes_is_topic(self) -> None:
        counter = voting.VoteCounter(
            topic_markers=frozenset(),
            vote_reactions=frozenset({'psc'}),
        )
        messages = [
            slack.Message('What are we reading today?', {'psc': 1}),
        ]

        topics = counter.extract_topics(messages)

        assert topics == (
            topics_.Topic('What are we reading today?', votes=2),
        )
