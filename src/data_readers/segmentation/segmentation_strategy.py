import enum
from typing import NamedTuple, Callable

from .factories.nrrd_segmentation_factories import NrrdLabelMapVolumeFactory, \
    NrrdSegmentationLabelMapRepresentationFactory


class SegmentationStrategy(NamedTuple):
    name: str
    file_extension: str
    factory: Callable


class SegmentationStrategies(SegmentationStrategy, enum.Enum):

    LABEL_MAP_VOLUME: SegmentationStrategy = SegmentationStrategy(
        name="label_map_volume",
        file_extension=".nrrd",
        factory=NrrdLabelMapVolumeFactory
    )

    SEGMENTATION_LABEL_MAP_REPRESENTATION: SegmentationStrategy = SegmentationStrategy(
        name="segmentation_label_map_representation",
        file_extension=".seg.nrrd",
        factory=NrrdSegmentationLabelMapRepresentationFactory
    )
