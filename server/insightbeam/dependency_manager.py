from typing import Any, Callable, Dict, Generator, Union


class DependencyManager:
    _deps: Dict

    def __init__(self):
        self._deps = dict()

    def register(
        self,
        instance: Union[object, type],
        named: Union[str, None] = None,
        supplier: Union[Callable[[], Any], None] = None,
    ):
        supplier_func = supplier or (lambda: instance)
        if named is None and isinstance(instance, type):
            type_: type = instance
            self._deps[type_.__name__] = supplier_func
        elif named is None:
            self._deps[type(instance).__name__] = supplier_func
        else:
            self._deps[named] = supplier_func

    def inject(self, class_: type) -> Callable[[], Any]:
        def injector(class_name: str):
            instance = self._deps[class_name]()

            if isinstance(instance, Generator):
                return next(instance)
            else:
                return instance

        return lambda: injector(class_.__name__)


manager = DependencyManager()
