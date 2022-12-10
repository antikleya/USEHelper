import database as _database
import sqlalchemy.orm as _orm
import models as _models, schemas as _schemas
import passlib.hash as _hash
import jwt as _jwt
import fastapi as _fastapi
import fastapi.security as _security

oauth2schema = _security.OAuth2PasswordBearer(tokenUrl="/api/token")

JWT_SECRET = "string incedent"


# ---------------------------MISC-----------------------------------
def require_admin(func):
    async def wrapped(current_user: _schemas.User, *args, **kwargs):
        if not is_admin(current_user):
            raise _fastapi.HTTPException(status_code=401, detail='Must be an admin to perform this action')

        return await func(*args, **kwargs)

    return wrapped

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
    roles = ["user", "teacher", "administrator"]
    for role in roles:
        role_model = _models.Role(name=role)
        db.add(role_model)
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


def is_admin(user: _schemas.User):
    return user.role.name == 'administrator'


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
    user_obj = _schemas.User.from_orm(user)

    token = _jwt.encode(user_obj.dict(), JWT_SECRET)

    return dict(access_token=token, token_type="bearer")


async def get_current_user(db: _orm.Session = _fastapi.Depends(get_db), token: str = _fastapi.Depends(oauth2schema)):
    try:
        payload = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(_models.User).get(payload["id"])
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


@require_admin
async def _teacher_selector_change(teacher_id: int, db: _orm.Session):
    return await _teacher_selector(teacher_id, db)


async def create_teacher(teacher: _schemas.TeacherCreate, db: _orm.Session):
    teacher_obj = _models.Teacher(name=teacher.name, phone_number=teacher.phone_number)

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
    teacher = _teacher_selector_change(user, teacher_id, db)

    db.delete(teacher)
    db.commit()


async def update_teacher(teacher_id: int, user: _schemas.User, db: _orm.Session, teacher: _schemas.TeacherCreate):
    old_teacher = _teacher_selector_change(user, teacher_id, db)

    old_teacher.name = teacher.name
    old_teacher.phone_number = teacher.phone_number
    old_teacher.themes = teacher.themes

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
    old_subject.themes = subject.themes

    db.commit()
    db.refresh(old_subject)

    return _schemas.Subject.from_orm(old_subject)


# ----------------------------------THEME-FUNCTIONS--------------------------
async def get_theme_by_name(theme_name, db: _orm.Session):
    return db.query(_models.Theme).filter_by(name=theme_name).first()


async def _theme_selector(subject_id: int, theme_id: int, db: _orm.Session):
    theme = db.query(_models.Theme).filter_by(id=theme_id, subject_id=subject_id).first()

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


async def update_theme(subject_id: int, theme_id: int, theme: _schemas.ThemeCreate, db: _orm.Session, current_user: _schemas.User):
    old_theme = await _theme_selector_change(current_user, subject_id, theme_id, db)

    old_theme.name = theme.name
    old_theme.description = theme.description

    db.commit()
    db.refresh(old_theme)

    return _schemas.Theme.from_orm(old_theme)