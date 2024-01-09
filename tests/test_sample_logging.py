import logging

from dynascope import stack
from samples.dynamic_logging import DynamicLogger


logger = DynamicLogger(logging.getLogger(__name__))


def test_dynamic_logging(caplog):
    logger.setLevel(logging.ERROR)

    def path_of_interest():
        stack.log_escalate = logging.ERROR
        function_of_interest()

    def other_call_paths():
        function_of_interest()

    def function_of_interest():
        logger.debug("Logged only when called from the call path of interest")

    logger.debug("Not logged")
    logger.error("Logged normally")

    path_of_interest()
    other_call_paths()

    logs = caplog.text

    assert "Not logged" not in logs
    assert "Logged normally" in logs
    assert logs.count("DEBUG - Logged only when called from the call path of interest") == 1
