"""Transaction DAO module."""

__all__ = ("TransactionDAO",)

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from expenses_counter.daos.address import AddressDAO
from expenses_counter.daos.base import BaseDAO
from expenses_counter.daos.product import ProductDAO
from expenses_counter.models.transaction import Transaction

from .schemas import TransactionGet, TransactionPatch, TransactionPost, TransactionPut


class TransactionDAO(BaseDAO[Transaction, TransactionGet, TransactionPost, TransactionPut, TransactionPatch]):
    """Data Access Object for Transaction entities.

    This DAO implements CRUD operations for Transaction entities, interacting with
    the database through the provided database client. It extends BaseDAO with
    transaction-specific implementations.
    """

    schema_cls = TransactionGet

    async def get_instance_by_id(self, pk: int, session: AsyncSession) -> Transaction | None:
        """Retrieve a transaction by its primary key.

        Args:
            pk: The primary key (ID) of the transaction to retrieve.
            session: The async database session to use for the query.

        Returns:
            A Transaction instance if found, None otherwise.

        """
        result = await session.execute(
            select(Transaction)
            .where(Transaction.id == pk)
            .options(joinedload(Transaction.product), joinedload(Transaction.address))
        )
        return result.scalar_one_or_none()

    async def get_all_instances(self, session: AsyncSession) -> list[Transaction]:
        """Retrieve all transactions.

        Args:
            session: The async database session to use for the query.

        Returns:
            A list of Transaction instances for all transactions.

        """
        result = await session.execute(
            select(Transaction).options(joinedload(Transaction.product), joinedload(Transaction.address))
        )
        return result.scalars().all()

    async def create(self, transaction: TransactionPost) -> TransactionGet:
        """Create a new transaction.

        Args:
            transaction: A TransactionPost schema instance containing the transaction data.

        Returns:
            A TransactionGet schema instance representing the created transaction.

        Raises:
            ValueError: If the product_id or address_id is provided but the entity does not exist.

        """
        logger.debug(f"Creating transaction: {transaction}")
        product_dao = ProductDAO(self.database_client)
        address_dao = AddressDAO(self.database_client)

        async with self.database_client.session_factory() as session:
            if (await product_dao.get_instance_by_id(transaction.product_id, session)) is None:
                logger.error(f"Product with id {transaction.product_id} not found")
                raise ValueError(f"Product with id {transaction.product_id} not found")

            if (await address_dao.get_instance_by_id(transaction.address_id, session)) is None:
                logger.error(f"Address with id {transaction.address_id} not found")
                raise ValueError(f"Address with id {transaction.address_id} not found")

            new_transaction = Transaction(
                date=transaction.date,
                count=transaction.count,
                price=transaction.price,
                product_id=transaction.product_id,
                address_id=transaction.address_id,
            )
            session.add(new_transaction)
            await session.commit()

            payload = await self.get_by_id(new_transaction.id)
            logger.debug(f"Transaction created: {payload.id}")
            return payload

    async def update(self, pk: int, transaction: TransactionPut) -> TransactionGet:
        """Perform a full update on a transaction.

        Args:
            pk: The primary key (ID) of the transaction to update.
            transaction: A TransactionPut schema instance containing all fields for the update.

        Returns:
            A TransactionGet schema instance representing the updated transaction.

        Raises:
            ValueError: If the transaction with the given ID is not found, or if the
                product_id or address_id is provided but the entity does not exist.

        """
        logger.debug(f"Updating transaction with id {pk}: {transaction}")
        product_dao = ProductDAO(self.database_client)
        address_dao = AddressDAO(self.database_client)

        async with self.database_client.session_factory() as session:
            if (existing_transaction := await self.get_instance_by_id(pk, session)) is None:
                logger.error(f"Transaction with id {pk} not found")
                raise ValueError(f"Transaction with id {pk} not found")

            if (await product_dao.get_instance_by_id(transaction.product_id, session)) is None:
                logger.error(f"Product with id {transaction.product_id} not found")
                raise ValueError(f"Product with id {transaction.product_id} not found")

            if (await address_dao.get_instance_by_id(transaction.address_id, session)) is None:
                logger.error(f"Address with id {transaction.address_id} not found")
                raise ValueError(f"Address with id {transaction.address_id} not found")

            existing_transaction.date = transaction.date
            existing_transaction.count = transaction.count
            existing_transaction.price = transaction.price
            existing_transaction.product_id = transaction.product_id
            existing_transaction.address_id = transaction.address_id

            await session.commit()
            payload = await self.get_by_id(existing_transaction.id)
            logger.debug(f"Transaction updated: {payload.id}")
            return payload

    async def modify(self, pk: int, transaction: TransactionPatch) -> TransactionGet:
        """Perform a partial update on a transaction.

        Only the fields provided in the TransactionPatch schema will be updated.
        Fields that are None will be left unchanged.

        Args:
            pk: The primary key (ID) of the transaction to modify.
            transaction: A TransactionPatch schema instance containing only the fields to update.

        Returns:
            A TransactionGet schema instance representing the modified transaction.

        Raises:
            ValueError: If the transaction with the given ID is not found, or if the
                product_id or address_id is provided but the entity does not exist.

        """
        logger.debug(f"Modifying transaction with id {pk}: {transaction}")
        product_dao = ProductDAO(self.database_client)
        address_dao = AddressDAO(self.database_client)

        async with self.database_client.session_factory() as session:
            if (existing_transaction := await self.get_instance_by_id(pk, session)) is None:
                raise ValueError(f"Transaction with id {pk} not found")

            if transaction.date is not None:
                existing_transaction.date = transaction.date
            if transaction.count is not None:
                existing_transaction.count = transaction.count
            if transaction.price is not None:
                existing_transaction.price = transaction.price
            if transaction.product_id is not None:
                if (await product_dao.get_instance_by_id(transaction.product_id, session)) is None:
                    logger.error(f"Product with id {transaction.product_id} not found")
                    raise ValueError(f"Product with id {transaction.product_id} not found")
                existing_transaction.product_id = transaction.product_id
            if transaction.address_id is not None:
                if (await address_dao.get_instance_by_id(transaction.address_id, session)) is None:
                    logger.error(f"Address with id {transaction.address_id} not found")
                    raise ValueError(f"Address with id {transaction.address_id} not found")
                existing_transaction.address_id = transaction.address_id

            await session.commit()
            payload = await self.get_by_id(existing_transaction.id)
            logger.debug(f"Transaction modified: {payload.id}")
            return payload

