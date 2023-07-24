from fastapi import HTTPException, status


async def menu_not_found():
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='menu not found'
    )
