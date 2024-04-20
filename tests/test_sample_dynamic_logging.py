import logging

from samples.dynamic_logging import dynalog
from samples.dynamic_logging import scope


logger = logging.getLogger(__name__)
dynalog(logger)  # Patch logger for dynamic filtering


def test_dynamic_logging(caplog):
    logger.setLevel(logging.ERROR)

    def api_endpoint():
        scope.log_level = logging.DEBUG  # Set log level for this call branch only
        service_function()

    def service_function():
        logger.debug("This message is only interesting for APIs")

    service_function()  # Debug message is not logged
    api_endpoint()  # Debug message is logged

    logger.debug("Not logged")
    logger.error("Logged normally")

    logs = caplog.text
    assert "Not logged" not in logs
    assert "Logged normally" in logs

    # We get the interesting log message only once, when the log call is made via the api_endpoint() that
    # sets a lower log level for that call branch.
    assert logs.count("This message is only interesting for APIs") == 1
