"""Logging setup"""

import daiquiri


def setup_logging(level: str = "INFO", log_file: str = None):
    """
    Set up global Daiquiri logging for the application.

    Configures logging to output to the console (with color formatting) and optionally to a file.
    Should be called once at application startup (e.g., in main.py or CLI entry point).

    :param level: Logging level to use (e.g., "DEBUG", "INFO", "WARNING", "ERROR").
    :param log_file: If provided, log output will also be written to this file.
    """
    outputs = [daiquiri.output.Stream(formatter=daiquiri.formatter.ColorFormatter())]
    if log_file:
        outputs.append(
            daiquiri.output.File(log_file, formatter=daiquiri.formatter.TextFormatter())
        )
    daiquiri.setup(level=level, outputs=tuple(outputs))
