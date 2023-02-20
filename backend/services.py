import database as _database
import datetime as _dt
import sqlalchemy.orm as _orm
import models as _models, schemas as _schemas
import passlib.hash as _hash
import jwt as _jwt
import fastapi as _fastapi
import fastapi.security as _security
from sqlalchemy.sql.functions import random as _random
from typing import List

oauth2schema = _security.OAuth2PasswordBearer(tokenUrl="/api/token")

JWT_SECRET = "string incedent"


# ---------------------------MISC-----------------------------------
def require_admin(func):
    async def wrapped(current_user: _schemas.User, *args, **kwargs):
        if not is_admin(current_user):
            raise _fastapi.HTTPException(status_code=401, detail='Must be an admin to perform this action')

        return await func(*args, **kwargs)

    return wrapped


def get_amounts(question_amount: int, theme_amount: int):
    amount = question_amount // theme_amount
    overhead = question_amount - theme_amount * amount
    amounts = [amount + 1 if i < overhead else amount for i in range(theme_amount)]
    return amounts


# -----------------------DATABASE-FUNCTIONS-------------------------
def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def fill_database(db: _orm.Session = next(get_db())):
    roles = ["user", "administrator"]
    for role in roles:
        role_model = _models.Role(name=role)
        db.add(role_model)
        db.commit()

    admin_model = _models.User(email="admin@mail.ru", name="admin",
                               hashed_password=_hash.bcrypt.hash("admin"), role_id=2)
    db.add(admin_model)
    db.commit()


# ------------------------USER-AND-LOGIN-FUNCTIONS-------------------------------
async def get_user_by_email(email: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.email == email).first()


async def _user_selector(user_id: int, db: _orm.Session):
    user = db.query(_models.User).filter_by(id=user_id).first()

    if user is None:
        raise _fastapi.HTTPException(status_code=404, detail="User does not exist")

    return user


async def _user_selector_change(user_id, db: _orm.Session, current_user: _schemas.User):
    user = await _user_selector(user_id, db)

    if user.id != current_user.id:
        raise _fastapi.HTTPException(status_code=401, detail="Can't do that action to another user")

    return user


def is_admin(user: _schemas.User, db: _orm.Session = next(get_db())):
    user_db = db.query(_models.User).filter_by(email=user.email).first()
    return user_db.role.name == 'administrator'


async def create_user(user: _schemas.UserCreate, db: _orm.Session):
    user_obj = _models.User(email=user.email, name=user.name, hashed_password=_hash.bcrypt.hash(user.hashed_password))

    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    return user_obj


async def authenticate_user(email: str, password: str, db: _orm.Session):
    user = await get_user_by_email(email, db)

    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user


async def create_token(user: _models.User):

    data = {'name': user.name, 'email': user.email, 'password': user.hashed_password}

    token = _jwt.encode(data, JWT_SECRET)

    return dict(access_token=token, token_type="bearer")


async def get_current_user(db: _orm.Session = _fastapi.Depends(get_db), token: str = _fastapi.Depends(oauth2schema)):
    try:
        payload = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(_models.User).filter_by(email=payload["email"]).first()
    except:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

    return _schemas.User.from_orm(user)


async def get_users(db: _orm.Session):
    users = db.query(_models.User).all()

    return list(map(_schemas.User.from_orm, users))


async def get_user(user_id: int, db: _orm.Session):
    user = await _user_selector(user_id, db)

    return _schemas.User.from_orm(user)


async def delete_user(user_id: int, current_user: _schemas.User, db: _orm.Session):
    user = await _user_selector_change(user_id, db, current_user)

    db.delete(user)
    db.commit()


async def update_user(user_id: int, user: _schemas.UserCreate, current_user: _schemas.User, db: _orm.Session):
    old_user = await _user_selector_change(user_id, db, current_user)

    old_user.name = user.name
    old_user.email = user.email
    old_user.hashed_password = _hash.bcrypt.hash(user.hashed_password)

    db.commit()
    db.refresh(old_user)

    return _schemas.User.from_orm(old_user)


