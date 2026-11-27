import argparse
from getpass import getpass
from pwdlib import PasswordHash
from sqlalchemy import select
from api.app.core.database import SessionLocal
from api.app.models.auth import Role, User


def main() -> None:
    parser = argparse.ArgumentParser(description='Создание учётной записи или назначение роли существующей')
    parser.add_argument('login')
    parser.add_argument('--role', choices=['student', 'teacher', 'admin', 'guest'], default='admin')
    parser.add_argument('--create', action='store_true', help='Создать аккаунт с интерактивным вводом пароля')
    args = parser.parse_args()
    login = args.login.strip()
    if not 3 <= len(login) <= 50:
        parser.error('Логин должен содержать от 3 до 50 символов')
    password = None
    if args.create:
        password = getpass('Пароль: ')
        if not 12 <= len(password) <= 128 or password != getpass('Повторите пароль: '):
            parser.error('Пароли не совпадают или длина вне диапазона 12–128')
    with SessionLocal.begin() as db:
        role = db.scalars(select(Role).where(Role.name == args.role)).one()
        user = db.scalar(select(User).where(User.login == login).with_for_update())
        if args.create:
            if user is not None:
                parser.error('Аккаунт уже существует')
            db.add(User(login=login, password_hash=PasswordHash.recommended().hash(password), role=role, is_active=True))
        else:
            if user is None or not user.is_active:
                parser.error('Аккаунт не найден или отключён')
            user.role = role
    print(f'Роль {args.role} назначена: {login}')


if __name__ == '__main__':
    main()
