"""
File size calculations
"""

from pathlib import Path

from .analyzer import IPathValueAnalysis
from . import register_analysis


class FileSizeAnalyzer(IPathValueAnalysis):

    name = 'size'

    @classmethod
    def calculate_file(cls, file_path: Path) -> int:
        return file_path.stat().st_size


register_analysis(FileSizeAnalyzer)
