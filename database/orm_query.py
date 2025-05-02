from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Note

async def orm_add_product(session: AsyncSession, data: dict, user_id: int):
    obj = Note(
        name=data["name"],
        description=data["description"],
        user_id=user_id  # Добавляем привязку к пользователю
    )
    session.add(obj)
    await session.commit()

async def orm_get_products(session: AsyncSession, user_id: int):
    result = await session.execute(select(Note).where(Note.user_id == user_id))
    return result.scalars().all()

async def orm_get_product(session: AsyncSession, product_id: int):
    query = select(Note).where(Note.id == product_id)
    result = await session.execute(query)
    return result.scalar()

async def orm_update_product(session: AsyncSession, product_id: int, data):
    query = update(Note).where(Note.id == product_id).values(
        name=data["name"],
        description=data["description"]
    )
    await session.execute(query)
    await session.commit()

async def orm_delete_product(session: AsyncSession, product_id: int):
    query = delete(Note).where(Note.id == product_id)
    await session.execute(query)
    await session.commit()
