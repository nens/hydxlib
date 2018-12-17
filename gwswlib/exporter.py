# -*- coding: utf-8 -*-
import logging

from gwswlib.threedi import Threedi

logger = logging.getLogger(__name__)


def export_hydx(hydxdict, csvfile):
    pass


def export_threedi(hydx):
    threedi = Threedi()
    threedi.import_hydx(hydx)
