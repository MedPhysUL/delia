import logging

from dicom2hdf.data_generators.patients_data_generator import PatientsDataGenerator, PatientWhoFailed
from dicom2hdf.data_model import PatientDataModel
from dicom2hdf.datasets.patients_dataset import PatientsDataset

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
logging.getLogger(__name__).addHandler(stream_handler)

__author__ = "Maxence Larose"
__version__ = "0.1.6"
__copyright__ = "Copyright 2022, Maxence Larose"
__credits__ = ["Maxence Larose"]
__license__ = "Apache License 2.0"
__maintainer__ = "Maxence Larose"
__email__ = "maxence.larose.1@ulaval.ca"
__status__ = "Production"
