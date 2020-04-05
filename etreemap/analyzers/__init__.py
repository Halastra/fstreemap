
from .duplicates import DuplicateFinder
from .entropy import EntropyCalculator
from .filesize import FileSizeAnalyzer

ANALYSES = {
    i.name: i
    for i in [
        EntropyCalculator,
        DuplicateFinder,
        FileSizeAnalyzer
    ]
}
