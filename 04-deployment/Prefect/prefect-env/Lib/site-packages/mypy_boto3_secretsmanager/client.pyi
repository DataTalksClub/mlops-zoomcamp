"""
Type annotations for secretsmanager service client.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/)

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_secretsmanager.client import SecretsManagerClient

    session = Session()
    client: SecretsManagerClient = session.client("secretsmanager")
    ```
"""

import sys
from typing import Any, Dict, Mapping, Sequence, Type

from botocore.client import BaseClient, ClientMeta

from .literals import SortOrderTypeType
from .paginator import ListSecretsPaginator
from .type_defs import (
    BatchGetSecretValueResponseTypeDef,
    BlobTypeDef,
    CancelRotateSecretResponseTypeDef,
    CreateSecretResponseTypeDef,
    DeleteResourcePolicyResponseTypeDef,
    DeleteSecretResponseTypeDef,
    DescribeSecretResponseTypeDef,
    EmptyResponseMetadataTypeDef,
    FilterTypeDef,
    GetRandomPasswordResponseTypeDef,
    GetResourcePolicyResponseTypeDef,
    GetSecretValueResponseTypeDef,
    ListSecretsResponseTypeDef,
    ListSecretVersionIdsResponseTypeDef,
    PutResourcePolicyResponseTypeDef,
    PutSecretValueResponseTypeDef,
    RemoveRegionsFromReplicationResponseTypeDef,
    ReplicaRegionTypeTypeDef,
    ReplicateSecretToRegionsResponseTypeDef,
    RestoreSecretResponseTypeDef,
    RotateSecretResponseTypeDef,
    RotationRulesTypeTypeDef,
    StopReplicationToReplicaResponseTypeDef,
    TagTypeDef,
    UpdateSecretResponseTypeDef,
    UpdateSecretVersionStageResponseTypeDef,
    ValidateResourcePolicyResponseTypeDef,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal

__all__ = ("SecretsManagerClient",)

class BotocoreClientError(Exception):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str

class Exceptions:
    ClientError: Type[BotocoreClientError]
    DecryptionFailure: Type[BotocoreClientError]
    EncryptionFailure: Type[BotocoreClientError]
    InternalServiceError: Type[BotocoreClientError]
    InvalidNextTokenException: Type[BotocoreClientError]
    InvalidParameterException: Type[BotocoreClientError]
    InvalidRequestException: Type[BotocoreClientError]
    LimitExceededException: Type[BotocoreClientError]
    MalformedPolicyDocumentException: Type[BotocoreClientError]
    PreconditionNotMetException: Type[BotocoreClientError]
    PublicPolicyException: Type[BotocoreClientError]
    ResourceExistsException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]

class SecretsManagerClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        SecretsManagerClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.exceptions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#exceptions)
        """

    def batch_get_secret_value(
        self,
        *,
        SecretIdList: Sequence[str] = ...,
        Filters: Sequence[FilterTypeDef] = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
    ) -> BatchGetSecretValueResponseTypeDef:
        """
        Retrieves the contents of the encrypted fields `SecretString` or `SecretBinary`
        for up to 20
        secrets.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.batch_get_secret_value)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#batch_get_secret_value)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.can_paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#can_paginate)
        """

    def cancel_rotate_secret(self, *, SecretId: str) -> CancelRotateSecretResponseTypeDef:
        """
        Turns off automatic rotation, and if a rotation is currently in progress,
        cancels the
        rotation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.cancel_rotate_secret)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#cancel_rotate_secret)
        """

    def close(self) -> None:
        """
        Closes underlying endpoint connections.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.close)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#close)
        """

    def create_secret(
        self,
        *,
        Name: str,
        ClientRequestToken: str = ...,
        Description: str = ...,
        KmsKeyId: str = ...,
        SecretBinary: BlobTypeDef = ...,
        SecretString: str = ...,
        Tags: Sequence[TagTypeDef] = ...,
        AddReplicaRegions: Sequence[ReplicaRegionTypeTypeDef] = ...,
        ForceOverwriteReplicaSecret: bool = ...,
    ) -> CreateSecretResponseTypeDef:
        """
        Creates a new secret.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.create_secret)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#create_secret)
        """

    def delete_resource_policy(self, *, SecretId: str) -> DeleteResourcePolicyResponseTypeDef:
        """
        Deletes the resource-based permission policy attached to the secret.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.delete_resource_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#delete_resource_policy)
        """

    def delete_secret(
        self,
        *,
        SecretId: str,
        RecoveryWindowInDays: int = ...,
        ForceDeleteWithoutRecovery: bool = ...,
    ) -> DeleteSecretResponseTypeDef:
        """
        Deletes a secret and all of its versions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.delete_secret)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#delete_secret)
        """

    def describe_secret(self, *, SecretId: str) -> DescribeSecretResponseTypeDef:
        """
        Retrieves the details of a secret.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.describe_secret)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#describe_secret)
        """

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#generate_presigned_url)
        """

    def get_random_password(
        self,
        *,
        PasswordLength: int = ...,
        ExcludeCharacters: str = ...,
        ExcludeNumbers: bool = ...,
        ExcludePunctuation: bool = ...,
        ExcludeUppercase: bool = ...,
        ExcludeLowercase: bool = ...,
        IncludeSpace: bool = ...,
        RequireEachIncludedType: bool = ...,
    ) -> GetRandomPasswordResponseTypeDef:
        """
        Generates a random password.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.get_random_password)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#get_random_password)
        """

    def get_resource_policy(self, *, SecretId: str) -> GetResourcePolicyResponseTypeDef:
        """
        Retrieves the JSON text of the resource-based policy document attached to the
        secret.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.get_resource_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#get_resource_policy)
        """

    def get_secret_value(
        self, *, SecretId: str, VersionId: str = ..., VersionStage: str = ...
    ) -> GetSecretValueResponseTypeDef:
        """
        Retrieves the contents of the encrypted fields `SecretString` or `SecretBinary`
        from the specified version of a secret, whichever contains
        content.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.get_secret_value)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#get_secret_value)
        """

    def list_secret_version_ids(
        self,
        *,
        SecretId: str,
        MaxResults: int = ...,
        NextToken: str = ...,
        IncludeDeprecated: bool = ...,
    ) -> ListSecretVersionIdsResponseTypeDef:
        """
        Lists the versions of a secret.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.list_secret_version_ids)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#list_secret_version_ids)
        """

    def list_secrets(
        self,
        *,
        IncludePlannedDeletion: bool = ...,
        MaxResults: int = ...,
        NextToken: str = ...,
        Filters: Sequence[FilterTypeDef] = ...,
        SortOrder: SortOrderTypeType = ...,
    ) -> ListSecretsResponseTypeDef:
        """
        Lists the secrets that are stored by Secrets Manager in the Amazon Web Services
        account, not including secrets that are marked for
        deletion.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.list_secrets)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#list_secrets)
        """

    def put_resource_policy(
        self, *, SecretId: str, ResourcePolicy: str, BlockPublicPolicy: bool = ...
    ) -> PutResourcePolicyResponseTypeDef:
        """
        Attaches a resource-based permission policy to a secret.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.put_resource_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#put_resource_policy)
        """

    def put_secret_value(
        self,
        *,
        SecretId: str,
        ClientRequestToken: str = ...,
        SecretBinary: BlobTypeDef = ...,
        SecretString: str = ...,
        VersionStages: Sequence[str] = ...,
        RotationToken: str = ...,
    ) -> PutSecretValueResponseTypeDef:
        """
        Creates a new version with a new encrypted secret value and attaches it to the
        secret.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.put_secret_value)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#put_secret_value)
        """

    def remove_regions_from_replication(
        self, *, SecretId: str, RemoveReplicaRegions: Sequence[str]
    ) -> RemoveRegionsFromReplicationResponseTypeDef:
        """
        For a secret that is replicated to other Regions, deletes the secret replicas
        from the Regions you
        specify.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.remove_regions_from_replication)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#remove_regions_from_replication)
        """

    def replicate_secret_to_regions(
        self,
        *,
        SecretId: str,
        AddReplicaRegions: Sequence[ReplicaRegionTypeTypeDef],
        ForceOverwriteReplicaSecret: bool = ...,
    ) -> ReplicateSecretToRegionsResponseTypeDef:
        """
        Replicates the secret to a new Regions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.replicate_secret_to_regions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#replicate_secret_to_regions)
        """

    def restore_secret(self, *, SecretId: str) -> RestoreSecretResponseTypeDef:
        """
        Cancels the scheduled deletion of a secret by removing the `DeletedDate` time
        stamp.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.restore_secret)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#restore_secret)
        """

    def rotate_secret(
        self,
        *,
        SecretId: str,
        ClientRequestToken: str = ...,
        RotationLambdaARN: str = ...,
        RotationRules: RotationRulesTypeTypeDef = ...,
        RotateImmediately: bool = ...,
    ) -> RotateSecretResponseTypeDef:
        """
        Configures and starts the asynchronous process of rotating the secret.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.rotate_secret)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#rotate_secret)
        """

    def stop_replication_to_replica(
        self, *, SecretId: str
    ) -> StopReplicationToReplicaResponseTypeDef:
        """
        Removes the link between the replica secret and the primary secret and promotes
        the replica to a primary secret in the replica
        Region.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.stop_replication_to_replica)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#stop_replication_to_replica)
        """

    def tag_resource(
        self, *, SecretId: str, Tags: Sequence[TagTypeDef]
    ) -> EmptyResponseMetadataTypeDef:
        """
        Attaches tags to a secret.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.tag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#tag_resource)
        """

    def untag_resource(
        self, *, SecretId: str, TagKeys: Sequence[str]
    ) -> EmptyResponseMetadataTypeDef:
        """
        Removes specific tags from a secret.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.untag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#untag_resource)
        """

    def update_secret(
        self,
        *,
        SecretId: str,
        ClientRequestToken: str = ...,
        Description: str = ...,
        KmsKeyId: str = ...,
        SecretBinary: BlobTypeDef = ...,
        SecretString: str = ...,
    ) -> UpdateSecretResponseTypeDef:
        """
        Modifies the details of a secret, including metadata and the secret value.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.update_secret)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#update_secret)
        """

    def update_secret_version_stage(
        self,
        *,
        SecretId: str,
        VersionStage: str,
        RemoveFromVersionId: str = ...,
        MoveToVersionId: str = ...,
    ) -> UpdateSecretVersionStageResponseTypeDef:
        """
        Modifies the staging labels attached to a version of a secret.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.update_secret_version_stage)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#update_secret_version_stage)
        """

    def validate_resource_policy(
        self, *, ResourcePolicy: str, SecretId: str = ...
    ) -> ValidateResourcePolicyResponseTypeDef:
        """
        Validates that a resource policy does not grant a wide range of principals
        access to your
        secret.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.validate_resource_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#validate_resource_policy)
        """

    def get_paginator(self, operation_name: Literal["list_secrets"]) -> ListSecretsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/client/#get_paginator)
        """
