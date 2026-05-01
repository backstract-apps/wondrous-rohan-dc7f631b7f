from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import class_mapper
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, Float, Text, ForeignKey, JSON, Numeric, Date, \
    TIMESTAMP, UUID, LargeBinary, text as text_sql, Interval
from sqlalchemy.types import Enum
from sqlalchemy.ext.declarative import declarative_base


@as_declarative()
class Base:
    id: int
    __name__: str

    # Auto-generate table name if not provided
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    # Generic to_dict() method
    def to_dict(self):
        """
        Converts the SQLAlchemy model instance to a dictionary, ensuring UUID fields are converted to strings.
        """
        result = {}
        for column in class_mapper(self.__class__).columns:
            value = getattr(self, column.key)
                # Handle UUID fields
            if isinstance(value, uuid.UUID):
                value = str(value)
            # Handle datetime fields
            elif isinstance(value, datetime):
                value = value.isoformat()  # Convert to ISO 8601 string
            # Handle Decimal fields
            elif isinstance(value, Decimal):
                value = float(value)

            result[column.key] = value
        return result




class AppUserAnalytics(Base):
    __tablename__ = "app_user_analytics"

    id = Column(Integer, primary_key=True)
    session_id = Column(String)
    action = Column(String)
    version = Column(String, nullable=True)
    timestamp = Column(DateTime, server_default=text_sql("now()"))
    user_agent = Column(String, nullable=True)
    locale = Column(String, nullable=True)
    location = Column(String, nullable=True)
    referrer = Column(String, nullable=True)
    pathname = Column(String, nullable=True)
    href = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=text_sql("now()"))


class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    title = Column(String)
    description = Column(String, nullable=True)
    status = Column(String)
    priority = Column(String)
    due_date = Column(String, nullable=True)
    created_at = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)
    created_at = Column(String, nullable=True)


