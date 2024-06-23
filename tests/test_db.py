from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    new_user = User(username='alice', email='test@test.com', password='secret')
    session.add(new_user)
    session.commit()

    user = session.scalar(select(User).where(User.username == 'alice'))

    assert user.username == 'alice'
