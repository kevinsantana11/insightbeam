import json
import os
from typing import Any, Callable, Dict, Sequence, Type, Union

from insightbeam.config import Configuration
from insightbeam.dal.schemas import JsonTable


class JsonFileDatabase:
    _base_path: str
    _db: Dict[str, Dict]

    def __init__(self, cfg: Configuration):
        self._base_path = cfg.db_dir
        self._db = dict()

    def store(self, table_name: str):
        table_path = f"{self._base_path}/{table_name}.json"
        with open(table_path, "w") as table_file:
            table_file.write(json.dumps(self._db.get(table_name)))

    def store_all(self):
        [self.store(table_name) for table_name in self._db.keys()]

    def load(self, table: Type[JsonTable], force: bool = False):
        table_name = table.table_name()

        if table_name in self._db.keys() and not force:
            return

        table_path = f"{self._base_path}/{table_name}.json"
        if os.path.exists(table_path):
            with open(table_path, "r") as table_file:
                self._db[table_name] = json.loads(table_file.read())
        elif not os.path.exists(table_path):
            self._db[table_name] = dict()

    def save(self, record: JsonTable):
        obj: Dict = json.loads(record.model_dump_json())
        self._db[record.table_name()][obj.get("uuid")] = obj

    def save_all(self, records: Sequence[JsonTable]):
        [self.save(record) for record in records]

    def get(self, class_: Type[JsonTable], uuid: str):
        table = self._db.get(class_.table_name(), {})
        return class_(**table.get(uuid))

    def get_all(
        self,
        class_: Type[JsonTable],
        filter_: Union[Callable[[Dict], Any], None] = None,
    ):
        if filter_ is None:
            return [class_(**obj) for obj in self._db[class_.table_name()].values()]
        else:
            return [
                class_(**obj)
                for obj in filter(filter_, self._db[class_.table_name()].values())
            ]
