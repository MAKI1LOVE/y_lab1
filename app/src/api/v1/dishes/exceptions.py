from fastapi import HTTPException, status


async def dish_not_found():
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='dish not found'
    )
