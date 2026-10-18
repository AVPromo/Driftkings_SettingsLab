# -*- coding: utf-8 -*-
"""Public updater API; implementations live in responsibility-specific modules."""
import logging
import os
import time
import threading
from Driftkings import VERSION
from Driftkings.core.updater.checker import Checker
from Driftkings.core.updater.state import State, IDLE, CHECKING, AVAILABLE, ERROR, DOWNLOADING, VERIFYING, READY, INSTALLING, RESTART_REQUIRED
from Driftkings.core.updater.transport import UnavailableTransport
from Driftkings.core.updater.downloader import Downloader
from Driftkings.core.updater.shared import LOG, INTERVAL
from Driftkings.core.updater.service import UpdaterService
