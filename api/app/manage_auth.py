import argparse

from sqlalchemy import select

from api.app.core.database import SessionLocal
from api.app.models.auth import Role, User


def main() -> None:
    parser = argparse.ArgumentParser(description="Назначить администратора существующему аккаунту")
    parser.add_argument("login", help="Логин зарегистрированного пользователя")
    args = parser.parse_args()

    with SessionLocal.begin() as db:
        user = db.scalar(select(User).where(User.login == args.login).with_for_update())
        if user is None:
            parser.exit(1, "Пользователь не найден\n")
        if not user.is_active:
            parser.exit(1, "Аккаунт отключён\n")
        user.role = db.scalars(select(Role).where(Role.name == "admin")).one()

    print(f"Администратор назначен: {args.login}")


if __name__ == "__main__":
    main()
