import logging
import os

from utils import utils

format_str = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
ai_str = "%(taskid)s - %(message)s"


class CustomLogger(logging.Logger):

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        from rq import get_current_job
        from rq.job import Job
        job: Job = get_current_job()
        if extra is None:
            extra = {}
        if "taskid" not in extra:
            task_id = None if job is None else job.id
            extra["taskid"] = task_id
        super(CustomLogger, self)._log(level, msg, args, exc_info, extra, stack_info)


def setup_logger():
    logging.setLoggerClass(CustomLogger)
    _logger = logging.getLogger()

    _logger.setLevel(logging.DEBUG)
    # Stdout handler
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG)
    c_handler.setFormatter(logging.Formatter(format_str))
    _logger.addHandler(c_handler)

    # Application insight handler
    if utils.convert_to_boolean(os.environ["AZURE_USEAPPINSIGHT"]):
        from applicationinsights import TelemetryClient
        from applicationinsights.logging import LoggingHandler
        a_handler = LoggingHandler(os.environ["AZURE_INSTRUMENTATION_KEY"])
        a_handler.setLevel(logging.DEBUG)
        a_handler.setFormatter(logging.Formatter(ai_str))
        _logger.addHandler(a_handler)
        tc = TelemetryClient(os.environ["AZURE_INSTRUMENTATION_KEY"])
        tc.channel.queue.max_queue_length = 2
