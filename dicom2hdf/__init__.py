import logging

from .databases import PatientsDatabase
from .generators import PatientsDataGenerator, PatientWhoFailed
from .radiomics import RadiomicsDataset, RadiomicsFeatureExtractor
from .utils import PatientDataModel

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
logging.getLogger(__name__).addHandler(stream_handler)

__author__ = "Maxence Larose"
__version__ = "0.3.0"
__copyright__ = "Copyright 2022, Maxence Larose"
__credits__ = ["Maxence Larose"]
__license__ = "Apache License 2.0"
__maintainer__ = "Maxence Larose"
__email__ = "maxence.larose.1@ulaval.ca"
__status__ = "Production"
