import asyncio
from pathlib import Path

from src.celery.db import update_db
from src.celery.excel_parser import parse_wb
from src.celery.run import celery_app


@celery_app.task
def excel_parse_task():
    print('*' * 30, 'running', '*' * 30)
    if not Path('admin').is_dir():
        return

    if not Path('admin/Menu.xlsx').is_file():
        return

    menus, submenus, dishes = parse_wb()

    asyncio.get_event_loop().run_until_complete(update_db(menus, submenus, dishes))
    # clear redis cache
