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
from samples.cancel_tokens import check_tokens
from samples.cancel_tokens import tokens


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
    add_to(tokens, CountdownToken(3))

    with scope(tokens):
        add_to(tokens, CountdownToken(1))
        tokens.check()

        with pytest.raises(TokenExhausted):
            tokens.check()

    tokens.check()

    with pytest.raises(TokenExhausted):
        tokens.check()


def test_check_decorator():

    # Set up sample intensive retry operation

    call_counter = 0  # Used to check results, not for cancelling

    @check_tokens
    def repeatedly_called_function():
        """Does something that may need to be repeated"""
        nonlocal call_counter
        call_counter += 1

    def driver():
        """Simulates retry handler or similar with infinite loop"""
        while True:
            repeatedly_called_function()

    # Configure retry count external to the operation
    with scope(tokens):
        add_to(tokens, CountdownToken(3))

        with pytest.raises(TokenExhausted):
            driver()

    assert call_counter == 3
    call_counter = 0

    # Configure time-based cancellation instead
    with scope(tokens):
        add_to(tokens, TimeoutToken(0.05))

        with pytest.raises(TokenTimeout):
            driver()

    assert call_counter > 0
    call_counter = 0

    # Configure multiple cancellation criteria
    with scope(tokens):
        add_to(tokens, TimeoutToken(1000))
        add_to(tokens, CountdownToken(2))

        with pytest.raises(TokenException):
            driver()

    assert call_counter == 2
