import logging

from dicom2hdf.data_generators.patient_data_generator import PatientDataGenerator
from dicom2hdf.datasets.patient_dataset import PatientDataset

logging.getLogger(__name__).addHandler(logging.NullHandler())

__author__ = "Maxence Larose"
__version__ = "0.1.6"
__copyright__ = "Copyright 2022, Maxence Larose"
__credits__ = ["Maxence Larose"]
__license__ = "Apache License 2.0"
__maintainer__ = "Maxence Larose"
__email__ = "maxence.larose.1@ulaval.ca"
__status__ = "Production"
