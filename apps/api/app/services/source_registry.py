from app.services.connectors.arsat import ArsatConnector
from app.services.connectors.boletin import BoletinOficialConnector
from app.services.connectors.chaco import ChacoConnector
from app.services.connectors.catamarca import CatamarcaConnector
from app.services.connectors.cordoba import CordobaConnector
from app.services.connectors.comprar import ComprarConnector
from app.services.connectors.contratar import ContratarConnector
from app.services.connectors.corrientes import CorrientesConnector
from app.services.connectors.entre_rios import EntreRiosConnector
from app.services.connectors.gcba import GcbaConnector
from app.services.connectors.inta import IntaConnector
from app.services.connectors.la_rioja import LaRiojaConnector
from app.services.connectors.mendoza import MendozaConnector
from app.services.connectors.neuquen import NeuquenConnector
from app.services.connectors.pami import PamiConnector
from app.services.connectors.pbac import PbacConnector
from app.services.connectors.rio_negro import RioNegroConnector
from app.services.connectors.salta import SaltaConnector
from app.services.connectors.san_juan import SanJuanConnector
from app.services.connectors.san_luis import SanLuisConnector
from app.services.connectors.santa_fe import SantaFeConnector
from app.services.connectors.tierra_del_fuego import TierraDelFuegoConnector
from app.services.connectors.tucuman import TucumanConnector

CONNECTORS = {
    "arsat": ArsatConnector,
    "comprar": ComprarConnector,
    "contratar": ContratarConnector,
    "licitaciones-caba": GcbaConnector,
    "licitaciones-corrientes": CorrientesConnector,
    "licitaciones-entre-rios": EntreRiosConnector,
    "inta": IntaConnector,
    "licitaciones-la-rioja": LaRiojaConnector,
    "boletin-oficial": BoletinOficialConnector,
    "licitaciones-catamarca": CatamarcaConnector,
    "licitaciones-chaco": ChacoConnector,
    "licitaciones-cordoba": CordobaConnector,
    "licitaciones-mendoza": MendozaConnector,
    "licitaciones-neuquen": NeuquenConnector,
    "pami": PamiConnector,
    "pbac": PbacConnector,
    "licitaciones-rio-negro": RioNegroConnector,
    "licitaciones-salta": SaltaConnector,
    "licitaciones-san-juan": SanJuanConnector,
    "licitaciones-san-luis": SanLuisConnector,
    "licitaciones-santa-fe": SantaFeConnector,
    "licitaciones-tierra-del-fuego": TierraDelFuegoConnector,
    "licitaciones-tucuman": TucumanConnector,
}

ALLOWED_CONNECTOR_SLUGS = frozenset(CONNECTORS.keys())
