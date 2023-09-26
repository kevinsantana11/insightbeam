from typing import Any, Callable, Dict, Union


class DependencyManager:
    _deps: Dict

    def __init__(self):
        self._deps = dict()

    def register(self, instance: object, named: Union[str, None] = None):
        if named is None:
            self._deps[type(instance).__name__] = instance
        else:
            self._deps[named] = instance

    def inject(self, class_: type) -> Callable[[], Any]:
        return lambda: self._deps[class_.__name__]


manager = DependencyManager()
