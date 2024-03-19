import logging

from dynascope import stack
from samples.dynamic_logging import DynamicLogger


logger = DynamicLogger(logging.getLogger(__name__))


def test_dynamic_logging(caplog):
    logger.setLevel(logging.ERROR)

    def api_endpoint():
        stack.log_escalate = logging.ERROR
        stack.transaction_id = 123

        service_function()

    def internal_call():
        service_function()

    def service_function():
        logger.debug("Logged only when called from the call path of interest")

    logger.debug("Not logged")
    logger.error("Logged normally")

    internal_call()
    api_endpoint()

    logs = caplog.text

    assert "Not logged" not in logs
    assert "Logged normally" in logs
    assert logs.count("DEBUG - Logged only when called from the call path of interest (#123)") == 1
