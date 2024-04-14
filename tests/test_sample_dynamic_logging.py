import logging

from samples.dynamic_logging import dynalog
from samples.dynamic_logging import set_dynamic_level


logger = logging.getLogger(__name__)
dynalog(logger)  # Patch logger for dynamic filtering


def test_dynamic_logging(caplog):
    logger.setLevel(logging.ERROR)

    def api_endpoint():
        set_dynamic_level(logging.DEBUG)
        service_function()

    def internal_call():
        service_function()

    def service_function():
        logger.debug("Logged only when debug is called in the relevant call branch")

    internal_call()  # Debug message is not logged
    api_endpoint()  # Debug message is logged

    logger.debug("Not logged")
    logger.error("Logged normally")

    logs = caplog.text
    assert "Not logged" not in logs
    assert "Logged normally" in logs

    # We get the interesting log message only once, when the log call is made via the api_endpoint() that
    # sets a lower log level for that call branch.
    assert logs.count("Logged only when debug is called in the relevant call branch") == 1
