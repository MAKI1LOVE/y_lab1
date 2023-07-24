from fastapi import HTTPException, status


async def submenu_not_found():
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='submenu not found'
    )
