"Defines utilities for adjusting the logging level for a specific branch of function calls."

from dynascope import scope


def dynalog(logger):
    "Patch the regular logger to support overriding the log level for the current call branch."
    original_isEnabledFor = logger.isEnabledFor

    def dynamic_isEnabledFor(level):
        if (log_level := getattr(scope, "log_level", None)) is not None:
            return log_level <= level
        else:
            return original_isEnabledFor(level)

    setattr(logger, "isEnabledFor", dynamic_isEnabledFor)
    return logger
