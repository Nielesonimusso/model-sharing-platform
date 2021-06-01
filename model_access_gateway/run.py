from concurrent.futures.thread import ThreadPoolExecutor
import os
from typing import Any, Callable, Optional, Tuple, TypeVar
from flask.globals import _app_ctx_stack
from concurrent.futures import Future


from .src import create_app
class ContextThreadPoolExecutor(ThreadPoolExecutor):

    def __init__(self, max_workers: Optional[int] = None, thread_name_prefix: str = '', 
            initializer: Optional[Callable[..., None]] = None, initargs: Tuple[Any, ...] = ()) -> None:
        super().__init__(max_workers, thread_name_prefix, initializer, initargs)

    def __wrap(self, fn):
        app_context = _app_ctx_stack.top

        def wrapper(*args, **kwargs):
            with app_context:
                return fn(*args, **kwargs)

        return wrapper

    def submit(self, fn: Callable, *args: Any, **kwargs: Any) -> Future:
        return super().submit(self.__wrap(fn), *args, **kwargs)


def shared_scheduler() -> ContextThreadPoolExecutor:
    global __TPE
    if '__TPE' not in globals():
        __TPE = ContextThreadPoolExecutor()
    return __TPE

def run_gateway():
    app = create_app()
    with shared_scheduler():
        app.run(host=os.getenv('FLASK_RUN_HOST', '0.0.0.0'), port=int(os.getenv('FLASK_RUN_PORT', '5001')))
