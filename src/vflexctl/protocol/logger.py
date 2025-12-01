import structlog

__all__ = ["log"]

log = structlog.get_logger("vflexctl.protocol")
