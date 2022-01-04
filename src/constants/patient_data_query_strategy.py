import enum
from typing import NamedTuple, Callable

from src.data_readers.patient_data.patient_data_factories import DefaultPatientDataFactory, \
    SegmentationPatientDataFactory, SeriesDescriptionPatientDataFactory, \
    SegmentationAndSeriesDescriptionPatientDataFactory


class PatientDataQueryStrategy(NamedTuple):
    name: str
    factory: Callable


class PatientDataQueryStrategies(PatientDataQueryStrategy, enum.Enum):

    DEFAULT: PatientDataQueryStrategy = PatientDataQueryStrategy(
        name="Default",
        factory=DefaultPatientDataFactory
    )

    SEGMENTATION: PatientDataQueryStrategy = PatientDataQueryStrategy(
        name="Segmentation",
        factory=SegmentationPatientDataFactory
    )

    SERIES_DESCRIPTION: PatientDataQueryStrategy = PatientDataQueryStrategy(
        name="Series description",
        factory=SeriesDescriptionPatientDataFactory
    )

    SEGMENTATION_AND_SERIES_DESCRIPTION: PatientDataQueryStrategy = PatientDataQueryStrategy(
        name="Segmentation and series description",
        factory=SegmentationAndSeriesDescriptionPatientDataFactory
    )
