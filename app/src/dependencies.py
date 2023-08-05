from src.database import get_session


def get_session_deco(func):
    """
    Give new session for every request in service.
    No need to create dependency in endpoint functions.
    :param func: func to wrap
    :return: simple data transfer
    """

    async def wrapper(*args, **kwargs):
        async with get_session() as session:
            data = await func(*args, **kwargs, session=session)
            await session.commit()

        return data

    return wrapper
