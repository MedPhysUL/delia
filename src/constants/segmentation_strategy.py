import enum
from typing import NamedTuple, Callable

from src.data_readers.segmentation.nrrd.label_map_volume_factory import LabelMapVolumeFactory
from src.data_readers.segmentation.nrrd.segmentation_label_map_representation_factory import \
    SegmentationLabelMapRepresentationFactory


class SegmentationStrategy(NamedTuple):
    name: str
    file_extension: str
    factory: Callable


class SegmentationStrategies(SegmentationStrategy, enum.Enum):

    LABEL_MAP_VOLUME: SegmentationStrategy = SegmentationStrategy(
        name="label_map_volume",
        file_extension=".nrrd",
        factory=LabelMapVolumeFactory
    )

    SEGMENTATION_LABEL_MAP_REPRESENTATION: SegmentationStrategy = SegmentationStrategy(
        name="segmentation_label_map_representation",
        file_extension=".seg.nrrd",
        factory=SegmentationLabelMapRepresentationFactory
    )
