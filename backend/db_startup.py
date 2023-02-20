from services import get_db, create_database, generate_test, create_answer
import models as _models
import passlib.hash as _hash
from faker import Faker
import random
from sqlalchemy.sql.functions import random as _random
import os
import schemas as _schemas
import asyncio

db = next(get_db())

USER_AMOUNT = 20
SUBJECT_AMOUNT = 5
THEME_AMOUNT = 25
TEACHER_AMOUNT = 500
QUESTION_AMOUNT = 1000


def fill_roles():
    print('-----------------------------------------------')
    print('Starting generating roles...')

    roles = ["user", "administrator"]
    for role in roles:
        role_model = _models.Role(name=role)
        db.add(role_model)
        db.commit()

    print('Clients generated.')


def fill_users():
    print('-----------------------------------------------')
    print('Starting generating users...')

    fake = Faker("ru_RU")

    admin_model = _models.User(email="admin@mail.ru", name="admin",
                               hashed_password=_hash.bcrypt.hash("admin"), role_id=2)
    db.add(admin_model)
    db.commit()

    for i in range(USER_AMOUNT):
        name = fake.name()
        email = fake.email()
        password = 'password'

        user = _models.User(email=email, name=name, hashed_password=_hash.bcrypt.hash(password), role_id=1)

        db.add(user)
        db.commit()

    print('Users generated.')


def fill_subjects():
    print('-----------------------------------------------')
    print('Starting generating subjects...')

    for i in range(SUBJECT_AMOUNT):
        name = f"Example Subject {i}"

        subject = _models.Subject(name=name)

        db.add(subject)
        db.commit()

    print('Subjects generated.')


def fill_themes():
    print('-----------------------------------------------')
    print('Starting generating themes...')

    for i in range(THEME_AMOUNT):
        name = f"Example Theme {i}"
        description = f"Example Description {i}"
        subject_id = random.randint(1, SUBJECT_AMOUNT)

        theme = _models.Theme(name=name, description=description, subject_id=subject_id)

        db.add(theme)
        db.commit()

    print('Themes generated.')


def fill_teachers():
    print('-----------------------------------------------')
    print('Starting generating Teachers...')

    fake = Faker("ru_RU")

    for i in range(TEACHER_AMOUNT):
        name = f"Example Teacher {i}"
        phone_number = fake.phone_number()

        teacher = _models.Teacher(name=name, phone_number=phone_number)

        themes = db.query(_models.Theme)\
            .filter_by(subject_id=random.randint(1, SUBJECT_AMOUNT))\
            .order_by(_random())\
            .limit(3)\
            .all()

        teacher.themes = themes

        db.add(teacher)
        db.commit()

    print('Teachers generated.')


def fill_questions():
    print('-----------------------------------------------')
    print('Starting generating Questions...')

    for i in range(QUESTION_AMOUNT):
        text = f"Example Question {i}"
        answer = "right" if i % 2 else "wrong"
        max_mark = random.randint(1, 4)
        theme_id = random.randint(1, THEME_AMOUNT)

        question = _models.Question(text=text, answer=answer, max_mark=max_mark, theme_id=theme_id)

        db.add(question)
        db.commit()

    print('Questions generated.')


async def fill_tests():
    print('-----------------------------------------------')
    print('Starting generating Tests...')

    users = db.query(_models.User).all()

    for user in users:
        subject = db.query(_models.Subject).filter_by(id=random.randint(1, SUBJECT_AMOUNT)).first()
        themes = subject.themes[:5]
        theme_names = [theme.name for theme in themes]
        await generate_test(subject.id, theme_names, db, user)

    print('Tests generated.')


async def fill_answers():
    print('-----------------------------------------------')
    print('Starting generating Answers...')

    tests = db.query(_models.Test).all()

    for test in tests:

        for question in test.questions:
            answer = _schemas.AnswerCreate(given_answer="right", id=1)

            await create_answer(test.id, question.id, answer, db)

    print('Answers generated.')


fillers = [fill_roles, fill_users, fill_subjects, fill_themes, fill_teachers, fill_questions]


def setup():
    os.remove(path="database.db")
    create_database()


async def fill():
    setup()

    for filler in fillers:
        filler()

    await fill_tests()
    await fill_answers()

if __name__ == '__main__':
    asyncio.run(fill())
