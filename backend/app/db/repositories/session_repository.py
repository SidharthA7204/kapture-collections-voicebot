from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models.session import Session


class SessionRepository:

    def __init__(self, db: DBSession):
        self.db = db

    def get_by_call_id(
        self,
        call_id: str,
    ) -> Session | None:
        statement = select(Session).where(
            Session.call_id == call_id
        )

        return self.db.scalar(statement)

    def create(
        self,
        session: Session,
        commit: bool = True,
    ) -> Session:
        self.db.add(session)

        if commit:
            self.db.commit()
            self.db.refresh(session)

        return session

    def update(
        self,
        session: Session,
        commit: bool = True,
    ) -> Session:
        if commit:
            self.db.commit()
            self.db.refresh(session)

        return session
