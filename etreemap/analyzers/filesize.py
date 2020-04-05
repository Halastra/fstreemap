"""
File size calculations
"""

from pathlib import Path

from .analyzer import IPathValueAnalysis


class FileSizeAnalyzer(IPathValueAnalysis):

    @property
    def name(self):
        return 'size'

    @classmethod
    def calculate_file(cls, file_path: Path) -> int:
        return file_path.stat().st_size
