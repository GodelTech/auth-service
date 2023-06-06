import pytest
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from src.data_access.postgresql.repositories.code_challenge import CodeChallengeRepository


@pytest.mark.asyncio
async def test_create_code_challenge_plain(connection: AsyncSession) -> None:
    repo = CodeChallengeRepository(connection)
    await repo.create(
        client_id="test_client",
        code_challenge_method="plain",
        code_challenge="test_code_challenge"
    )
    result = await repo.get_code_challenge_by_client_id("test_client")

    assert result.client_id == "test_client"
    assert result.code_challenge == "test_code_challenge"
    # We also need to check the code_challenge_method_id,
    # but it depends on the code_challenge_methods tabel, adjust it as needed
    assert result.code_challenge_method_id == 1


@pytest.mark.asyncio
async def test_create_code_challenge_s256(connection: AsyncSession) -> None:
    repo = CodeChallengeRepository(connection)
    await repo.create(
        client_id="test_client",
        code_challenge_method="S256",
        code_challenge="test_code_challenge"
    )
    result = await repo.get_code_challenge_by_client_id("test_client")

    assert result.client_id == "test_client"
    assert result.code_challenge == "test_code_challenge"
    # We also need to check the code_challenge_method_id,
    # but it depends on the code_challenge_methods tabel, adjust it as needed
    assert result.code_challenge_method_id == 2


@pytest.mark.asyncio
async def test_delete_code_challenge_by_client_id(connection: AsyncSession) -> None:
    repo = CodeChallengeRepository(connection)
    await repo.create(
        client_id="test_client",
        code_challenge_method="plain",
        code_challenge="test_code_challenge"
    )
    await repo.delete_code_challenge_by_client_id("test_client")
    with pytest.raises(NoResultFound):
        await repo.get_code_challenge_by_client_id("test_client")


@pytest.mark.asyncio
async def test_get_code_challenge_by_client_id_not_exist(connection: AsyncSession) -> None:
    repo = CodeChallengeRepository(connection)
    with pytest.raises(NoResultFound):
        await repo.get_code_challenge_by_client_id("not_exist")


@pytest.mark.asyncio
async def test_get_code_challenge_method_id_exist(connection: AsyncSession) -> None:
    repo = CodeChallengeRepository(connection)
    result = await repo.get_code_challenge_method_id("plain")
    id = 1  # the id of the "plain" method, adjust it as DB code_challenge_method table changes
    assert isinstance(result, int)
    assert result == id

    result = await repo.get_code_challenge_method_id("S256")
    id = 2  # the id of the "s256" method, adjust it as DB code_challenge_method table changes
    assert isinstance(result, int)
    assert result == id


@pytest.mark.asyncio
async def test_get_code_challenge_method_id_not_exist(connection: AsyncSession) -> None:
    repo = CodeChallengeRepository(connection)
    with pytest.raises(ValueError):
        await repo.get_code_challenge_method_id("not_exist")
