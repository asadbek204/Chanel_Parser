from datetime import datetime
from aiofiles import open as async_open
from config import LOGS_PATH
from pprint import pformat
import typing
import os


async def save_logs(err: Exception):
    traceback = err.__traceback__
    traceback_tree = ''
    cur = traceback.tb_next
    while cur is not None:
        traceback_tree += f'\t\tin line: {cur.tb_lineno}: {pformat(cur.tb_frame)}\t{traceback.tb_lasti}\n'
        cur = cur.tb_next
    err = f"{datetime.now().time()}\t{err.__class__.__name__}: \n{pformat(err.__dict__)}\n\ttraceback:\n{traceback_tree} \t{err}\n\n"
    open_type: typing.Literal["a", "x"] = 'a'
    if not os.path.exists(LOGS_PATH):
        open_type = 'x'
    async with async_open(LOGS_PATH, mode=open_type) as err_file:
        await err_file.write(err)
