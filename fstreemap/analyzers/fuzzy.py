"""
Duplicate calculations, based on fuzzy hashes
https://github.com/MacDue/ssdeep-windows-32_64


"""

from pathlib import Path
from hashlib import sha256
from typing import Type, Mapping

from tqdm import tqdm

from .analyzer import IPathPropertyAnalysis, IPathValueAnalysis
from . import register_analysis


class FuzzyDuplicateFinder(IPathPropertyAnalysis):

    @classmethod
    def ticks(cls) -> Mapping[float, str]:
        return {
            0.0: 'Unique',
            1.0: 'Redundant'
        }

    name = 'fuzzy'

    def __init__(self, base_directory: Path, value_analyzer: Type[IPathValueAnalysis]):

        super().__init__(base_directory, value_analyzer)

        self.collision_dict = self.calculate_collisions()

    def calculate_collisions(self):

        paths = self.keys()

        self.logger.info("Calculating file hashes (the most intensive operation):")

        # This is the most intensive operation:
        hash_dict = {
            i: sha256(i.read_bytes()).digest()
            for i in tqdm(paths)
            if i.is_file()
        }

        # TODO: This essentially cuts away the hash values.
        #  Hash values may be needed if/when we support file-system updates
        hash_reverse_dict = dict()
        for file_path, hash_value in hash_dict.items():
            hash_reverse_dict.setdefault(hash_value, []).append(file_path)

        collision_dict = dict()
        for file_path, hash_value in hash_dict.items():
            collision_dict[file_path] = hash_reverse_dict[hash_value]

        return collision_dict

    def calculate_file(self, file_path: Path) -> float:
        return 1 if len(self.collision_dict[file_path]) > 1 else 0


# register_analysis(FuzzyDuplicateFinder)
