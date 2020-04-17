"""
Entropy calculations
"""

import math
import zlib
from collections import Counter
from pathlib import Path

from .analyzer import IPathPropertyAnalysis
from . import register_analysis


class EntropyCalculator(IPathPropertyAnalysis):

    name = 'entropy'

    @staticmethod
    def entropy_estimate(data: bytes) -> float:
        """
        Heuristic for estimating entropy based on zlib compression ratio
        """
        data_len = len(data)
        if data_len == 0:
            return 0
        if data_len < 0x100:
            return len(set(data)) / data_len
        return min(len(zlib.compress(data)) / data_len, 1.0)

    @staticmethod
    def entropy_math(data, unit='shannon') -> float:
        """
        Actual mathematical calculation of entropy
        """
        base = {
            'shannon': 2.,
            'natural': math.exp(1),
            'hartley': 10.
        }

        if len(data) <= 1:
            return 0

        counts = Counter()

        for d in data:
            counts[d] += 1

        ent = 0

        probs = [float(c) / len(data) for c in counts.values()]
        for p in probs:
            if p > 0.:
                ent -= p * math.log(p, base[unit])

        return ent / 8

    def calculate_file(self, file_path: Path) -> float:
        return self.entropy_estimate(file_path.read_bytes())


register_analysis(EntropyCalculator)
