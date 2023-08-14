class Config:
    broker_connection_retry_on_startup = True
    broker_url = 'pyamqp://guest:guest@rabbitmq:5672/'
    result_backend = 'rpc://'
    result_persistent = False
    timezone = 'Europe/Moscow'
    beat_schedule = {
        'update_db_every_15_seconds': {
            'task': 'src.celery.tasks.excel_parse_task',
            'schedule': 15,
        },
    }


celery_settings = Config()
