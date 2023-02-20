import datetime as _dt
from typing import List, Tuple

import pydantic as _pydantic


# ----------------BASE-MODELS------------------
class _UserBase(_pydantic.BaseModel):
    email: str
    name: str

    class Config:
        orm_mode = True


class _TeacherBase(_pydantic.BaseModel):
    name: str
    phone_number: str

    class Config:
        orm_mode = True


class _ThemeBase(_pydantic.BaseModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True


class _RoleBase(_pydantic.BaseModel):
    id: int = 1
    name: str = 'user'

    class Config:
        orm_mode = True


class _SubjectBase(_pydantic.BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class _QuestionBase(_pydantic.BaseModel):
    id: int
    text: str
    max_mark: int

    class Config:
        orm_mode = True


class _TestBase(_pydantic.BaseModel):
    id: int

    class Config:
        orm_mode = True


class _AnswerBase(_pydantic.BaseModel):
    id: int
    given_answer: str

    class Config:
        orm_mode = True


# -----------------------USER-MODELS-----------------------------------
class UserCreate(_UserBase):
    hashed_password: str


class User(_UserBase):
    id: int
    role_id: int


# ------------------------TEACHER-MODELS------------------------------
class Teacher(_TeacherBase):
    id: int
    themes: List[_ThemeBase]


class TeacherCreate(_TeacherBase):
    theme_ids: List[int]


# ----------------------------THEME-MODELS-----------------------------
class ThemeCreate(_ThemeBase):
    pass


class Theme(_ThemeBase):
    id: int
    teachers: List[_TeacherBase]
    subject: _SubjectBase
    questions: List[_QuestionBase]


# ------------------------------SUBJECT-MODELS---------------------------
class SubjectCreate(_SubjectBase):
    pass


class Subject(_SubjectBase):
    themes: List[_ThemeBase]


# -------------------------------QUESTION-MODELS-------------------------
class QuestionCreate(_QuestionBase):
    answer: str


class Question(_QuestionBase):
    theme: _ThemeBase


# --------------------------------ANSWER-MODELS---------------------------
class Answer(_AnswerBase):
    pass


class AnswerComplete(_AnswerBase):
    mark: int


class AnswerCreate(_AnswerBase):
    pass


# --------------------------------TEST-MODELS-----------------------------
class Test(_TestBase):
    questions: List[_QuestionBase]


class TestCompleted(Test):
    answers: List[AnswerComplete]

