from sqlalchemy import select

from fast_zero.models import Todo, User


def test_create_user(session):
    new_user = User(username='alice', email='test@test.com', password='secret')
    session.add(new_user)
    session.commit()

    user = session.scalar(select(User).where(User.username == 'alice'))

    assert user.username == 'alice'


def test_create_todo(session, user: User):
    todo = Todo(
        title='Test todo',
        description='Test desc',
        state='draft',
        user_id=user.id,
    )

    session.add(todo)
    session.commit()
    session.refresh(todo)

    user = session.scalar(select(User).where(User.id == user.id))

    assert todo in user.todos
