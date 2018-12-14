# -*- coding: utf-8 -*-
import logging

from gwswlib.sql_models.model_schematisation import ConnectionNode, Manhole

# from gwswlib.sql_models.constants import Constants


logger = logging.getLogger(__name__)


class Threedi:
    def __init__(self):
        pass

    def __repr__(self):
        pass

    def import_hydx(self, hydx):
        connection_node = ConnectionNode()
        manhole = Manhole()
        print(connection_node, manhole)
        pass
