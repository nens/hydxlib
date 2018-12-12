# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


class Hydx:
    def __init__(self):
        self.connection_nodes = []


class ConnectionNode:
    CSVHEADERS = ["UNI_IDE", "RST_IDE"]
    FIELDS = [
        {
            "csvheader": "UNI_IDE",
            "fieldname": "IdentificatieKnooppuntOfVerbinding",
            "unit": "-",
            "type": (str, 10),
            "required": True,
        }
    ]

    @classmethod
    def csvheaders(cls):
        return [field["csvheader"] for fields in cls.FIELDS]

    def __init__(self, codes):
        self.uni_ide = uni_ide

    def check(self):
        pass


class Connection:
    pass


class Structure:
    pass


class Meta:
    pass
