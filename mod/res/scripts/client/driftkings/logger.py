# -*- coding: utf-8 -*-
"""Single logger factory; handlers and output remain owned by the game client."""
import logging
import os

NAMESPACE = 'Driftkings'


class LocationFilter(logging.Filter):
    """Identify every module; reserve source locations for warnings and errors."""
    driftkings_location = True

    def filter(self, record):
        if getattr(record, 'driftkings_formatted', False):
            return True
        module = record.name[len(NAMESPACE) + 1:] if record.name.startswith(NAMESPACE + '.') else ''
        prefix = '[%s][Driftkings]' % getattr(record, 'driftkings_levelname', record.levelname)
        if module:
            prefix += '[%s]' % module
        if record.levelno >= logging.WARNING:
            filename = getattr(record, 'driftkings_filename', record.filename)
            lineno = getattr(record, 'driftkings_lineno', record.lineno)
            if record.exc_info and record.exc_info[2] is not None:
                frame = record.exc_info[2]
                while frame.tb_next is not None:
                    frame = frame.tb_next
                filename = os.path.basename(frame.tb_frame.f_code.co_filename)
                lineno = frame.tb_lineno
            prefix += ' %s line %s:' % (filename, lineno)
        record.msg = prefix + ' ' + record.msg
        record.driftkings_formatted = True
        return True


def get_logger(name=NAMESPACE):
    """Accept a full channel or a short name within the Driftkings namespace."""
    if name != NAMESPACE and not name.startswith(NAMESPACE + '.'):
        name = NAMESPACE + '.' + name
    logger = logging.getLogger(name)
    if not any(getattr(item, 'driftkings_location', False) for item in logger.filters):
        logger.addFilter(LocationFilter())
    return logger
