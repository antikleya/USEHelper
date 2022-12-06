import datetime as _dt
from sqlalchemy import (
    Column, ForeignKey, Table,
    Integer, String, DateTime
)
from database import Base
from sqlalchemy.orm import relationship
import passlib.hash as _hash

teacher_theme_association_table = Table(
    'teacher_theme',
    Base.metadata,
    Column('teacher_id', ForeignKey("teachers.id")),
    Column('theme_id', ForeignKey('themes.id'))
)

test_question_association_table = Table(
    'test_question',
    Base.metadata,
    Column('test_id', ForeignKey("tests.id")),
    Column('question_id', ForeignKey("questions.id"))
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, default="")
    hashed_password = Column(String)
    role_id = Column(Integer, ForeignKey("roles.id"), default=1)

    role = relationship("Role", back_populates="users")
    tests = relationship("Test", back_populates="user")

    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.hashed_password)


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, unique=True)

    users = relationship("User", back_populates="role")


class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True)
    phone_number = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)

    themes = relationship("Theme", secondary=teacher_theme_association_table, back_populates="teachers")


class Theme(Base):
    __tablename__ = "themes"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"))

    subject = relationship("Subject", back_populates="themes")
    questions = relationship("Question", back_populates="theme")
    teachers = relationship("Teacher", secondary=teacher_theme_association_table, back_populates="themes")


class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True, unique=True)

    themes = relationship("Theme", back_populates="subject")


class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=_dt.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="tests")
    answers = relationship("Answer", back_populates="test")
    questions = relationship("Question", secondary=test_question_association_table, back_populates="tests")


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    answer = Column(String, nullable=False)
    text = Column(String, nullable=False)
    max_mark = Column(Integer, nullable=False)
    theme_id = Column(Integer, ForeignKey("themes.id"))

    theme = relationship("Theme", back_populates="questions")
    answers = relationship("Answer", back_populates="question")
    tests = relationship("Test", secondary=test_question_association_table, back_populates="questions")


class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True)
    given_answer = Column(String, default="")
    mark = Column(Integer, nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"))
    test_id = Column(Integer, ForeignKey("tests.id"))

    question = relationship("Question", back_populates="answers")
    test = relationship("Test", back_populates="answers")
