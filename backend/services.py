import database as _database
import sqlalchemy.orm as _orm
import models as _models, schemas as _schemas
import passlib.hash as _hash
import jwt as _jwt
import fastapi as _fastapi
import fastapi.security as _security

oauth2schema = _security.OAuth2PasswordBearer(tokenUrl="/api/token")

JWT_SECRET = "string incedent"


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


async def get_user_by_email(email: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.email == email).first()


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
