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
    {
        "name": "Themes",
        "description": "Operations with Themes",
    },
    {
        "name": "Questions",
        "description": "Operations with Questions",
    },
    {
        "name": "Answers",
        "description": "Operations with Answers",
    },
    {
        "name": "Tests",
        "description": "Operations with Tests",
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

    return {"message": "Deleted Successfully"}


@app.put('/api/users/{user_id}', tags=["Users"], status_code=200)
async def update_user(
        user_id: int,
        user: _schemas.UserCreate,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    await _services.update_user(user_id, user, current_user, db)
    return {"message": "Updated Successfully"}


@app.get('/api/users/{user_id}/tests', tags=['Users'], response_model=List[_schemas.TestCompleted])
async def get_test_results(
        user_id: int,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    if user_id != current_user.id:
        raise _fastapi.HTTPException(status_code=403, detail="Cannot view other user results")
    tests = await _services.get_test_answers(db, current_user)

    return list(map(_schemas.TestCompleted.from_orm, tests))


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
async def create_teacher(teacher: _schemas.TeacherCreate,
                         db: _orm.Session = _fastapi.Depends(_services.get_db),
                         current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    teacher_db = await _services.get_teacher_by_phone(teacher.phone_number, db)
    if teacher_db:
        raise _fastapi.HTTPException(status_code=400, detail='This phone number is already in use')

    teacher = await _services.create_teacher(current_user, teacher, db)

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

    return {"message": "Deleted Successfully"}


@app.put("/api/teachers/{teacher_id}", tags=["Teachers"], status_code=200)
async def update_teacher(
        teacher_id: int,
        teacher: _schemas.TeacherCreate,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    await _services.update_teacher(teacher_id, current_user, db, teacher)

    return {"message": "Updated Successfully"}


# --------------------------------------SUBJECT-API----------------------
@app.post("/api/subjects", tags=["Subjects"])
async def create_subject(
        subject: _schemas.SubjectCreate,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    subject_db = await _services.get_subject_by_name(subject.name, db)

    if subject_db:
        raise _fastapi.HTTPException(status_code=400, detail='This subject already exists')

    subject = await _services.create_subject(user, subject, db)

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

    return {"message": "Deleted Successfully"}


@app.put("/api/subjects/{subject_id}", tags=["Subjects"], status_code=200)
async def update_subject(
        subject_id: int,
        subject: _schemas.SubjectCreate,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    await _services.update_subject(subject_id, db, current_user, subject)

    return {"message": "Updated Successfully"}


# ----------------------------------THEME-API-------------------------------
@app.post('/api/subjects/{subject_id}/themes', tags=["Themes"])
async def create_theme(
        subject_id: int,
        theme: _schemas.ThemeCreate,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    theme_db = await _services.get_theme_by_name(subject_id, theme.name, db)

    if theme_db:
        raise _fastapi.HTTPException(status_code=400, detail='This theme already exists')

    theme = await _services.create_theme(subject_id, db, theme, current_user)

    return _schemas.Theme.from_orm(theme)


@app.get('/api/subjects/{subject_id}/themes', tags=["Themes"], response_model=List[_schemas._ThemeBase])
async def get_themes(
        subject_id: int,
        db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    return await _services.get_themes(subject_id, db)


@app.get('/api/subjects/{subject_id}/themes/{theme_id}', tags=["Themes"], status_code=200)
async def get_theme(
        subject_id: int,
        theme_id: int,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    return await _services.get_theme(subject_id, theme_id, db)


@app.put('/api/subjects/{subject_id}/themes/{theme_id}', tags=["Themes"], status_code=200)
async def update_theme(
        subject_id: int,
        theme_id: int,
        theme: _schemas.ThemeCreate,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    theme = await _services.update_theme(subject_id, theme_id, theme, db, current_user)

    return theme


@app.delete("/api/subjects/{subject_id}/themes/{theme_id}", tags=["Themes"], status_code=204)
async def delete_theme(
        subject_id: int,
        theme_id: int,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    await _services.delete_theme(subject_id, theme_id, db, current_user)

    return {"message": "Deleted Successfully"}


# ----------------------------------------QUESTION-API------------------------------
@app.get('/api/questions/{question_id}', tags=["Questions"], status_code=200, response_model=_schemas.Question)
async def get_question(
        question_id: int,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    question = await _services.get_question(question_id, db)
    return _schemas.Question.from_orm(question)


@app.get('/api/questions', tags=['Questions'], response_model=List[_schemas.Question])
async def get_questions(db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_questions(db)


@app.post('/api/questions/{theme_id}', tags=['Questions'])
async def create_question(
        question: _schemas.QuestionCreate,
        theme_id: int = _fastapi.Query(),
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    question_db = await _services.get_question_by_text(theme_id, question.text, db)

    if question_db:
        raise _fastapi.HTTPException(status_code=400, detail='Question already exists')

    question = await _services.create_question(current_user, theme_id, question, db)

    return _schemas.Question.from_orm(question)


@app.put('/api/questions/{question_id}', tags=['Questions'], status_code=200)
async def update_question(
        question_id: int,
        question: _schemas.QuestionCreate,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    question = await _services.update_question(question_id, question, db, current_user)

    return _schemas.Question.from_orm(question)


@app.delete('/api/questions/{questions_id}', tags=['Questions'], status_code=204)
async def delete_question(
        question_id: int,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    await _services.delete_question(question_id, db, current_user)

    return {"message": "Deleted Successfully"}


# ------------------------------------ANSWER-API------------------------------
@app.post('/api/subjects/{subject_id}/tests/{test_id}/', tags=['Answers'], status_code=200)
async def create_or_update_answer(
        test_id: int,
        answer: _schemas.AnswerCreate,
        question_id: int = _fastapi.Query(),
        db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    if await _services.answer_exists(test_id, question_id, db):
        answer = await _services.update_answer(test_id, question_id, answer, db)
    else:
        answer = await _services.create_answer(test_id, question_id, answer, db)

    return answer


# ----------------------------------------TEST-API------------------------------
@app.get("/api/subjects/{subject_id}/tests/{test_id}", tags=['Tests'])
async def get_test(
        test_id: int,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    test = await _services.get_test(test_id, db, current_user)

    return _schemas.Test.from_orm(test)


@app.get('/api/subjects/{subject_id}/tests', tags=['Tests'])
async def generate_test(
        subject_id: int,
        theme_names: List[str] = _fastapi.Query(default=[]),
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    if not theme_names:
        raise _fastapi.HTTPException(status_code=400, detail='No theme names given')

    test = await _services.generate_test(subject_id, theme_names, db, current_user)

    return _schemas.Test.from_orm(test)
