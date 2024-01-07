import logging

from peak.util.proxies import ObjectWrapper

from dynascope import stack


class DynamicLogger(ObjectWrapper):

    def debug(self, *args, **kwargs):
        self.log(logging.DEBUG, *args, **kwargs)

    def info(self, *args, **kwargs):
        self.log(logging.INFO, *args, **kwargs)

    def warning(self, *args, **kwargs):
        self.log(logging.WARNING, *args, **kwargs)

    def error(self, *args, **kwargs):
        self.log(logging.ERROR, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        logging_threshold = self.getEffectiveLevel()
        if level < logging_threshold:
            if (escalation_level := getattr(stack, "log_escalate", None)) is not None:
                if logging_threshold <= escalation_level:
                    msg = f"{logging.getLevelName(level)} - {msg}"
                    self.__subject__.log(escalation_level, msg, *args, **kwargs)
        self.__subject__.log(level, msg, *args, **kwargs)
