import json
from pathlib import Path
from typing import Union, Dict, Any, List
from inspectus.utils import to_json

import numpy as np
from labml import monit, logger


class DataLogger:
    def __init__(self, path: Union[str, Path]):
        if isinstance(path, str):
            path = Path(path)
        path = path.absolute()
        self._path = path

        if not path.exists():
            with monit.section(f'Create {path}'):
                path.mkdir(parents=True)
        elif not path.is_dir():
            raise ValueError(f'Path {path} is not a directory')
        else:
            with monit.section(f'Using {path}'):
                pass

    def clear(self):
        for f in self._path.iterdir():
            if f.is_dir():
                raise RuntimeError(f'{f} is a folder')
            logger.log(f'Deleting {f}')
            f.unlink()

    def save(self, name: str, data: Dict[str, Any], step=-1):
        # NOTE: If it's already a histogram data = {'histogram': }
        data = to_json(data)
        if 'step' not in data:
            data['step'] = step
        with open(self._path / f'{name}.jsonl', "a") as f:
            f.write(json.dumps(data) + '\n')

    def read(self, name: str) -> List[dict]:
        with open(self._path / f'{name}.jsonl', "r") as f:
            return [json.loads(line) for line in f]

    def get_names(self) -> List[str]:
        return [p.stem for p in self._path.iterdir() if p.is_file()]

    def get_all(self) -> Dict[str, List[dict]]:
        return {name: self.read(name) for name in self.get_names()}
