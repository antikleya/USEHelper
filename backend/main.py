from typing import List
import fastapi as _fastapi
import fastapi.security as _security

import sqlalchemy.orm as _orm

import services as _services, schemas as _schemas

app = _fastapi.FastAPI()


# --------------USER-API----------------------
@app.post("/api/users")
async def create_user(user: _schemas.UserCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    db_user = await _services.get_user_by_email(user.email, db)
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Email already is use")

    user = await _services.create_user(user, db)

    return await _services.create_token(user)


@app.get("/api/users", response_model=List[_schemas.User])
async def get_users(db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_users(db)


@app.get("/api/users/me", response_model=_schemas.User)
async def get_current_user(user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    return user


@app.get("/api/users/{user_id}", status_code=200)
async def get_user(user_id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_user(user_id, db)


@app.delete("/api/users/{user_id}", status_code=204)
async def delete_user(
        user_id: int,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    await _services.delete_user(user_id, current_user, db)

    return {"message", "Deleted Successfully"}


@app.put('/api/users/{user_id}', status_code=200)
async def update_user(
        user_id: int,
        user: _schemas.UserCreate,
        db: _orm.Session = _fastapi.Depends(_services.get_db),
        current_user: _schemas.User = _fastapi.Depends(_services.get_current_user)
):
    await _services.update_user(user_id, user, current_user, db)
    return {"message", "Updated Successfully"}


# ------------------------LOGIN-API------------------------------
@app.post("/api/token")
async def generate_token(
        form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
        db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    user = await _services.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

    return await _services.create_token(user)


@app.get("/api")
async def root():
    return {"Successful connect"}
