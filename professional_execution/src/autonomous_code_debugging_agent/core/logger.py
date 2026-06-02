from __future__ import annotations

import logging


# Return the requested value or object from the current state.
def get_logger(name: str = "autonomous-code-debugging-agent") -> logging.Logger:
    # Create a simple logger that writes to the console for debugging output.
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
