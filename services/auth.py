from dependency_injector.wiring import inject, Provide

from container import Container
from repositories.database_repo import UsersDBRepo


@inject
def get_user_by_username(
    username: str,
    user_repo: UsersDBRepo = Provide[Container.user_repo],
):
    return user_repo.get_user_by_username(username)


@inject
def get_user_by_id(
    user_id: int,
    user_repo: UsersDBRepo = Provide[Container.user_repo],
):
    return user_repo.get_user_by_id(user_id)
