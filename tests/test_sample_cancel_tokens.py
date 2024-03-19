import time

import pytest

from dynascope import dynamic
from dynascope import scope
from samples.cancel_tokens import CountdownToken
from samples.cancel_tokens import TimeoutToken
from samples.cancel_tokens import TokenException
from samples.cancel_tokens import TokenExhausted
from samples.cancel_tokens import TokenTimeout
from samples.cancel_tokens import add_to


def test_timeout_token():
    timeout_token = TimeoutToken(0.01)
    timeout_token.check()
    time.sleep(0.01)
    with pytest.raises(TokenTimeout):
        timeout_token.check()


def test_countdown_token():
    countdown_token = CountdownToken(1)
    countdown_token.check()
    with pytest.raises(TokenExhausted):
        countdown_token.check()


def test_combined_tokens():
    token = TimeoutToken(0.1)
    add_to(token, CountdownToken(1))
    token.check()
    with pytest.raises(TokenException):
        token.check()


def test_dynamic_tokens():

    token = dynamic(CountdownToken(3))

    with scope(token):
        add_to(token, CountdownToken(1))
        token.check()

        with pytest.raises(TokenExhausted):
            token.check()

    token.check()

    with pytest.raises(TokenExhausted):
        token.check()