# --------------------------------TEACHER-FUNCTIONS--------------------------
async def get_teacher_by_phone(phone_number: str, db: _orm.Session):
    return db.query(_models.Teacher).filter_by(phone_number=phone_number).first()


async def _teacher_selector(teacher_id: int, db: _orm.Session):
    teacher = db.query(_models.Teacher).filter_by(id=teacher_id).first()

    if teacher is None:
        raise _fastapi.HTTPException(status_code=404, detail='Teacher does not exist')

    return teacher


async def _get_teacher_themes(theme_ids: List[int], db: _orm.Session):
    themes = []

    for theme_id in theme_ids:
        theme = await _simple_theme_selector(theme_id, db)
        themes.append(theme)

    return themes


@require_admin
async def _teacher_selector_change(teacher_id: int, db: _orm.Session):
    return await _teacher_selector(teacher_id, db)


@require_admin
async def create_teacher(teacher: _schemas.TeacherCreate, db: _orm.Session):
    teacher_obj = _models.Teacher(name=teacher.name, phone_number=teacher.phone_number)

    themes = await _get_teacher_themes(teacher.theme_ids, db)
    teacher_obj.themes = themes

    db.add(teacher_obj)
    db.commit()
    db.refresh(teacher_obj)

    return teacher_obj


async def get_teachers(db: _orm.Session):
    teachers = db.query(_models.Teacher).all()

    return list(map(_schemas.Teacher.from_orm, teachers))


async def get_teacher(teacher_id: int, db: _orm.Session):
    teacher = await _teacher_selector(teacher_id, db)

    return _schemas.Teacher.from_orm(teacher)


async def delete_teacher(teacher_id: int, user: _schemas.User, db: _orm.Session):
    teacher = await _teacher_selector_change(user, teacher_id, db)

    db.delete(teacher)
    db.commit()


async def update_teacher(teacher_id: int, user: _schemas.User, db: _orm.Session, teacher: _schemas.TeacherCreate):
    old_teacher = await _teacher_selector_change(user, teacher_id, db)

    old_teacher.name = teacher.name
    old_teacher.phone_number = teacher.phone_number

    themes = await _get_teacher_themes(teacher.theme_ids, db)
    old_teacher.themes = themes

    db.commit()
    db.refresh(old_teacher)

    return _schemas.Teacher.from_orm(old_teacher)


# ----------------------------SUBJECT-FUNCTIONS-------------------------------
async def get_subject_by_name(subject_name: str, db: _orm.Session):
    return db.query(_models.Subject).filter_by(name=subject_name).first()


async def get_subject_by_id(subject_id: int, db: _orm.Session):
    return db.query(_models.Subject).filter_by(id=subject_id).first()


async def _subject_selector(subject_id: int, db: _orm.Session):
    subject = db.query(_models.Subject).filter_by(id=subject_id).first()

    if subject is None:
        raise _fastapi.HTTPException(status_code=404, detail='Subject does not exist')

    return subject


@require_admin
async def _subject_selector_change(subject_id: int, db: _orm.Session):
    subject = await _subject_selector(subject_id, db)

    return subject


@require_admin
async def create_subject(subject: _schemas.SubjectCreate, db: _orm.Session):
    subject_obj = _models.Subject(name=subject.name)

    db.add(subject_obj)
    db.commit()
    db.refresh(subject_obj)

    return subject_obj


async def get_subjects(db: _orm.Session):
    subjects = db.query(_models.Subject).all()

    return list(map(_schemas.Subject.from_orm, subjects))


async def get_subject(subject_id: int, db: _orm.Session):
    subject = await _subject_selector(subject_id, db)

    return _schemas.Subject.from_orm(subject)


async def delete_subject(subject_id: int, db: _orm.Session, user: _schemas.User):
    subject = await _subject_selector_change(user, subject_id, db)

    db.delete(subject)
    db.commit()


