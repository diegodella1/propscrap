from app.services.connectors.boletin import BoletinOficialConnector
from app.services.connectors.comprar import ComprarConnector
from app.services.connectors.pbac import PbacConnector

CONNECTORS = {
    "comprar": ComprarConnector,
    "boletin-oficial": BoletinOficialConnector,
    "pbac": PbacConnector,
}
