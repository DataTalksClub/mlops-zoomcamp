"""
Type annotations for secretsmanager service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_secretsmanager/type_defs/)

Usage::

    ```python
    from mypy_boto3_secretsmanager.type_defs import APIErrorTypeTypeDef

    data: APIErrorTypeTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import IO, Any, Dict, List, Sequence, Union

from botocore.response import StreamingBody

from .literals import FilterNameStringTypeType, SortOrderTypeType, StatusTypeType

if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "APIErrorTypeTypeDef",
    "FilterTypeDef",
    "ResponseMetadataTypeDef",
    "SecretValueEntryTypeDef",
    "BlobTypeDef",
    "CancelRotateSecretRequestRequestTypeDef",
    "ReplicaRegionTypeTypeDef",
    "TagTypeDef",
    "ReplicationStatusTypeTypeDef",
    "DeleteResourcePolicyRequestRequestTypeDef",
    "DeleteSecretRequestRequestTypeDef",
    "DescribeSecretRequestRequestTypeDef",
    "RotationRulesTypeTypeDef",
    "GetRandomPasswordRequestRequestTypeDef",
    "GetResourcePolicyRequestRequestTypeDef",
    "GetSecretValueRequestRequestTypeDef",
    "ListSecretVersionIdsRequestRequestTypeDef",
    "SecretVersionsListEntryTypeDef",
    "PaginatorConfigTypeDef",
    "PutResourcePolicyRequestRequestTypeDef",
    "RemoveRegionsFromReplicationRequestRequestTypeDef",
    "RestoreSecretRequestRequestTypeDef",
    "StopReplicationToReplicaRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateSecretVersionStageRequestRequestTypeDef",
    "ValidateResourcePolicyRequestRequestTypeDef",
    "ValidationErrorsEntryTypeDef",
    "BatchGetSecretValueRequestRequestTypeDef",
    "ListSecretsRequestRequestTypeDef",
    "CancelRotateSecretResponseTypeDef",
    "DeleteResourcePolicyResponseTypeDef",
    "DeleteSecretResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "GetRandomPasswordResponseTypeDef",
    "GetResourcePolicyResponseTypeDef",
    "GetSecretValueResponseTypeDef",
    "PutResourcePolicyResponseTypeDef",
    "PutSecretValueResponseTypeDef",
    "RestoreSecretResponseTypeDef",
    "RotateSecretResponseTypeDef",
    "StopReplicationToReplicaResponseTypeDef",
    "UpdateSecretResponseTypeDef",
    "UpdateSecretVersionStageResponseTypeDef",
    "BatchGetSecretValueResponseTypeDef",
    "PutSecretValueRequestRequestTypeDef",
    "UpdateSecretRequestRequestTypeDef",
    "ReplicateSecretToRegionsRequestRequestTypeDef",
    "CreateSecretRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "CreateSecretResponseTypeDef",
    "RemoveRegionsFromReplicationResponseTypeDef",
    "ReplicateSecretToRegionsResponseTypeDef",
    "DescribeSecretResponseTypeDef",
    "RotateSecretRequestRequestTypeDef",
    "SecretListEntryTypeDef",
    "ListSecretVersionIdsResponseTypeDef",
    "ListSecretsRequestListSecretsPaginateTypeDef",
    "ValidateResourcePolicyResponseTypeDef",
    "ListSecretsResponseTypeDef",
)

APIErrorTypeTypeDef = TypedDict(
    "APIErrorTypeTypeDef",
    {
        "SecretId": NotRequired[str],
        "ErrorCode": NotRequired[str],
        "Message": NotRequired[str],
    },
)
FilterTypeDef = TypedDict(
    "FilterTypeDef",
    {
        "Key": NotRequired[FilterNameStringTypeType],
        "Values": NotRequired[Sequence[str]],
    },
)
ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
        "HostId": NotRequired[str],
    },
)
SecretValueEntryTypeDef = TypedDict(
    "SecretValueEntryTypeDef",
    {
        "ARN": NotRequired[str],
        "Name": NotRequired[str],
        "VersionId": NotRequired[str],
        "SecretBinary": NotRequired[bytes],
        "SecretString": NotRequired[str],
        "VersionStages": NotRequired[List[str]],
        "CreatedDate": NotRequired[datetime],
    },
)
BlobTypeDef = Union[str, bytes, IO[Any], StreamingBody]
CancelRotateSecretRequestRequestTypeDef = TypedDict(
    "CancelRotateSecretRequestRequestTypeDef",
    {
        "SecretId": str,
    },
)
ReplicaRegionTypeTypeDef = TypedDict(
    "ReplicaRegionTypeTypeDef",
    {
        "Region": NotRequired[str],
        "KmsKeyId": NotRequired[str],
    },
)
TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": NotRequired[str],
        "Value": NotRequired[str],
    },
)
ReplicationStatusTypeTypeDef = TypedDict(
    "ReplicationStatusTypeTypeDef",
    {
        "Region": NotRequired[str],
        "KmsKeyId": NotRequired[str],
        "Status": NotRequired[StatusTypeType],
        "StatusMessage": NotRequired[str],
        "LastAccessedDate": NotRequired[datetime],
    },
)
DeleteResourcePolicyRequestRequestTypeDef = TypedDict(
    "DeleteResourcePolicyRequestRequestTypeDef",
    {
        "SecretId": str,
    },
)
DeleteSecretRequestRequestTypeDef = TypedDict(
    "DeleteSecretRequestRequestTypeDef",
    {
        "SecretId": str,
        "RecoveryWindowInDays": NotRequired[int],
        "ForceDeleteWithoutRecovery": NotRequired[bool],
    },
)
DescribeSecretRequestRequestTypeDef = TypedDict(
    "DescribeSecretRequestRequestTypeDef",
    {
        "SecretId": str,
    },
)
RotationRulesTypeTypeDef = TypedDict(
    "RotationRulesTypeTypeDef",
    {
        "AutomaticallyAfterDays": NotRequired[int],
        "Duration": NotRequired[str],
        "ScheduleExpression": NotRequired[str],
    },
)
GetRandomPasswordRequestRequestTypeDef = TypedDict(
    "GetRandomPasswordRequestRequestTypeDef",
    {
        "PasswordLength": NotRequired[int],
        "ExcludeCharacters": NotRequired[str],
        "ExcludeNumbers": NotRequired[bool],
        "ExcludePunctuation": NotRequired[bool],
        "ExcludeUppercase": NotRequired[bool],
        "ExcludeLowercase": NotRequired[bool],
        "IncludeSpace": NotRequired[bool],
        "RequireEachIncludedType": NotRequired[bool],
    },
)
GetResourcePolicyRequestRequestTypeDef = TypedDict(
    "GetResourcePolicyRequestRequestTypeDef",
    {
        "SecretId": str,
    },
)
GetSecretValueRequestRequestTypeDef = TypedDict(
    "GetSecretValueRequestRequestTypeDef",
    {
        "SecretId": str,
        "VersionId": NotRequired[str],
        "VersionStage": NotRequired[str],
    },
)
ListSecretVersionIdsRequestRequestTypeDef = TypedDict(
    "ListSecretVersionIdsRequestRequestTypeDef",
    {
        "SecretId": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "IncludeDeprecated": NotRequired[bool],
    },
)
SecretVersionsListEntryTypeDef = TypedDict(
    "SecretVersionsListEntryTypeDef",
    {
        "VersionId": NotRequired[str],
        "VersionStages": NotRequired[List[str]],
        "LastAccessedDate": NotRequired[datetime],
        "CreatedDate": NotRequired[datetime],
        "KmsKeyIds": NotRequired[List[str]],
    },
)
PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": NotRequired[int],
        "PageSize": NotRequired[int],
        "StartingToken": NotRequired[str],
    },
)
PutResourcePolicyRequestRequestTypeDef = TypedDict(
    "PutResourcePolicyRequestRequestTypeDef",
    {
        "SecretId": str,
        "ResourcePolicy": str,
        "BlockPublicPolicy": NotRequired[bool],
    },
)
RemoveRegionsFromReplicationRequestRequestTypeDef = TypedDict(
    "RemoveRegionsFromReplicationRequestRequestTypeDef",
    {
        "SecretId": str,
        "RemoveReplicaRegions": Sequence[str],
    },
)
RestoreSecretRequestRequestTypeDef = TypedDict(
    "RestoreSecretRequestRequestTypeDef",
    {
        "SecretId": str,
    },
)
StopReplicationToReplicaRequestRequestTypeDef = TypedDict(
    "StopReplicationToReplicaRequestRequestTypeDef",
    {
        "SecretId": str,
    },
)
UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "SecretId": str,
        "TagKeys": Sequence[str],
    },
)
UpdateSecretVersionStageRequestRequestTypeDef = TypedDict(
    "UpdateSecretVersionStageRequestRequestTypeDef",
    {
        "SecretId": str,
        "VersionStage": str,
        "RemoveFromVersionId": NotRequired[str],
        "MoveToVersionId": NotRequired[str],
    },
)
ValidateResourcePolicyRequestRequestTypeDef = TypedDict(
    "ValidateResourcePolicyRequestRequestTypeDef",
    {
        "ResourcePolicy": str,
        "SecretId": NotRequired[str],
    },
)
ValidationErrorsEntryTypeDef = TypedDict(
    "ValidationErrorsEntryTypeDef",
    {
        "CheckName": NotRequired[str],
        "ErrorMessage": NotRequired[str],
    },
)
BatchGetSecretValueRequestRequestTypeDef = TypedDict(
    "BatchGetSecretValueRequestRequestTypeDef",
    {
        "SecretIdList": NotRequired[Sequence[str]],
        "Filters": NotRequired[Sequence[FilterTypeDef]],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListSecretsRequestRequestTypeDef = TypedDict(
    "ListSecretsRequestRequestTypeDef",
    {
        "IncludePlannedDeletion": NotRequired[bool],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "Filters": NotRequired[Sequence[FilterTypeDef]],
        "SortOrder": NotRequired[SortOrderTypeType],
    },
)
CancelRotateSecretResponseTypeDef = TypedDict(
    "CancelRotateSecretResponseTypeDef",
    {
        "ARN": str,
        "Name": str,
        "VersionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteResourcePolicyResponseTypeDef = TypedDict(
    "DeleteResourcePolicyResponseTypeDef",
    {
        "ARN": str,
        "Name": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteSecretResponseTypeDef = TypedDict(
    "DeleteSecretResponseTypeDef",
    {
        "ARN": str,
        "Name": str,
        "DeletionDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetRandomPasswordResponseTypeDef = TypedDict(
    "GetRandomPasswordResponseTypeDef",
    {
        "RandomPassword": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetResourcePolicyResponseTypeDef = TypedDict(
    "GetResourcePolicyResponseTypeDef",
    {
        "ARN": str,
        "Name": str,
        "ResourcePolicy": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetSecretValueResponseTypeDef = TypedDict(
    "GetSecretValueResponseTypeDef",
    {
        "ARN": str,
        "Name": str,
        "VersionId": str,
        "SecretBinary": bytes,
        "SecretString": str,
        "VersionStages": List[str],
        "CreatedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutResourcePolicyResponseTypeDef = TypedDict(
    "PutResourcePolicyResponseTypeDef",
    {
        "ARN": str,
        "Name": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutSecretValueResponseTypeDef = TypedDict(
    "PutSecretValueResponseTypeDef",
    {
        "ARN": str,
        "Name": str,
        "VersionId": str,
        "VersionStages": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RestoreSecretResponseTypeDef = TypedDict(
    "RestoreSecretResponseTypeDef",
    {
        "ARN": str,
        "Name": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RotateSecretResponseTypeDef = TypedDict(
    "RotateSecretResponseTypeDef",
    {
        "ARN": str,
        "Name": str,
        "VersionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StopReplicationToReplicaResponseTypeDef = TypedDict(
    "StopReplicationToReplicaResponseTypeDef",
    {
        "ARN": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateSecretResponseTypeDef = TypedDict(
    "UpdateSecretResponseTypeDef",
    {
        "ARN": str,
        "Name": str,
        "VersionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateSecretVersionStageResponseTypeDef = TypedDict(
    "UpdateSecretVersionStageResponseTypeDef",
    {
        "ARN": str,
        "Name": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchGetSecretValueResponseTypeDef = TypedDict(
    "BatchGetSecretValueResponseTypeDef",
    {
        "SecretValues": List[SecretValueEntryTypeDef],
        "Errors": List[APIErrorTypeTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
PutSecretValueRequestRequestTypeDef = TypedDict(
    "PutSecretValueRequestRequestTypeDef",
    {
        "SecretId": str,
        "ClientRequestToken": NotRequired[str],
        "SecretBinary": NotRequired[BlobTypeDef],
        "SecretString": NotRequired[str],
        "VersionStages": NotRequired[Sequence[str]],
        "RotationToken": NotRequired[str],
    },
)
UpdateSecretRequestRequestTypeDef = TypedDict(
    "UpdateSecretRequestRequestTypeDef",
    {
        "SecretId": str,
        "ClientRequestToken": NotRequired[str],
        "Description": NotRequired[str],
        "KmsKeyId": NotRequired[str],
        "SecretBinary": NotRequired[BlobTypeDef],
        "SecretString": NotRequired[str],
    },
)
ReplicateSecretToRegionsRequestRequestTypeDef = TypedDict(
    "ReplicateSecretToRegionsRequestRequestTypeDef",
    {
        "SecretId": str,
        "AddReplicaRegions": Sequence[ReplicaRegionTypeTypeDef],
        "ForceOverwriteReplicaSecret": NotRequired[bool],
    },
)
CreateSecretRequestRequestTypeDef = TypedDict(
    "CreateSecretRequestRequestTypeDef",
    {
        "Name": str,
        "ClientRequestToken": NotRequired[str],
        "Description": NotRequired[str],
        "KmsKeyId": NotRequired[str],
        "SecretBinary": NotRequired[BlobTypeDef],
        "SecretString": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "AddReplicaRegions": NotRequired[Sequence[ReplicaRegionTypeTypeDef]],
        "ForceOverwriteReplicaSecret": NotRequired[bool],
    },
)
TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "SecretId": str,
        "Tags": Sequence[TagTypeDef],
    },
)
CreateSecretResponseTypeDef = TypedDict(
    "CreateSecretResponseTypeDef",
    {
        "ARN": str,
        "Name": str,
        "VersionId": str,
        "ReplicationStatus": List[ReplicationStatusTypeTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RemoveRegionsFromReplicationResponseTypeDef = TypedDict(
    "RemoveRegionsFromReplicationResponseTypeDef",
    {
        "ARN": str,
        "ReplicationStatus": List[ReplicationStatusTypeTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ReplicateSecretToRegionsResponseTypeDef = TypedDict(
    "ReplicateSecretToRegionsResponseTypeDef",
    {
        "ARN": str,
        "ReplicationStatus": List[ReplicationStatusTypeTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeSecretResponseTypeDef = TypedDict(
    "DescribeSecretResponseTypeDef",
    {
        "ARN": str,
        "Name": str,
        "Description": str,
        "KmsKeyId": str,
        "RotationEnabled": bool,
        "RotationLambdaARN": str,
        "RotationRules": RotationRulesTypeTypeDef,
        "LastRotatedDate": datetime,
        "LastChangedDate": datetime,
        "LastAccessedDate": datetime,
        "DeletedDate": datetime,
        "NextRotationDate": datetime,
        "Tags": List[TagTypeDef],
        "VersionIdsToStages": Dict[str, List[str]],
        "OwningService": str,
        "CreatedDate": datetime,
        "PrimaryRegion": str,
        "ReplicationStatus": List[ReplicationStatusTypeTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RotateSecretRequestRequestTypeDef = TypedDict(
    "RotateSecretRequestRequestTypeDef",
    {
        "SecretId": str,
        "ClientRequestToken": NotRequired[str],
        "RotationLambdaARN": NotRequired[str],
        "RotationRules": NotRequired[RotationRulesTypeTypeDef],
        "RotateImmediately": NotRequired[bool],
    },
)
SecretListEntryTypeDef = TypedDict(
    "SecretListEntryTypeDef",
    {
        "ARN": NotRequired[str],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "KmsKeyId": NotRequired[str],
        "RotationEnabled": NotRequired[bool],
        "RotationLambdaARN": NotRequired[str],
        "RotationRules": NotRequired[RotationRulesTypeTypeDef],
        "LastRotatedDate": NotRequired[datetime],
        "LastChangedDate": NotRequired[datetime],
        "LastAccessedDate": NotRequired[datetime],
        "DeletedDate": NotRequired[datetime],
        "NextRotationDate": NotRequired[datetime],
        "Tags": NotRequired[List[TagTypeDef]],
        "SecretVersionsToStages": NotRequired[Dict[str, List[str]]],
        "OwningService": NotRequired[str],
        "CreatedDate": NotRequired[datetime],
        "PrimaryRegion": NotRequired[str],
    },
)
ListSecretVersionIdsResponseTypeDef = TypedDict(
    "ListSecretVersionIdsResponseTypeDef",
    {
        "Versions": List[SecretVersionsListEntryTypeDef],
        "ARN": str,
        "Name": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
ListSecretsRequestListSecretsPaginateTypeDef = TypedDict(
    "ListSecretsRequestListSecretsPaginateTypeDef",
    {
        "IncludePlannedDeletion": NotRequired[bool],
        "Filters": NotRequired[Sequence[FilterTypeDef]],
        "SortOrder": NotRequired[SortOrderTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ValidateResourcePolicyResponseTypeDef = TypedDict(
    "ValidateResourcePolicyResponseTypeDef",
    {
        "PolicyValidationPassed": bool,
        "ValidationErrors": List[ValidationErrorsEntryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListSecretsResponseTypeDef = TypedDict(
    "ListSecretsResponseTypeDef",
    {
        "SecretList": List[SecretListEntryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "NextToken": NotRequired[str],
    },
)
