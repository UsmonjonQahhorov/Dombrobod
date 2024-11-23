import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from db import Base, db

db.init()


# ----------------------------- ABSTRACTS ----------------------------------
class AbstractClass:
    @staticmethod
    async def commit():
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

    @classmethod
    async def create(cls, **kwargs):
        object_ = cls(**kwargs)
        db.add(object_)
        await cls.commit()
        return object_

    @classmethod
    async def update(cls, id_, **kwargs):
        query = (
            sqlalchemy_update(cls)
            .where(cls.user_id == id_)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        print(query)
        await db.execute(query)
        await cls.commit()

    @classmethod
    async def get(cls, id_):
        query = select(cls).where(cls.id == id_)
        objects = await db.execute(query)
        object_ = objects.first()
        if object_:
            return object_[0]
        else:
            return []

    @classmethod
    async def get_user_id(cls, id_):
        try:
            query = select(cls).where(cls.user_id == str(id_))
            result = await db.execute(query)
            user = result.scalar_one_or_none()
            return user
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            return None

    @classmethod
    async def get_group_username(cls, username):
        try:
            query = select(cls).where(cls.username == username)
            objects = await db.execute(query)
            object_ = objects.first()
            if object_:
                return object_[0]
            else:
                return []
        except Exception as e:
            return e

    @classmethod
    async def get_group_id(cls, id_):
        query = select(cls).where(cls.group_id == id_)
        objects = await db.execute(query)
        object_ = objects.first()
        if object_:
            return object_[0]
        else:
            return []

    @classmethod
    async def delete(cls, id_):
        query = sqlalchemy_delete(cls).where(cls.id == id_)
        await db.execute(query)
        await cls.commit()
        return True

    @classmethod
    async def delete_task(cls, job_name_):
        try:
            query = sqlalchemy_delete(cls).where(cls.job_name == job_name_)
            await db.execute(query)
            await cls.commit()
            return True
        except:
            return "Something went wrong!!"

    @classmethod
    async def get_all(cls):
        query = select(cls)
        objects = await db.execute(query)
        result = []
        for i in objects.all():
            result.append(i[0])
        return result


class CreatedModel(Base, AbstractClass):
    __abstract__ = True

    created_at = Column(DateTime(), default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
