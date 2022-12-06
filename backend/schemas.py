import datetime as _dt

import pydantic as _pydantic


class _UserBase(_pydantic.BaseModel):
    email: str
    name: str

    class Config:
        orm_mode = True


class UserCreate(_UserBase):
    hashed_password: str

    class Config:
        orm_mode = True


class User(_UserBase):
    id: int

    class Config:
        orm_mode = True


class _TeacherBase(_pydantic.BaseModel):
    pass


class TeacherCreate(_TeacherBase):
    pass


class TeacherUpdate(_TeacherBase):
    pass