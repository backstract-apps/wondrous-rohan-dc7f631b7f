

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine(
     "sqlite+libsql:///embedded.db",
     connect_args={
         "sync_url": "libsql://coll-40b587e0e76f464c8cb78a581d06c1c5-mayson.aws-ap-south-1.turso.io",
         "auth_token": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3Nzc2Mjg3NTksInAiOnsicm9hIjp7Im5zIjpbIjAxOWRlMmVlLTNkMDEtNzc2OS1iYTE4LTEwNWI5YmVlNDVlMiJdfSwicnciOnsibnMiOlsiMDE5ZGUyZWUtM2QwMS03NzY5LWJhMTgtMTA1YjliZWU0NWUyIl19fSwicmlkIjoiZjYxYTFlZmUtYzdlMC00MTdiLWE5OWUtNTRkOWIyMmFjNDZiIn0.7L0xZbdrh5BhuQWqgHVZw2cw1uIC_EYbVZlt3s1nX8GXtZZ-8t4DCYwTWyxcOddFC0X7qg2LjSaD9vVPtLtSCA",
     },
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
Base = declarative_base()