async def update_subject(subject_id: int, db: _orm.Session, user: _schemas.User, subject: _schemas.SubjectCreate):
    old_subject = await _subject_selector_change(user, subject_id, db)

    old_subject.name = subject.name

    db.commit()
    db.refresh(old_subject)

    return _schemas.Subject.from_orm(old_subject)


# ----------------------------------THEME-FUNCTIONS--------------------------
async def get_theme_by_name(subject_id: int, theme_name: str, db: _orm.Session):
    return db.query(_models.Theme).filter_by(name=theme_name, subject_id=subject_id).first()


async def _theme_selector(subject_id: int, theme_id: int, db: _orm.Session):
    theme = db.query(_models.Theme).filter_by(id=theme_id, subject_id=subject_id).first()

    if theme is None:
        raise _fastapi.HTTPException(status_code=404, detail='Theme does not exist')

    return theme


async def _simple_theme_selector(theme_id: int, db: _orm.Session):
    theme = db.query(_models.Theme).filter_by(id=theme_id).first()

    if theme is None:
        raise _fastapi.HTTPException(status_code=404, detail='Theme does not exist')

    return theme


@require_admin
async def _theme_selector_change(subject_id: int, theme_id: int, db: _orm.Session):
    return await _theme_selector(subject_id, theme_id, db)


async def create_theme(subject_id: int, db: _orm.Session, theme: _schemas.ThemeCreate, user: _schemas.User):
    subject = await _subject_selector_change(user, subject_id, db)

    theme_obj = _models.Theme(name=theme.name, description=theme.description, subject=subject, subject_id=subject.id)

    db.add(theme_obj)
    db.commit()
    db.refresh(theme_obj)

    return theme_obj


async def get_themes(subject_id: int, db: _orm.Session):
    subject = _schemas.Subject.from_orm(await _subject_selector(subject_id, db))

    themes = subject.themes

    return themes


async def get_theme(subject_id: int, theme_id: int, db: _orm.Session):
    return await _theme_selector(subject_id, theme_id, db)


async def delete_theme(subject_id: int, theme_id: int, db: _orm.Session, current_user: _schemas.User):
    theme = await _theme_selector_change(current_user, subject_id, theme_id, db)

    db.delete(theme)
    db.commit()


async def update_theme(
        subject_id: int,
        theme_id: int,
        theme: _schemas.ThemeCreate,
        db: _orm.Session,
        current_user: _schemas.User
):
    old_theme = await _theme_selector_change(current_user, subject_id, theme_id, db)

    old_theme.name = theme.name
    old_theme.description = theme.description

    db.commit()
    db.refresh(old_theme)

    return _schemas.Theme.from_orm(old_theme)


# ---------------------------------QUESTIONS-FUNCTIONS-----------------------------
async def get_question_by_text(theme_id: int, question_text: str, db: _orm.Session):
    return db.query(_models.Question).filter_by(theme_id=theme_id, text=question_text).first()


async def _question_selector(question_id: int, db: _orm.Session):
    question = db.query(_models.Question).filter_by(id=question_id).first()

    if question is None:
        raise _fastapi.HTTPException(status_code=404, detail="Question does not exist")

    return question


@require_admin
async def _question_selector_change(question_id: int, db: _orm.Session):
    return await _question_selector(question_id, db)


@require_admin
async def create_question(theme_id: int, question: _schemas.QuestionCreate, db: _orm.Session):
    question_orm = _models.Question(text=question.text, max_mark=question.max_mark, answer=question.answer,
                                    theme_id=theme_id)

    db.add(question_orm)
    db.commit()
    db.refresh(question_orm)

    return question_orm


async def get_question(question_id: int, db: _orm.Session):
    return await _question_selector(question_id, db)


async def get_questions(db: _orm.Session):
    questions = db.query(_models.Question).all()

    return list(map(_schemas.Question.from_orm, questions))


async def update_question(
        question_id: int,
        question: _schemas.QuestionCreate,
        db: _orm.Session,
        current_user: _schemas.User
):
    old_question = await _question_selector_change(current_user, question_id, db)

    old_question.text = question.text
    old_question.max_mark = question.max_mark
    old_question.answer = question.answer

    db.commit()
    db.refresh(old_question)

    return old_question


