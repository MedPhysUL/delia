import enum
from typing import NamedTuple, Callable

from src.data_readers.patient_data.patient_data_factories import DefaultPatientDataFactory, \
    SegmentationPatientDataFactory, SeriesDescriptionPatientDataFactory, \
    SegmentationAndSeriesDescriptionPatientDataFactory


class PatientDataStrategy(NamedTuple):
    name: str
    factory: Callable


class PatientDataStrategies(PatientDataStrategy, enum.Enum):

    DEFAULT: PatientDataStrategy = PatientDataStrategy(
        name="Default",
        factory=DefaultPatientDataFactory
    )

    SEGMENTATION: PatientDataStrategy = PatientDataStrategy(
        name="Segmentation",
        factory=SegmentationPatientDataFactory
    )

    SERIES_DESCRIPTION: PatientDataStrategy = PatientDataStrategy(
        name="Series description",
        factory=SeriesDescriptionPatientDataFactory
    )

    SEGMENTATION_AND_SERIES_DESCRIPTION: PatientDataStrategy = PatientDataStrategy(
        name="Segmentation and series description",
        factory=SegmentationAndSeriesDescriptionPatientDataFactory
    )
