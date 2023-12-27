import logging

from .databases import PatientsDatabase
from .extractors import PatientsDataExtractor, PatientWhoFailed
from .utils import PatientDataModel

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
logging.getLogger(__name__).addHandler(stream_handler)

__author__ = "Maxence Larose"
__version__ = "1.2.7"
__copyright__ = "Copyright 2022, Maxence Larose"
__credits__ = ["Maxence Larose"]
__license__ = "Apache License 2.0"
__maintainer__ = "Maxence Larose"
__email__ = "maxence.larose.1@ulaval.ca"
__status__ = "Production"
