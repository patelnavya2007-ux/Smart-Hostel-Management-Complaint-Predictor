from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker


# =========================
# DATABASE
# =========================

DATABASE_URL = "sqlite:///hostel.db"

engine = create_engine(DATABASE_URL)

Base = declarative_base()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# =========================
# STUDENT TABLE
# =========================

class Student(Base):

    __tablename__ = "students"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    username = Column(
        String,
        unique=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )

    room_number = Column(
        String
    )


# =========================
# COMPLAINT TABLE
# =========================

class Complaint(Base):

    __tablename__ = "complaints"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String,
        nullable=False
    )

    complaint = Column(
        String,
        nullable=False
    )

    category = Column(
        String,
        default="General"
    )

    priority = Column(
        String,
        default="Medium"
    )

    status = Column(
        String,
        default="Pending"
    )


# =========================
# ROOM TABLE
# =========================

class Room(Base):

    __tablename__ = "rooms"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    room_number = Column(
        String,
        unique=True,
        nullable=False
    )


# =========================
# CREATE TABLES
# =========================

Base.metadata.create_all(bind=engine)


# =========================
# CREATE 15 HOSTEL ROOMS
# =========================

db = SessionLocal()

existing_rooms = db.query(Room).count()

if existing_rooms == 0:

    for number in range(101, 116):

        room = Room(
            room_number=str(number)
        )

        db.add(room)

    db.commit()

db.close()