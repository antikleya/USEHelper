import datetime as _dt
from typing import List

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
    id: int
    name: str

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


# -----------------------USER-MODELS-----------------------------------
class UserCreate(_UserBase):
    hashed_password: str


class User(_UserBase):
    id: int
    role: _RoleBase


# ------------------------TEACHER-MODELS------------------------------
class Teacher(_TeacherBase):
    id: int
    themes: List[_ThemeBase]


class TeacherCreate(_TeacherBase):
    themes: List[_ThemeBase]


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
    themes: List[_ThemeBase]


class Subject(_SubjectBase):
    themes: List[_ThemeBase]
