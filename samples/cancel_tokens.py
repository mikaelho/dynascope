import time
from dataclasses import dataclass
from dataclasses import field

from dynascope import Static
from dynascope.manager import transparent


class TokenException(Exception):
    pass


class TokenTimeout(TokenException):
    pass


class TokenExhausted(TokenException):
    pass


@dataclass
class BaseToken:

    tokens: list["BaseToken"] = field(default_factory=list)

    def _check_token(self):
        pass

    def check(self):
        raised = []

        try:
            self._check_token()
        except TokenException as e:
            e.token = self
            raised.append(e)

        for token in self.tokens:
            try:
                token._check_token()
            except TokenException as e:
                e.token = token
                raised.append(e)

        if raised:
            if len(raised) == 1:
                raise raised[0]
            else:
                raise ExceptionGroup(f"Raised from {self}", raised)


@dataclass
class TimeoutToken(BaseToken):
    def __init__(self, timeout_in_seconds: float):
        super().__init__()
        self.end_timestamp = Static(time.time() + timeout_in_seconds)

    def _check_token(self):
        if time.time() >= self.end_timestamp.value:
            raise TokenTimeout()


@dataclass
class CountdownToken(BaseToken):
    def __init__(self, countdown_starting_value: int):
        super().__init__()
        assert countdown_starting_value > 0
        self.countdown_remaining = Static(countdown_starting_value)

    def _check_token(self):
        if self.countdown_remaining.value == 0:
            raise TokenExhausted()
        self.countdown_remaining.value -= 1


@transparent
def add_to(token, *tokens):
    token.tokens.extend(tokens)
