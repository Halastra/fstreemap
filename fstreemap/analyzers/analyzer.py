from abc import abstractmethod
from pathlib import Path
from typing import Mapping, Type
from tqdm import tqdm

from ..loggers import LoggingHandler


class IPathAnalysis(Mapping, LoggingHandler):

    @property
    @abstractmethod
    def name(self):
        pass

    def __init__(self, base_directory: Path, lazy: bool = True):
        super().__init__()

        self.logger.info("Initializing %s analysis for %s", self.name, base_directory)
        self.base_directory = base_directory

        # TODO: consider using pyfilesystem for filesystem recursion (e.g. inspecting files in zip archives)
        #  https://github.com/PyFilesystem/pyfilesystem2
        #  Maybe use MountFS? https://docs.pyfilesystem.org/en/latest/reference/mountfs.html
        #  - Create a dictionary to map file paths into mounted filesystems
        #  - That way you can track of which files are mounted archives, and optionally ignore them as files
        #  - Probably a good idea to put all of this logic as a filesystem using pyfilesystem's API
        #  Otherwise, dynamically mount/unmount with context manager
        self._keys = list(base_directory.glob('**/*'))
        self._mapping = dict()

    def run(self):
        """
        Evaluates all values in the analysis
        :return:
        """
        self.logger.info("Running %s analysis for %s", self.name, self.base_directory)
        for i in tqdm(sorted(self._keys, key=lambda p: len(p.parts), reverse=True)):
            self.get(i)

    @abstractmethod
    def calculate_file(self, file_path: Path) -> int:
        pass

    @abstractmethod
    def calculate_dir(self, dir_path: Path) -> int:
        pass

    def is_valid_path(self, query_path: Path) -> bool:
        # try:
        #     query_path.relative_to(self.base_directory)
        #     return True
        # except ValueError as e:
        #     return False
        return query_path in self._keys

    def calculate_path(self, query_path: Path) -> int:
        if not self.is_valid_path(query_path):
            raise KeyError("Requested path is not under base directory", query_path, self.base_directory)

        if query_path.is_file():
            return self.calculate_file(query_path)
        elif query_path.is_dir():
            return self.calculate_dir(query_path)
        else:
            raise ValueError("Unexpected path type", query_path)

    def __getitem__(self, key: Path):

        # Development note: why not use self._mapping.setdefault?
        # "Python is not a lazy language, as it requires all function arguments to be evaluated prior to the call."
        # More info: https://xion.org.pl/2012/01/28/pythons-setdefault-considered-harmful/

        try:
            val = self._mapping[key]
        except KeyError:
            self._mapping[key] = val = self.calculate_path(key)
        return val

    def __iter__(self):
        return iter(self._keys)

    def __len__(self):
        return len(self._keys)

    def __contains__(self, key):
        return key in self._keys

    def __repr__(self):
        return f"{type(self).__name__}({self._mapping})"


class IPathValueAnalysis(IPathAnalysis):
    """
    Calculates values.

    Files are calculated independently;
    Directories are calculated as the sum of the underlying items.
    """

    def calculate_dir(self, dir_path: Path) -> int:
        return sum(self[i] for i in dir_path.iterdir())

    @abstractmethod
    def calculate_file(self, file_path: Path) -> int:
        pass


class IPathPropertyAnalysis(IPathAnalysis):
    """
    Calculates properties.

    Files are calculated independently;
    Directories are calculated as a weighted average of the underlying items.
    """

    def __init__(self, base_directory: Path, value_analysis_class: Type[IPathValueAnalysis]):
        self.value_analysis = value_analysis_class(base_directory)

        super().__init__(base_directory)

        assert self.keys() == self.value_analysis.keys()

    def calculate_dir(self, dir_path: Path) -> float:
        if self.value_analysis[dir_path] == 0:
            return 0
        else:
            directory_properties = [
                self[i] * self.value_analysis[i]
                for i in dir_path.iterdir()
            ]
            return sum(directory_properties) / self.value_analysis[dir_path]

    @abstractmethod
    def calculate_file(self, file_path: Path) -> float:
        pass