async def delete_question(
        question_id: int,
        db: _orm.Session,
        current_user: _schemas.User
):
    question = await _question_selector_change(current_user, question_id, db)

    db.delete(question)
    db.commit()


async def get_random_questions_by_theme(theme: _models.Theme, amount: int, db: _orm.Session):
    questions = db.query(_models.Question)\
        .filter_by(theme_id=theme.id)\
        .order_by(_random())\
        .limit(amount)\
        .all()
    return questions


# -------------------------------------ANSWER-FUNCTIONS-----------------------------
async def answer_exists(test_id: int, question_id: int, db: _orm.Session):
    answer = db.query(_models.Answer).filter_by(test_id=test_id, question_id=question_id).first()
    if answer is None:
        return False

    return True


async def _answer_selector(test_id: int, question_id: int, db: _orm.Session):
    return db.query(_models.Answer).filter_by(test_id=test_id, question_id=question_id).first()


async def get_mark(question_id: int, answer: _schemas.AnswerCreate, db: _orm.Session):
    question = db.query(_models.Question).filter_by(id=question_id).first()

    if question.max_mark == 1:
        if question.answer == answer.given_answer:
            return 1
        else:
            return 0

    else:
        answers = set(str(question.answer).split('; '))
        given_answers = set(answer.given_answer.split('; '))

        if len(given_answers) > len(answers):
            mark = len(answers) - len(given_answers)
        else:
            mark = 0
        mark += len(answers.intersection(given_answers))
        return max(0, mark)


async def create_answer(
        test_id: int,
        question_id: int,
        answer: _schemas.AnswerCreate,
        db: _orm.Session
):
    mark = await get_mark(question_id, answer, db)
    answer_orm = _models.Answer(given_answer=answer.given_answer, mark=mark, question_id=question_id, test_id=test_id)

    db.add(answer_orm)
    db.commit()
    db.refresh(answer_orm)

    return _schemas.Answer.from_orm(answer_orm)


async def update_answer(
        test_id: int,
        question_id: int,
        answer: _schemas.AnswerCreate,
        db: _orm.Session
):
    mark = await get_mark(question_id, answer, db)
    old_answer = await _answer_selector(test_id, question_id, db)

    old_answer.given_answer = answer.given_answer
    old_answer.mark = mark

    db.commit()
    db.refresh(old_answer)

    return _schemas.Answer.from_orm(old_answer)


# --------------------------------------TEST-FUNCTIONS---------------------------------
async def _test_selector(test_id: int, db: _orm.Session, user: _schemas.User):
    test = db.query(_models.Test).filter_by(id=test_id, user_id=user.id).first()

    if test is None:
        raise _fastapi.HTTPException(status_code=404, detail="Test does no exist")

    return test


async def _get_test_themes(subject_id: int, theme_names: List[str], db: _orm.Session):
    themes = []

    for theme_name in theme_names:
        themes.append(await get_theme_by_name(subject_id, theme_name, db))

    return themes


async def generate_test(subject_id: int, theme_names: List[str], db: _orm.Session, current_user: _schemas.User):
    themes = await _get_test_themes(subject_id, theme_names, db)

    if None in themes:
        raise _fastapi.HTTPException(status_code=401, detail="Incorrect theme name")

    amounts = get_amounts(20, len(themes))

    questions = []

    for (i, j) in zip(themes, amounts):
        questions.extend(await get_random_questions_by_theme(i, j, db))

    test = _models.Test(date=_dt.datetime.utcnow(), user_id=current_user.id)

    test.questions = questions

    db.add(test)
    db.commit()
    db.refresh(test)

    return test


async def get_test(test_id: int, db: _orm.Session, current_user: _schemas.User):
    return await _test_selector(test_id, db, current_user)


async def get_test_answers(db: _orm.Session, current_user: _schemas.User):
    tests = db.query(_models.Test).filter_by(user_id=current_user.id).all()

    return tests




