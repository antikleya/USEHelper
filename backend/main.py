from typing import List
import fastapi as _fastapi
import fastapi.security as _security

import sqlalchemy.orm as _orm

import services as _services, schemas as _schemas

tags_metadata = [
    {
        "name": "Users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "Subjects",
        "description": "Operations with Subjects",
    },
    {
        "name": "Teachers",
        "description": "Operations with Teachers",
    },
]

app = _fastapi.FastAPI(openapi_tags=tags_metadata)


# --------------USER-API----------------------
@app.post("/api/users", tags=["Users"])
async def create_user(user: _schemas.UserCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    db_user = await _services.get_user_by_email(user.email, db)
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Email already is use")

    user = await _services.create_user(user, db)

    return await _services.create_token(user)


@app.get("/api/users", tags=["Users"], response_model=List[_schemas.User])
async def get_users(db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_users(db)


@app.get("/api/users/me", tags=["Users"], response_model=_schemas.User)
async def get_current_user(user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    return user


@app.get("/api/users/{user_id}", tags=["Users"], status_code=200)
async def get_user(user_id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_user(user_id, db)


@app.delete("/api/users/{user_id}", tags=["Users"], status_code=204)
async def delete_user(
        user_id: int,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    await _services.delete_user(user_id, current_user, db)

    return {"message", "Deleted Successfully"}


@app.put('/api/users/{user_id}', tags=["Users"], status_code=200)
async def update_user(
        user_id: int,
        user: _schemas.UserCreate,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    await _services.update_user(user_id, user, current_user, db)
    return {"message", "Updated Successfully"}


# ------------------------LOGIN-API------------------------------
@app.post("/api/token", tags=["Users"])
async def generate_token(
        form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
        db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    user = await _services.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

    return await _services.create_token(user)


# -------------------------Teacher-API----------------------------
@app.post("/api/teachers", tags=["Teachers"])
async def create_teacher(teacher: _schemas.TeacherCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    teacher_db = await _services.get_teacher_by_phone(teacher.phone_number, db)
    if teacher_db:
        raise _fastapi.HTTPException(status_code=400, detail='This phone number is already in use')

    teacher = await _services.create_teacher(teacher, db)

    return _schemas.Teacher.from_orm(teacher)


@app.get("/api/teachers", tags=["Teachers"], response_model=List[_schemas.Teacher])
async def get_teachers(db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_teachers(db)


@app.get("/api/teachers/{teacher_id}", tags=["Teachers"], status_code=200)
async def get_teacher(teacher_id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_teacher(teacher_id, db)


@app.delete("/api/teachers/{teacher_id}", tags=["Teachers"], status_code=204)
async def delete_teacher(
        teacher_id: int,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    await _services.delete_teacher(teacher_id, current_user, db)

    return {"message", "Deleted Successfully"}


@app.put("/api/teachers/{teacher_id}", tags=["Teachers"], status_code=200)
async def update_teacher(
        teacher_id: int,
        teacher: _schemas.TeacherCreate,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    await _services.update_teacher(teacher_id, current_user, db, teacher)

    return {"message", "Updated Successfully"}


# --------------------------------------SUBJECT-API----------------------
@app.post("/api/subjects", tags=["Subjects"])
async def create_subject(
        subject: _schemas.SubjectCreate,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    if not _services.is_admin(user):
        raise _fastapi.HTTPException(status_code=401, detail='Must be an admin to perform this action')

    subject_db = await _services.get_subject_by_name(subject.name, db)

    if subject_db:
        raise _fastapi.HTTPException(status_code=400, detail='This subject already exists')

    subject = await _services.create_subject(subject, db)

    return _schemas.Subject.from_orm(subject)


@app.get("/api/subjects", tags=["Subjects"], response_model=List[_schemas.Subject])
async def get_subjects(db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_subjects(db)


@app.get("/api/subjects/{subject_id}", tags=["Subjects"], status_code=200)
async def get_subject(subject_id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_subject(subject_id, db)


@app.delete("/api/subjects/{subject_id}", tags=["Subjects"], status_code=204)
async def delete_subject(
        subject_id: int,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    await _services.delete_subject(subject_id, db, current_user)

    return {"message", "Deleted Successfully"}


@app.put("/api/subjects/{subject_id}", tags=["Subjects"], status_code=200)
async def update_subject(
        subject_id: int,
        subject: _schemas.SubjectCreate,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    await _services.update_subject(subject_id, db, current_user, subject)

    return {"message", "Updated Successfully"}
