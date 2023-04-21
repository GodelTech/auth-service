from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from src.data_access.postgresql.repositories import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

class UnitOfWork:
    def __init__(self, session: Session):
        self.session = session
    
    def begin(self):
        self.session.begin()
        
    def commit(self):
        self.session.commit()
        
    def rollback(self):
        self.session.rollback()
        
    def user_repo(self) -> UserRepository:
        return UserRepository(self.session)
    

# Dependency for accessing UnitOfWork
def get_uow(db: Session) -> UnitOfWork:
    return SQLAlchemyUnitOfWork(db)


def get_user_repo(db: Session) -> UserRepository:
    return UserRepository(db)


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, engine):
        self.session_factory = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )

    def __enter__(self):
        self.session = self.session_factory()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.rollback()
        else:
            self.commit()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    async def async_commit(self):
        await self.session.commit()

    async def async_rollback(self):
        await self.session.rollback()

    async def async_close(self):
        await self.session.close()

    async def async_enter(self):
        self.session = self.session_factory()
        return self.session

    async def async_exit(self, exc_type, exc_val, exc_tb):
        if exc_val:
            await self.async_rollback()
        else:
            await self.async_commit()
        await self.async_close()
