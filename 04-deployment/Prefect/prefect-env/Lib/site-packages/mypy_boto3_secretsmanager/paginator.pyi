"""
Type annotations for secretsmanager service client paginators.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/paginators/)

Usage::

    ```python
    from boto3.session import Session

    from mypy_boto3_secretsmanager.client import SecretsManagerClient
    from mypy_boto3_secretsmanager.paginator import (
        ListSecretsPaginator,
    )

    session = Session()
    client: SecretsManagerClient = session.client("secretsmanager")

    list_secrets_paginator: ListSecretsPaginator = client.get_paginator("list_secrets")
    ```
"""

from typing import Generic, Iterator, Sequence, TypeVar

from botocore.paginate import PageIterator, Paginator

from .literals import SortOrderTypeType
from .type_defs import FilterTypeDef, ListSecretsResponseTypeDef, PaginatorConfigTypeDef

__all__ = ("ListSecretsPaginator",)

_ItemTypeDef = TypeVar("_ItemTypeDef")

class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """

class ListSecretsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Paginator.ListSecrets)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/paginators/#listsecretspaginator)
    """

    def paginate(
        self,
        *,
        IncludePlannedDeletion: bool = ...,
        Filters: Sequence[FilterTypeDef] = ...,
        SortOrder: SortOrderTypeType = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...,
    ) -> _PageIterator[ListSecretsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Paginator.ListSecrets.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/paginators/#listsecretspaginator)
        """
