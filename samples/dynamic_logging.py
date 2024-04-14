"Defines utilities for adjusting the logging level for a specific branch of function calls."

from dynascope import stack
from dynascope.manager import transparent


def dynalog(logger):
    "Patch the regular logger to support overriding with a temporary log level for the call branch."
    original_IsEnabledFor = logger.isEnabledFor

    def adjusted_IsEnabledFor(level):
        if (temporary_log_level := getattr(stack, "temporary_log_level", None)) is not None:
            return temporary_log_level <= level
        else:
            return original_IsEnabledFor(level)

    setattr(logger, "isEnabledFor", adjusted_IsEnabledFor)
    return logger


@transparent
def set_dynamic_level(level: int):
    "Set the log level for the branch of function calls."
    stack.temporary_log_level = level
