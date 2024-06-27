"""
Type annotations for s3 service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/type_defs/)

Usage::

    ```python
    from mypy_boto3_s3.type_defs import AbortIncompleteMultipartUploadTypeDef

    data: AbortIncompleteMultipartUploadTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import IO, Any, Callable, Dict, List, Mapping, Optional, Sequence, Union

from boto3.s3.transfer import TransferConfig
from botocore.client import BaseClient
from botocore.eventstream import EventStream
from botocore.response import StreamingBody

from .literals import (
    ArchiveStatusType,
    BucketAccelerateStatusType,
    BucketCannedACLType,
    BucketLocationConstraintType,
    BucketLogsPermissionType,
    BucketVersioningStatusType,
    ChecksumAlgorithmType,
    CompressionTypeType,
    DeleteMarkerReplicationStatusType,
    EventType,
    ExistingObjectReplicationStatusType,
    ExpirationStatusType,
    FileHeaderInfoType,
    FilterRuleNameType,
    IntelligentTieringAccessTierType,
    IntelligentTieringStatusType,
    InventoryFormatType,
    InventoryFrequencyType,
    InventoryIncludedObjectVersionsType,
    InventoryOptionalFieldType,
    JSONTypeType,
    MetadataDirectiveType,
    MetricsStatusType,
    MFADeleteStatusType,
    MFADeleteType,
    ObjectAttributesType,
    ObjectCannedACLType,
    ObjectLockLegalHoldStatusType,
    ObjectLockModeType,
    ObjectLockRetentionModeType,
    ObjectOwnershipType,
    ObjectStorageClassType,
    PartitionDateSourceType,
    PayerType,
    PermissionType,
    ProtocolType,
    QuoteFieldsType,
    ReplicaModificationsStatusType,
    ReplicationRuleStatusType,
    ReplicationStatusType,
    ReplicationTimeStatusType,
    ServerSideEncryptionType,
    SessionModeType,
    SseKmsEncryptedObjectsStatusType,
    StorageClassType,
    TaggingDirectiveType,
    TierType,
    TransitionStorageClassType,
    TypeType,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "AbortIncompleteMultipartUploadTypeDef",
    "ResponseMetadataTypeDef",
    "AbortMultipartUploadRequestMultipartUploadAbortTypeDef",
    "AbortMultipartUploadRequestRequestTypeDef",
    "AccelerateConfigurationTypeDef",
    "OwnerTypeDef",
    "AccessControlTranslationTypeDef",
    "TagTypeDef",
    "AnalyticsS3BucketDestinationTypeDef",
    "BlobTypeDef",
    "CopySourceTypeDef",
    "BucketDownloadFileRequestTypeDef",
    "FileobjTypeDef",
    "BucketInfoTypeDef",
    "BucketTypeDef",
    "BucketUploadFileRequestTypeDef",
    "CORSRuleTypeDef",
    "CORSRuleExtraOutputTypeDef",
    "CORSRuleOutputTypeDef",
    "CSVInputTypeDef",
    "CSVOutputTypeDef",
    "ChecksumTypeDef",
    "ClientDownloadFileRequestTypeDef",
    "ClientGeneratePresignedPostRequestTypeDef",
    "ClientUploadFileRequestTypeDef",
    "CloudFunctionConfigurationOutputTypeDef",
    "CloudFunctionConfigurationTypeDef",
    "CommonPrefixTypeDef",
    "CompletedPartTypeDef",
    "ConditionTypeDef",
    "CopyObjectResultTypeDef",
    "TimestampTypeDef",
    "CopyPartResultTypeDef",
    "LocationInfoTypeDef",
    "SessionCredentialsTypeDef",
    "CreateSessionRequestRequestTypeDef",
    "DefaultRetentionTypeDef",
    "DeleteBucketAnalyticsConfigurationRequestRequestTypeDef",
    "DeleteBucketCorsRequestBucketCorsDeleteTypeDef",
    "DeleteBucketCorsRequestRequestTypeDef",
    "DeleteBucketEncryptionRequestRequestTypeDef",
    "DeleteBucketIntelligentTieringConfigurationRequestRequestTypeDef",
    "DeleteBucketInventoryConfigurationRequestRequestTypeDef",
    "DeleteBucketLifecycleRequestBucketLifecycleConfigurationDeleteTypeDef",
    "DeleteBucketLifecycleRequestBucketLifecycleDeleteTypeDef",
    "DeleteBucketLifecycleRequestRequestTypeDef",
    "DeleteBucketMetricsConfigurationRequestRequestTypeDef",
    "DeleteBucketOwnershipControlsRequestRequestTypeDef",
    "DeleteBucketPolicyRequestBucketPolicyDeleteTypeDef",
    "DeleteBucketPolicyRequestRequestTypeDef",
    "DeleteBucketReplicationRequestRequestTypeDef",
    "DeleteBucketRequestBucketDeleteTypeDef",
    "DeleteBucketRequestRequestTypeDef",
    "DeleteBucketTaggingRequestBucketTaggingDeleteTypeDef",
    "DeleteBucketTaggingRequestRequestTypeDef",
    "DeleteBucketWebsiteRequestBucketWebsiteDeleteTypeDef",
    "DeleteBucketWebsiteRequestRequestTypeDef",
    "DeleteMarkerReplicationTypeDef",
    "DeleteObjectRequestObjectDeleteTypeDef",
    "DeleteObjectRequestObjectSummaryDeleteTypeDef",
    "DeleteObjectRequestObjectVersionDeleteTypeDef",
    "DeleteObjectRequestRequestTypeDef",
    "DeleteObjectTaggingRequestRequestTypeDef",
    "DeletedObjectTypeDef",
    "ErrorTypeDef",
    "DeletePublicAccessBlockRequestRequestTypeDef",
    "ObjectIdentifierTypeDef",
    "EncryptionConfigurationTypeDef",
    "EncryptionTypeDef",
    "ErrorDocumentTypeDef",
    "ExistingObjectReplicationTypeDef",
    "FilterRuleTypeDef",
    "GetBucketAccelerateConfigurationRequestRequestTypeDef",
    "GetBucketAclRequestRequestTypeDef",
    "GetBucketAnalyticsConfigurationRequestRequestTypeDef",
    "GetBucketCorsRequestRequestTypeDef",
    "GetBucketEncryptionRequestRequestTypeDef",
    "GetBucketIntelligentTieringConfigurationRequestRequestTypeDef",
    "GetBucketInventoryConfigurationRequestRequestTypeDef",
    "GetBucketLifecycleConfigurationRequestRequestTypeDef",
    "GetBucketLifecycleRequestRequestTypeDef",
    "GetBucketLocationRequestRequestTypeDef",
    "GetBucketLoggingRequestRequestTypeDef",
    "GetBucketMetricsConfigurationRequestRequestTypeDef",
    "GetBucketNotificationConfigurationRequestRequestTypeDef",
    "GetBucketOwnershipControlsRequestRequestTypeDef",
    "GetBucketPolicyRequestRequestTypeDef",
    "PolicyStatusTypeDef",
    "GetBucketPolicyStatusRequestRequestTypeDef",
    "GetBucketReplicationRequestRequestTypeDef",
    "GetBucketRequestPaymentRequestRequestTypeDef",
    "GetBucketTaggingRequestRequestTypeDef",
    "GetBucketVersioningRequestRequestTypeDef",
    "IndexDocumentTypeDef",
    "RedirectAllRequestsToTypeDef",
    "GetBucketWebsiteRequestRequestTypeDef",
    "GetObjectAclRequestRequestTypeDef",
    "ObjectPartTypeDef",
    "GetObjectAttributesRequestRequestTypeDef",
    "ObjectLockLegalHoldTypeDef",
    "GetObjectLegalHoldRequestRequestTypeDef",
    "GetObjectLockConfigurationRequestRequestTypeDef",
    "ObjectLockRetentionOutputTypeDef",
    "GetObjectRetentionRequestRequestTypeDef",
    "GetObjectTaggingRequestRequestTypeDef",
    "GetObjectTorrentRequestRequestTypeDef",
    "PublicAccessBlockConfigurationTypeDef",
    "GetPublicAccessBlockRequestRequestTypeDef",
    "GlacierJobParametersTypeDef",
    "GranteeTypeDef",
    "WaiterConfigTypeDef",
    "HeadBucketRequestRequestTypeDef",
    "InitiatorTypeDef",
    "JSONInputTypeDef",
    "TieringTypeDef",
    "InventoryFilterTypeDef",
    "InventoryScheduleTypeDef",
    "SSEKMSTypeDef",
    "JSONOutputTypeDef",
    "LifecycleExpirationExtraExtraOutputTypeDef",
    "LifecycleExpirationExtraOutputTypeDef",
    "LifecycleExpirationOutputTypeDef",
    "NoncurrentVersionExpirationTypeDef",
    "NoncurrentVersionTransitionTypeDef",
    "TransitionExtraOutputTypeDef",
    "TransitionOutputTypeDef",
    "ListBucketAnalyticsConfigurationsRequestRequestTypeDef",
    "ListBucketIntelligentTieringConfigurationsRequestRequestTypeDef",
    "ListBucketInventoryConfigurationsRequestRequestTypeDef",
    "ListBucketMetricsConfigurationsRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "ListDirectoryBucketsRequestRequestTypeDef",
    "ListMultipartUploadsRequestRequestTypeDef",
    "ListObjectVersionsRequestRequestTypeDef",
    "ListObjectsRequestRequestTypeDef",
    "ListObjectsV2RequestRequestTypeDef",
    "PartTypeDef",
    "ListPartsRequestRequestTypeDef",
    "MetadataEntryTypeDef",
    "ReplicationTimeValueTypeDef",
    "QueueConfigurationDeprecatedOutputTypeDef",
    "TopicConfigurationDeprecatedOutputTypeDef",
    "QueueConfigurationDeprecatedTypeDef",
    "TopicConfigurationDeprecatedTypeDef",
    "ObjectDownloadFileRequestTypeDef",
    "RestoreStatusTypeDef",
    "ObjectUploadFileRequestTypeDef",
    "OwnershipControlsRuleTypeDef",
    "PartitionedPrefixTypeDef",
    "ProgressTypeDef",
    "PutBucketPolicyRequestBucketPolicyPutTypeDef",
    "PutBucketPolicyRequestRequestTypeDef",
    "RequestPaymentConfigurationTypeDef",
    "PutBucketVersioningRequestBucketVersioningEnableTypeDef",
    "VersioningConfigurationTypeDef",
    "PutBucketVersioningRequestBucketVersioningSuspendTypeDef",
    "RecordsEventTypeDef",
    "RedirectTypeDef",
    "ReplicaModificationsTypeDef",
    "RequestProgressTypeDef",
    "TransitionExtraExtraOutputTypeDef",
    "ScanRangeTypeDef",
    "ServerSideEncryptionByDefaultTypeDef",
    "SseKmsEncryptedObjectsTypeDef",
    "StatsTypeDef",
    "AbortMultipartUploadOutputTypeDef",
    "CompleteMultipartUploadOutputTypeDef",
    "CreateBucketOutputTypeDef",
    "CreateMultipartUploadOutputTypeDef",
    "DeleteObjectOutputTypeDef",
    "DeleteObjectTaggingOutputTypeDef",
    "EmptyResponseMetadataTypeDef",
    "ErrorDocumentResponseTypeDef",
    "GetBucketAccelerateConfigurationOutputTypeDef",
    "GetBucketLocationOutputTypeDef",
    "GetBucketPolicyOutputTypeDef",
    "GetBucketRequestPaymentOutputTypeDef",
    "GetBucketVersioningOutputTypeDef",
    "GetObjectOutputTypeDef",
    "GetObjectTorrentOutputTypeDef",
    "HeadBucketOutputTypeDef",
    "HeadObjectOutputTypeDef",
    "IndexDocumentResponseTypeDef",
    "InitiatorResponseTypeDef",
    "OwnerResponseTypeDef",
    "PutObjectAclOutputTypeDef",
    "PutObjectLegalHoldOutputTypeDef",
    "PutObjectLockConfigurationOutputTypeDef",
    "PutObjectOutputTypeDef",
    "PutObjectRetentionOutputTypeDef",
    "PutObjectTaggingOutputTypeDef",
    "RedirectAllRequestsToResponseTypeDef",
    "RestoreObjectOutputTypeDef",
    "RestoreStatusResponseTypeDef",
    "UploadPartOutputTypeDef",
    "PutBucketAccelerateConfigurationRequestRequestTypeDef",
    "DeleteMarkerEntryTypeDef",
    "AnalyticsAndOperatorOutputTypeDef",
    "AnalyticsAndOperatorTypeDef",
    "GetBucketTaggingOutputTypeDef",
    "GetObjectTaggingOutputTypeDef",
    "IntelligentTieringAndOperatorOutputTypeDef",
    "IntelligentTieringAndOperatorTypeDef",
    "LifecycleRuleAndOperatorExtraOutputTypeDef",
    "LifecycleRuleAndOperatorOutputTypeDef",
    "LifecycleRuleAndOperatorTypeDef",
    "MetricsAndOperatorOutputTypeDef",
    "MetricsAndOperatorTypeDef",
    "ReplicationRuleAndOperatorOutputTypeDef",
    "ReplicationRuleAndOperatorTypeDef",
    "TaggingTypeDef",
    "AnalyticsExportDestinationTypeDef",
    "UploadPartRequestMultipartUploadPartUploadTypeDef",
    "UploadPartRequestRequestTypeDef",
    "BucketCopyRequestTypeDef",
    "ClientCopyRequestTypeDef",
    "CopySourceOrStrTypeDef",
    "ObjectCopyRequestTypeDef",
    "BucketDownloadFileobjRequestTypeDef",
    "BucketUploadFileobjRequestTypeDef",
    "ClientDownloadFileobjRequestTypeDef",
    "ClientUploadFileobjRequestTypeDef",
    "ObjectDownloadFileobjRequestTypeDef",
    "ObjectUploadFileobjRequestTypeDef",
    "ListBucketsOutputTypeDef",
    "ListDirectoryBucketsOutputTypeDef",
    "CORSConfigurationTypeDef",
    "GetBucketCorsOutputTypeDef",
    "CompletedMultipartUploadTypeDef",
    "CopyObjectOutputTypeDef",
    "CopyObjectRequestObjectCopyFromTypeDef",
    "CopyObjectRequestObjectSummaryCopyFromTypeDef",
    "CreateMultipartUploadRequestObjectInitiateMultipartUploadTypeDef",
    "CreateMultipartUploadRequestObjectSummaryInitiateMultipartUploadTypeDef",
    "CreateMultipartUploadRequestRequestTypeDef",
    "GetObjectRequestObjectGetTypeDef",
    "GetObjectRequestObjectSummaryGetTypeDef",
    "GetObjectRequestObjectVersionGetTypeDef",
    "GetObjectRequestRequestTypeDef",
    "HeadObjectRequestObjectVersionHeadTypeDef",
    "HeadObjectRequestRequestTypeDef",
    "LifecycleExpirationTypeDef",
    "ObjectLockRetentionTypeDef",
    "PutObjectRequestBucketPutObjectTypeDef",
    "PutObjectRequestObjectPutTypeDef",
    "PutObjectRequestObjectSummaryPutTypeDef",
    "PutObjectRequestRequestTypeDef",
    "TransitionTypeDef",
    "WriteGetObjectResponseRequestRequestTypeDef",
    "UploadPartCopyOutputTypeDef",
    "CreateBucketConfigurationTypeDef",
    "CreateSessionOutputTypeDef",
    "ObjectLockRuleTypeDef",
    "DeleteObjectsOutputTypeDef",
    "DeleteTypeDef",
    "S3KeyFilterExtraOutputTypeDef",
    "S3KeyFilterOutputTypeDef",
    "S3KeyFilterTypeDef",
    "GetBucketPolicyStatusOutputTypeDef",
    "GetObjectAttributesPartsTypeDef",
    "GetObjectLegalHoldOutputTypeDef",
    "PutObjectLegalHoldRequestRequestTypeDef",
    "GetObjectRetentionOutputTypeDef",
    "GetPublicAccessBlockOutputTypeDef",
    "PutPublicAccessBlockRequestRequestTypeDef",
    "GrantTypeDef",
    "TargetGrantTypeDef",
    "HeadBucketRequestBucketExistsWaitTypeDef",
    "HeadBucketRequestBucketNotExistsWaitTypeDef",
    "HeadObjectRequestObjectExistsWaitTypeDef",
    "HeadObjectRequestObjectNotExistsWaitTypeDef",
    "MultipartUploadTypeDef",
    "InputSerializationTypeDef",
    "InventoryEncryptionOutputTypeDef",
    "InventoryEncryptionTypeDef",
    "OutputSerializationTypeDef",
    "RuleOutputTypeDef",
    "ListDirectoryBucketsRequestListDirectoryBucketsPaginateTypeDef",
    "ListMultipartUploadsRequestListMultipartUploadsPaginateTypeDef",
    "ListObjectVersionsRequestListObjectVersionsPaginateTypeDef",
    "ListObjectsRequestListObjectsPaginateTypeDef",
    "ListObjectsV2RequestListObjectsV2PaginateTypeDef",
    "ListPartsRequestListPartsPaginateTypeDef",
    "ListPartsOutputTypeDef",
    "MetricsTypeDef",
    "ReplicationTimeTypeDef",
    "NotificationConfigurationDeprecatedResponseTypeDef",
    "NotificationConfigurationDeprecatedTypeDef",
    "ObjectTypeDef",
    "ObjectVersionTypeDef",
    "OwnershipControlsOutputTypeDef",
    "OwnershipControlsTypeDef",
    "TargetObjectKeyFormatExtraOutputTypeDef",
    "TargetObjectKeyFormatOutputTypeDef",
    "TargetObjectKeyFormatTypeDef",
    "ProgressEventTypeDef",
    "PutBucketRequestPaymentRequestBucketRequestPaymentPutTypeDef",
    "PutBucketRequestPaymentRequestRequestTypeDef",
    "PutBucketVersioningRequestBucketVersioningPutTypeDef",
    "PutBucketVersioningRequestRequestTypeDef",
    "RoutingRuleTypeDef",
    "RuleExtraOutputTypeDef",
    "ServerSideEncryptionRuleTypeDef",
    "SourceSelectionCriteriaTypeDef",
    "StatsEventTypeDef",
    "AnalyticsFilterOutputTypeDef",
    "AnalyticsFilterTypeDef",
    "IntelligentTieringFilterOutputTypeDef",
    "IntelligentTieringFilterTypeDef",
    "LifecycleRuleFilterExtraOutputTypeDef",
    "LifecycleRuleFilterOutputTypeDef",
    "LifecycleRuleFilterTypeDef",
    "MetricsFilterOutputTypeDef",
    "MetricsFilterTypeDef",
    "ReplicationRuleFilterOutputTypeDef",
    "ReplicationRuleFilterTypeDef",
    "PutBucketTaggingRequestBucketTaggingPutTypeDef",
    "PutBucketTaggingRequestRequestTypeDef",
    "PutObjectTaggingRequestRequestTypeDef",
    "StorageClassAnalysisDataExportTypeDef",
    "CopyObjectRequestRequestTypeDef",
    "UploadPartCopyRequestMultipartUploadPartCopyFromTypeDef",
    "UploadPartCopyRequestRequestTypeDef",
    "PutBucketCorsRequestBucketCorsPutTypeDef",
    "PutBucketCorsRequestRequestTypeDef",
    "CompleteMultipartUploadRequestMultipartUploadCompleteTypeDef",
    "CompleteMultipartUploadRequestRequestTypeDef",
    "ObjectLockRetentionUnionTypeDef",
    "PutObjectRetentionRequestRequestTypeDef",
    "RuleTypeDef",
    "CreateBucketRequestBucketCreateTypeDef",
    "CreateBucketRequestRequestTypeDef",
    "CreateBucketRequestServiceResourceCreateBucketTypeDef",
    "ObjectLockConfigurationTypeDef",
    "DeleteObjectsRequestBucketDeleteObjectsTypeDef",
    "DeleteObjectsRequestRequestTypeDef",
    "NotificationConfigurationFilterExtraOutputTypeDef",
    "NotificationConfigurationFilterOutputTypeDef",
    "NotificationConfigurationFilterTypeDef",
    "GetObjectAttributesOutputTypeDef",
    "AccessControlPolicyTypeDef",
    "GetBucketAclOutputTypeDef",
    "GetObjectAclOutputTypeDef",
    "S3LocationTypeDef",
    "ListMultipartUploadsOutputTypeDef",
    "InventoryS3BucketDestinationOutputTypeDef",
    "InventoryS3BucketDestinationTypeDef",
    "SelectObjectContentRequestRequestTypeDef",
    "SelectParametersTypeDef",
    "GetBucketLifecycleOutputTypeDef",
    "DestinationTypeDef",
    "PutBucketNotificationRequestRequestTypeDef",
    "ListObjectsOutputTypeDef",
    "ListObjectsV2OutputTypeDef",
    "ListObjectVersionsOutputTypeDef",
    "GetBucketOwnershipControlsOutputTypeDef",
    "OwnershipControlsUnionTypeDef",
    "PutBucketOwnershipControlsRequestRequestTypeDef",
    "LoggingEnabledResponseTypeDef",
    "LoggingEnabledOutputTypeDef",
    "LoggingEnabledTypeDef",
    "GetBucketWebsiteOutputTypeDef",
    "WebsiteConfigurationTypeDef",
    "ServerSideEncryptionConfigurationOutputTypeDef",
    "ServerSideEncryptionConfigurationTypeDef",
    "SelectObjectContentEventStreamTypeDef",
    "IntelligentTieringConfigurationOutputTypeDef",
    "IntelligentTieringConfigurationTypeDef",
    "LifecycleRuleExtraOutputTypeDef",
    "LifecycleRuleOutputTypeDef",
    "LifecycleRuleTypeDef",
    "MetricsConfigurationOutputTypeDef",
    "MetricsConfigurationTypeDef",
    "StorageClassAnalysisTypeDef",
    "LifecycleConfigurationTypeDef",
    "GetObjectLockConfigurationOutputTypeDef",
    "PutObjectLockConfigurationRequestRequestTypeDef",
    "LambdaFunctionConfigurationExtraOutputTypeDef",
    "QueueConfigurationExtraOutputTypeDef",
    "TopicConfigurationExtraOutputTypeDef",
    "LambdaFunctionConfigurationOutputTypeDef",
    "QueueConfigurationOutputTypeDef",
    "TopicConfigurationOutputTypeDef",
    "LambdaFunctionConfigurationTypeDef",
    "QueueConfigurationTypeDef",
    "TopicConfigurationTypeDef",
    "PutBucketAclRequestBucketAclPutTypeDef",
    "PutBucketAclRequestRequestTypeDef",
    "PutObjectAclRequestObjectAclPutTypeDef",
    "PutObjectAclRequestRequestTypeDef",
    "OutputLocationTypeDef",
    "InventoryDestinationOutputTypeDef",
    "InventoryDestinationTypeDef",
    "ReplicationRuleOutputTypeDef",
    "ReplicationRuleTypeDef",
    "GetBucketLoggingOutputTypeDef",
    "BucketLoggingStatusTypeDef",
    "PutBucketWebsiteRequestBucketWebsitePutTypeDef",
    "PutBucketWebsiteRequestRequestTypeDef",
    "GetBucketEncryptionOutputTypeDef",
    "PutBucketEncryptionRequestRequestTypeDef",
    "ServerSideEncryptionConfigurationUnionTypeDef",
    "SelectObjectContentOutputTypeDef",
    "GetBucketIntelligentTieringConfigurationOutputTypeDef",
    "ListBucketIntelligentTieringConfigurationsOutputTypeDef",
    "IntelligentTieringConfigurationUnionTypeDef",
    "PutBucketIntelligentTieringConfigurationRequestRequestTypeDef",
    "GetBucketLifecycleConfigurationOutputTypeDef",
    "BucketLifecycleConfigurationTypeDef",
    "GetBucketMetricsConfigurationOutputTypeDef",
    "ListBucketMetricsConfigurationsOutputTypeDef",
    "MetricsConfigurationUnionTypeDef",
    "PutBucketMetricsConfigurationRequestRequestTypeDef",
    "AnalyticsConfigurationOutputTypeDef",
    "AnalyticsConfigurationTypeDef",
    "PutBucketLifecycleRequestBucketLifecyclePutTypeDef",
    "PutBucketLifecycleRequestRequestTypeDef",
    "NotificationConfigurationResponseTypeDef",
    "NotificationConfigurationTypeDef",
    "RestoreRequestTypeDef",
    "InventoryConfigurationOutputTypeDef",
    "InventoryConfigurationTypeDef",
    "ReplicationConfigurationOutputTypeDef",
    "ReplicationConfigurationTypeDef",
    "PutBucketLoggingRequestBucketLoggingPutTypeDef",
    "PutBucketLoggingRequestRequestTypeDef",
    "PutBucketLifecycleConfigurationRequestBucketLifecycleConfigurationPutTypeDef",
    "PutBucketLifecycleConfigurationRequestRequestTypeDef",
    "GetBucketAnalyticsConfigurationOutputTypeDef",
    "ListBucketAnalyticsConfigurationsOutputTypeDef",
    "AnalyticsConfigurationUnionTypeDef",
    "PutBucketAnalyticsConfigurationRequestRequestTypeDef",
    "PutBucketNotificationConfigurationRequestBucketNotificationPutTypeDef",
    "PutBucketNotificationConfigurationRequestRequestTypeDef",
    "RestoreObjectRequestObjectRestoreObjectTypeDef",
    "RestoreObjectRequestObjectSummaryRestoreObjectTypeDef",
    "RestoreObjectRequestRequestTypeDef",
    "GetBucketInventoryConfigurationOutputTypeDef",
    "ListBucketInventoryConfigurationsOutputTypeDef",
    "InventoryConfigurationUnionTypeDef",
    "PutBucketInventoryConfigurationRequestRequestTypeDef",
    "GetBucketReplicationOutputTypeDef",
    "PutBucketReplicationRequestRequestTypeDef",
    "ReplicationConfigurationUnionTypeDef",
)

AbortIncompleteMultipartUploadTypeDef = TypedDict(
    "AbortIncompleteMultipartUploadTypeDef",
    {
        "DaysAfterInitiation": NotRequired[int],
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
AbortMultipartUploadRequestMultipartUploadAbortTypeDef = TypedDict(
    "AbortMultipartUploadRequestMultipartUploadAbortTypeDef",
    {
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
AbortMultipartUploadRequestRequestTypeDef = TypedDict(
    "AbortMultipartUploadRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "UploadId": str,
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
AccelerateConfigurationTypeDef = TypedDict(
    "AccelerateConfigurationTypeDef",
    {
        "Status": NotRequired[BucketAccelerateStatusType],
    },
)
OwnerTypeDef = TypedDict(
    "OwnerTypeDef",
    {
        "DisplayName": NotRequired[str],
        "ID": NotRequired[str],
    },
)
AccessControlTranslationTypeDef = TypedDict(
    "AccessControlTranslationTypeDef",
    {
        "Owner": Literal["Destination"],
    },
)
TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
)
AnalyticsS3BucketDestinationTypeDef = TypedDict(
    "AnalyticsS3BucketDestinationTypeDef",
    {
        "Format": Literal["CSV"],
        "Bucket": str,
        "BucketAccountId": NotRequired[str],
        "Prefix": NotRequired[str],
    },
)
BlobTypeDef = Union[str, bytes, IO[Any], StreamingBody]
CopySourceTypeDef = TypedDict(
    "CopySourceTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "VersionId": NotRequired[str],
    },
)
BucketDownloadFileRequestTypeDef = TypedDict(
    "BucketDownloadFileRequestTypeDef",
    {
        "Key": str,
        "Filename": str,
        "ExtraArgs": NotRequired[Optional[Dict[str, Any]]],
        "Callback": NotRequired[Optional[Callable[..., Any]]],
        "Config": NotRequired[Optional[TransferConfig]],
    },
)
FileobjTypeDef = Union[IO[Any], StreamingBody]
BucketInfoTypeDef = TypedDict(
    "BucketInfoTypeDef",
    {
        "DataRedundancy": NotRequired[Literal["SingleAvailabilityZone"]],
        "Type": NotRequired[Literal["Directory"]],
    },
)
BucketTypeDef = TypedDict(
    "BucketTypeDef",
    {
        "Name": NotRequired[str],
        "CreationDate": NotRequired[datetime],
    },
)
BucketUploadFileRequestTypeDef = TypedDict(
    "BucketUploadFileRequestTypeDef",
    {
        "Filename": str,
        "Key": str,
        "ExtraArgs": NotRequired[Optional[Dict[str, Any]]],
        "Callback": NotRequired[Optional[Callable[..., Any]]],
        "Config": NotRequired[Optional[TransferConfig]],
    },
)
CORSRuleTypeDef = TypedDict(
    "CORSRuleTypeDef",
    {
        "AllowedMethods": Sequence[str],
        "AllowedOrigins": Sequence[str],
        "ID": NotRequired[str],
        "AllowedHeaders": NotRequired[Sequence[str]],
        "ExposeHeaders": NotRequired[Sequence[str]],
        "MaxAgeSeconds": NotRequired[int],
    },
)
CORSRuleExtraOutputTypeDef = TypedDict(
    "CORSRuleExtraOutputTypeDef",
    {
        "AllowedMethods": List[str],
        "AllowedOrigins": List[str],
        "ID": NotRequired[str],
        "AllowedHeaders": NotRequired[List[str]],
        "ExposeHeaders": NotRequired[List[str]],
        "MaxAgeSeconds": NotRequired[int],
    },
)
CORSRuleOutputTypeDef = TypedDict(
    "CORSRuleOutputTypeDef",
    {
        "AllowedMethods": List[str],
        "AllowedOrigins": List[str],
        "ID": NotRequired[str],
        "AllowedHeaders": NotRequired[List[str]],
        "ExposeHeaders": NotRequired[List[str]],
        "MaxAgeSeconds": NotRequired[int],
    },
)
CSVInputTypeDef = TypedDict(
    "CSVInputTypeDef",
    {
        "FileHeaderInfo": NotRequired[FileHeaderInfoType],
        "Comments": NotRequired[str],
        "QuoteEscapeCharacter": NotRequired[str],
        "RecordDelimiter": NotRequired[str],
        "FieldDelimiter": NotRequired[str],
        "QuoteCharacter": NotRequired[str],
        "AllowQuotedRecordDelimiter": NotRequired[bool],
    },
)
CSVOutputTypeDef = TypedDict(
    "CSVOutputTypeDef",
    {
        "QuoteFields": NotRequired[QuoteFieldsType],
        "QuoteEscapeCharacter": NotRequired[str],
        "RecordDelimiter": NotRequired[str],
        "FieldDelimiter": NotRequired[str],
        "QuoteCharacter": NotRequired[str],
    },
)
ChecksumTypeDef = TypedDict(
    "ChecksumTypeDef",
    {
        "ChecksumCRC32": NotRequired[str],
        "ChecksumCRC32C": NotRequired[str],
        "ChecksumSHA1": NotRequired[str],
        "ChecksumSHA256": NotRequired[str],
    },
)
ClientDownloadFileRequestTypeDef = TypedDict(
    "ClientDownloadFileRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "Filename": str,
        "ExtraArgs": NotRequired[Optional[Dict[str, Any]]],
        "Callback": NotRequired[Optional[Callable[..., Any]]],
        "Config": NotRequired[Optional[TransferConfig]],
    },
)
ClientGeneratePresignedPostRequestTypeDef = TypedDict(
    "ClientGeneratePresignedPostRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "Fields": NotRequired[Optional[Dict[str, Any]]],
        "Conditions": NotRequired[Union[List[Any], Dict[str, Any], None]],
        "ExpiresIn": NotRequired[int],
    },
)
ClientUploadFileRequestTypeDef = TypedDict(
    "ClientUploadFileRequestTypeDef",
    {
        "Filename": str,
        "Bucket": str,
        "Key": str,
        "ExtraArgs": NotRequired[Optional[Dict[str, Any]]],
        "Callback": NotRequired[Optional[Callable[..., Any]]],
        "Config": NotRequired[Optional[TransferConfig]],
    },
)
CloudFunctionConfigurationOutputTypeDef = TypedDict(
    "CloudFunctionConfigurationOutputTypeDef",
    {
        "Id": NotRequired[str],
        "Event": NotRequired[EventType],
        "Events": NotRequired[List[EventType]],
        "CloudFunction": NotRequired[str],
        "InvocationRole": NotRequired[str],
    },
)
CloudFunctionConfigurationTypeDef = TypedDict(
    "CloudFunctionConfigurationTypeDef",
    {
        "Id": NotRequired[str],
        "Event": NotRequired[EventType],
        "Events": NotRequired[Sequence[EventType]],
        "CloudFunction": NotRequired[str],
        "InvocationRole": NotRequired[str],
    },
)
CommonPrefixTypeDef = TypedDict(
    "CommonPrefixTypeDef",
    {
        "Prefix": NotRequired[str],
    },
)
CompletedPartTypeDef = TypedDict(
    "CompletedPartTypeDef",
    {
        "ETag": NotRequired[str],
        "ChecksumCRC32": NotRequired[str],
        "ChecksumCRC32C": NotRequired[str],
        "ChecksumSHA1": NotRequired[str],
        "ChecksumSHA256": NotRequired[str],
        "PartNumber": NotRequired[int],
    },
)
ConditionTypeDef = TypedDict(
    "ConditionTypeDef",
    {
        "HttpErrorCodeReturnedEquals": NotRequired[str],
        "KeyPrefixEquals": NotRequired[str],
    },
)
CopyObjectResultTypeDef = TypedDict(
    "CopyObjectResultTypeDef",
    {
        "ETag": NotRequired[str],
        "LastModified": NotRequired[datetime],
        "ChecksumCRC32": NotRequired[str],
        "ChecksumCRC32C": NotRequired[str],
        "ChecksumSHA1": NotRequired[str],
        "ChecksumSHA256": NotRequired[str],
    },
)
TimestampTypeDef = Union[datetime, str]
CopyPartResultTypeDef = TypedDict(
    "CopyPartResultTypeDef",
    {
        "ETag": NotRequired[str],
        "LastModified": NotRequired[datetime],
        "ChecksumCRC32": NotRequired[str],
        "ChecksumCRC32C": NotRequired[str],
        "ChecksumSHA1": NotRequired[str],
        "ChecksumSHA256": NotRequired[str],
    },
)
LocationInfoTypeDef = TypedDict(
    "LocationInfoTypeDef",
    {
        "Type": NotRequired[Literal["AvailabilityZone"]],
        "Name": NotRequired[str],
    },
)
SessionCredentialsTypeDef = TypedDict(
    "SessionCredentialsTypeDef",
    {
        "AccessKeyId": str,
        "SecretAccessKey": str,
        "SessionToken": str,
        "Expiration": datetime,
    },
)
CreateSessionRequestRequestTypeDef = TypedDict(
    "CreateSessionRequestRequestTypeDef",
    {
        "Bucket": str,
        "SessionMode": NotRequired[SessionModeType],
    },
)
DefaultRetentionTypeDef = TypedDict(
    "DefaultRetentionTypeDef",
    {
        "Mode": NotRequired[ObjectLockRetentionModeType],
        "Days": NotRequired[int],
        "Years": NotRequired[int],
    },
)
DeleteBucketAnalyticsConfigurationRequestRequestTypeDef = TypedDict(
    "DeleteBucketAnalyticsConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "Id": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketCorsRequestBucketCorsDeleteTypeDef = TypedDict(
    "DeleteBucketCorsRequestBucketCorsDeleteTypeDef",
    {
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketCorsRequestRequestTypeDef = TypedDict(
    "DeleteBucketCorsRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketEncryptionRequestRequestTypeDef = TypedDict(
    "DeleteBucketEncryptionRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketIntelligentTieringConfigurationRequestRequestTypeDef = TypedDict(
    "DeleteBucketIntelligentTieringConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "Id": str,
    },
)
DeleteBucketInventoryConfigurationRequestRequestTypeDef = TypedDict(
    "DeleteBucketInventoryConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "Id": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketLifecycleRequestBucketLifecycleConfigurationDeleteTypeDef = TypedDict(
    "DeleteBucketLifecycleRequestBucketLifecycleConfigurationDeleteTypeDef",
    {
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketLifecycleRequestBucketLifecycleDeleteTypeDef = TypedDict(
    "DeleteBucketLifecycleRequestBucketLifecycleDeleteTypeDef",
    {
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketLifecycleRequestRequestTypeDef = TypedDict(
    "DeleteBucketLifecycleRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketMetricsConfigurationRequestRequestTypeDef = TypedDict(
    "DeleteBucketMetricsConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "Id": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketOwnershipControlsRequestRequestTypeDef = TypedDict(
    "DeleteBucketOwnershipControlsRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketPolicyRequestBucketPolicyDeleteTypeDef = TypedDict(
    "DeleteBucketPolicyRequestBucketPolicyDeleteTypeDef",
    {
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketPolicyRequestRequestTypeDef = TypedDict(
    "DeleteBucketPolicyRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketReplicationRequestRequestTypeDef = TypedDict(
    "DeleteBucketReplicationRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketRequestBucketDeleteTypeDef = TypedDict(
    "DeleteBucketRequestBucketDeleteTypeDef",
    {
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketRequestRequestTypeDef = TypedDict(
    "DeleteBucketRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketTaggingRequestBucketTaggingDeleteTypeDef = TypedDict(
    "DeleteBucketTaggingRequestBucketTaggingDeleteTypeDef",
    {
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketTaggingRequestRequestTypeDef = TypedDict(
    "DeleteBucketTaggingRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketWebsiteRequestBucketWebsiteDeleteTypeDef = TypedDict(
    "DeleteBucketWebsiteRequestBucketWebsiteDeleteTypeDef",
    {
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteBucketWebsiteRequestRequestTypeDef = TypedDict(
    "DeleteBucketWebsiteRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteMarkerReplicationTypeDef = TypedDict(
    "DeleteMarkerReplicationTypeDef",
    {
        "Status": NotRequired[DeleteMarkerReplicationStatusType],
    },
)
DeleteObjectRequestObjectDeleteTypeDef = TypedDict(
    "DeleteObjectRequestObjectDeleteTypeDef",
    {
        "MFA": NotRequired[str],
        "VersionId": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "BypassGovernanceRetention": NotRequired[bool],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteObjectRequestObjectSummaryDeleteTypeDef = TypedDict(
    "DeleteObjectRequestObjectSummaryDeleteTypeDef",
    {
        "MFA": NotRequired[str],
        "VersionId": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "BypassGovernanceRetention": NotRequired[bool],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteObjectRequestObjectVersionDeleteTypeDef = TypedDict(
    "DeleteObjectRequestObjectVersionDeleteTypeDef",
    {
        "MFA": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "BypassGovernanceRetention": NotRequired[bool],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteObjectRequestRequestTypeDef = TypedDict(
    "DeleteObjectRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "MFA": NotRequired[str],
        "VersionId": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "BypassGovernanceRetention": NotRequired[bool],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeleteObjectTaggingRequestRequestTypeDef = TypedDict(
    "DeleteObjectTaggingRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "VersionId": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
DeletedObjectTypeDef = TypedDict(
    "DeletedObjectTypeDef",
    {
        "Key": NotRequired[str],
        "VersionId": NotRequired[str],
        "DeleteMarker": NotRequired[bool],
        "DeleteMarkerVersionId": NotRequired[str],
    },
)
ErrorTypeDef = TypedDict(
    "ErrorTypeDef",
    {
        "Key": NotRequired[str],
        "VersionId": NotRequired[str],
        "Code": NotRequired[str],
        "Message": NotRequired[str],
    },
)
DeletePublicAccessBlockRequestRequestTypeDef = TypedDict(
    "DeletePublicAccessBlockRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
ObjectIdentifierTypeDef = TypedDict(
    "ObjectIdentifierTypeDef",
    {
        "Key": str,
        "VersionId": NotRequired[str],
    },
)
EncryptionConfigurationTypeDef = TypedDict(
    "EncryptionConfigurationTypeDef",
    {
        "ReplicaKmsKeyID": NotRequired[str],
    },
)
EncryptionTypeDef = TypedDict(
    "EncryptionTypeDef",
    {
        "EncryptionType": ServerSideEncryptionType,
        "KMSKeyId": NotRequired[str],
        "KMSContext": NotRequired[str],
    },
)
ErrorDocumentTypeDef = TypedDict(
    "ErrorDocumentTypeDef",
    {
        "Key": str,
    },
)
ExistingObjectReplicationTypeDef = TypedDict(
    "ExistingObjectReplicationTypeDef",
    {
        "Status": ExistingObjectReplicationStatusType,
    },
)
FilterRuleTypeDef = TypedDict(
    "FilterRuleTypeDef",
    {
        "Name": NotRequired[FilterRuleNameType],
        "Value": NotRequired[str],
    },
)
GetBucketAccelerateConfigurationRequestRequestTypeDef = TypedDict(
    "GetBucketAccelerateConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
    },
)
GetBucketAclRequestRequestTypeDef = TypedDict(
    "GetBucketAclRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketAnalyticsConfigurationRequestRequestTypeDef = TypedDict(
    "GetBucketAnalyticsConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "Id": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketCorsRequestRequestTypeDef = TypedDict(
    "GetBucketCorsRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketEncryptionRequestRequestTypeDef = TypedDict(
    "GetBucketEncryptionRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketIntelligentTieringConfigurationRequestRequestTypeDef = TypedDict(
    "GetBucketIntelligentTieringConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "Id": str,
    },
)
GetBucketInventoryConfigurationRequestRequestTypeDef = TypedDict(
    "GetBucketInventoryConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "Id": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketLifecycleConfigurationRequestRequestTypeDef = TypedDict(
    "GetBucketLifecycleConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketLifecycleRequestRequestTypeDef = TypedDict(
    "GetBucketLifecycleRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketLocationRequestRequestTypeDef = TypedDict(
    "GetBucketLocationRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketLoggingRequestRequestTypeDef = TypedDict(
    "GetBucketLoggingRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketMetricsConfigurationRequestRequestTypeDef = TypedDict(
    "GetBucketMetricsConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "Id": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketNotificationConfigurationRequestRequestTypeDef = TypedDict(
    "GetBucketNotificationConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketOwnershipControlsRequestRequestTypeDef = TypedDict(
    "GetBucketOwnershipControlsRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketPolicyRequestRequestTypeDef = TypedDict(
    "GetBucketPolicyRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PolicyStatusTypeDef = TypedDict(
    "PolicyStatusTypeDef",
    {
        "IsPublic": NotRequired[bool],
    },
)
GetBucketPolicyStatusRequestRequestTypeDef = TypedDict(
    "GetBucketPolicyStatusRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketReplicationRequestRequestTypeDef = TypedDict(
    "GetBucketReplicationRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketRequestPaymentRequestRequestTypeDef = TypedDict(
    "GetBucketRequestPaymentRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketTaggingRequestRequestTypeDef = TypedDict(
    "GetBucketTaggingRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketVersioningRequestRequestTypeDef = TypedDict(
    "GetBucketVersioningRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
IndexDocumentTypeDef = TypedDict(
    "IndexDocumentTypeDef",
    {
        "Suffix": str,
    },
)
RedirectAllRequestsToTypeDef = TypedDict(
    "RedirectAllRequestsToTypeDef",
    {
        "HostName": str,
        "Protocol": NotRequired[ProtocolType],
    },
)
GetBucketWebsiteRequestRequestTypeDef = TypedDict(
    "GetBucketWebsiteRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetObjectAclRequestRequestTypeDef = TypedDict(
    "GetObjectAclRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "VersionId": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
ObjectPartTypeDef = TypedDict(
    "ObjectPartTypeDef",
    {
        "PartNumber": NotRequired[int],
        "Size": NotRequired[int],
        "ChecksumCRC32": NotRequired[str],
        "ChecksumCRC32C": NotRequired[str],
        "ChecksumSHA1": NotRequired[str],
        "ChecksumSHA256": NotRequired[str],
    },
)
GetObjectAttributesRequestRequestTypeDef = TypedDict(
    "GetObjectAttributesRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "ObjectAttributes": Sequence[ObjectAttributesType],
        "VersionId": NotRequired[str],
        "MaxParts": NotRequired[int],
        "PartNumberMarker": NotRequired[int],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
ObjectLockLegalHoldTypeDef = TypedDict(
    "ObjectLockLegalHoldTypeDef",
    {
        "Status": NotRequired[ObjectLockLegalHoldStatusType],
    },
)
GetObjectLegalHoldRequestRequestTypeDef = TypedDict(
    "GetObjectLegalHoldRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "VersionId": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetObjectLockConfigurationRequestRequestTypeDef = TypedDict(
    "GetObjectLockConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
ObjectLockRetentionOutputTypeDef = TypedDict(
    "ObjectLockRetentionOutputTypeDef",
    {
        "Mode": NotRequired[ObjectLockRetentionModeType],
        "RetainUntilDate": NotRequired[datetime],
    },
)
GetObjectRetentionRequestRequestTypeDef = TypedDict(
    "GetObjectRetentionRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "VersionId": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetObjectTaggingRequestRequestTypeDef = TypedDict(
    "GetObjectTaggingRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "VersionId": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
    },
)
GetObjectTorrentRequestRequestTypeDef = TypedDict(
    "GetObjectTorrentRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PublicAccessBlockConfigurationTypeDef = TypedDict(
    "PublicAccessBlockConfigurationTypeDef",
    {
        "BlockPublicAcls": NotRequired[bool],
        "IgnorePublicAcls": NotRequired[bool],
        "BlockPublicPolicy": NotRequired[bool],
        "RestrictPublicBuckets": NotRequired[bool],
    },
)
GetPublicAccessBlockRequestRequestTypeDef = TypedDict(
    "GetPublicAccessBlockRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GlacierJobParametersTypeDef = TypedDict(
    "GlacierJobParametersTypeDef",
    {
        "Tier": TierType,
    },
)
GranteeTypeDef = TypedDict(
    "GranteeTypeDef",
    {
        "Type": TypeType,
        "DisplayName": NotRequired[str],
        "EmailAddress": NotRequired[str],
        "ID": NotRequired[str],
        "URI": NotRequired[str],
    },
)
WaiterConfigTypeDef = TypedDict(
    "WaiterConfigTypeDef",
    {
        "Delay": NotRequired[int],
        "MaxAttempts": NotRequired[int],
    },
)
HeadBucketRequestRequestTypeDef = TypedDict(
    "HeadBucketRequestRequestTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
InitiatorTypeDef = TypedDict(
    "InitiatorTypeDef",
    {
        "ID": NotRequired[str],
        "DisplayName": NotRequired[str],
    },
)
JSONInputTypeDef = TypedDict(
    "JSONInputTypeDef",
    {
        "Type": NotRequired[JSONTypeType],
    },
)
TieringTypeDef = TypedDict(
    "TieringTypeDef",
    {
        "Days": int,
        "AccessTier": IntelligentTieringAccessTierType,
    },
)
InventoryFilterTypeDef = TypedDict(
    "InventoryFilterTypeDef",
    {
        "Prefix": str,
    },
)
InventoryScheduleTypeDef = TypedDict(
    "InventoryScheduleTypeDef",
    {
        "Frequency": InventoryFrequencyType,
    },
)
SSEKMSTypeDef = TypedDict(
    "SSEKMSTypeDef",
    {
        "KeyId": str,
    },
)
JSONOutputTypeDef = TypedDict(
    "JSONOutputTypeDef",
    {
        "RecordDelimiter": NotRequired[str],
    },
)
LifecycleExpirationExtraExtraOutputTypeDef = TypedDict(
    "LifecycleExpirationExtraExtraOutputTypeDef",
    {
        "Date": NotRequired[datetime],
        "Days": NotRequired[int],
        "ExpiredObjectDeleteMarker": NotRequired[bool],
    },
)
LifecycleExpirationExtraOutputTypeDef = TypedDict(
    "LifecycleExpirationExtraOutputTypeDef",
    {
        "Date": NotRequired[datetime],
        "Days": NotRequired[int],
        "ExpiredObjectDeleteMarker": NotRequired[bool],
    },
)
LifecycleExpirationOutputTypeDef = TypedDict(
    "LifecycleExpirationOutputTypeDef",
    {
        "Date": NotRequired[datetime],
        "Days": NotRequired[int],
        "ExpiredObjectDeleteMarker": NotRequired[bool],
    },
)
NoncurrentVersionExpirationTypeDef = TypedDict(
    "NoncurrentVersionExpirationTypeDef",
    {
        "NoncurrentDays": NotRequired[int],
        "NewerNoncurrentVersions": NotRequired[int],
    },
)
NoncurrentVersionTransitionTypeDef = TypedDict(
    "NoncurrentVersionTransitionTypeDef",
    {
        "NoncurrentDays": NotRequired[int],
        "StorageClass": NotRequired[TransitionStorageClassType],
        "NewerNoncurrentVersions": NotRequired[int],
    },
)
TransitionExtraOutputTypeDef = TypedDict(
    "TransitionExtraOutputTypeDef",
    {
        "Date": NotRequired[datetime],
        "Days": NotRequired[int],
        "StorageClass": NotRequired[TransitionStorageClassType],
    },
)
TransitionOutputTypeDef = TypedDict(
    "TransitionOutputTypeDef",
    {
        "Date": NotRequired[datetime],
        "Days": NotRequired[int],
        "StorageClass": NotRequired[TransitionStorageClassType],
    },
)
ListBucketAnalyticsConfigurationsRequestRequestTypeDef = TypedDict(
    "ListBucketAnalyticsConfigurationsRequestRequestTypeDef",
    {
        "Bucket": str,
        "ContinuationToken": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
ListBucketIntelligentTieringConfigurationsRequestRequestTypeDef = TypedDict(
    "ListBucketIntelligentTieringConfigurationsRequestRequestTypeDef",
    {
        "Bucket": str,
        "ContinuationToken": NotRequired[str],
    },
)
ListBucketInventoryConfigurationsRequestRequestTypeDef = TypedDict(
    "ListBucketInventoryConfigurationsRequestRequestTypeDef",
    {
        "Bucket": str,
        "ContinuationToken": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
ListBucketMetricsConfigurationsRequestRequestTypeDef = TypedDict(
    "ListBucketMetricsConfigurationsRequestRequestTypeDef",
    {
        "Bucket": str,
        "ContinuationToken": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
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
ListDirectoryBucketsRequestRequestTypeDef = TypedDict(
    "ListDirectoryBucketsRequestRequestTypeDef",
    {
        "ContinuationToken": NotRequired[str],
        "MaxDirectoryBuckets": NotRequired[int],
    },
)
ListMultipartUploadsRequestRequestTypeDef = TypedDict(
    "ListMultipartUploadsRequestRequestTypeDef",
    {
        "Bucket": str,
        "Delimiter": NotRequired[str],
        "EncodingType": NotRequired[Literal["url"]],
        "KeyMarker": NotRequired[str],
        "MaxUploads": NotRequired[int],
        "Prefix": NotRequired[str],
        "UploadIdMarker": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
    },
)
ListObjectVersionsRequestRequestTypeDef = TypedDict(
    "ListObjectVersionsRequestRequestTypeDef",
    {
        "Bucket": str,
        "Delimiter": NotRequired[str],
        "EncodingType": NotRequired[Literal["url"]],
        "KeyMarker": NotRequired[str],
        "MaxKeys": NotRequired[int],
        "Prefix": NotRequired[str],
        "VersionIdMarker": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "OptionalObjectAttributes": NotRequired[Sequence[Literal["RestoreStatus"]]],
    },
)
ListObjectsRequestRequestTypeDef = TypedDict(
    "ListObjectsRequestRequestTypeDef",
    {
        "Bucket": str,
        "Delimiter": NotRequired[str],
        "EncodingType": NotRequired[Literal["url"]],
        "Marker": NotRequired[str],
        "MaxKeys": NotRequired[int],
        "Prefix": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
        "OptionalObjectAttributes": NotRequired[Sequence[Literal["RestoreStatus"]]],
    },
)
ListObjectsV2RequestRequestTypeDef = TypedDict(
    "ListObjectsV2RequestRequestTypeDef",
    {
        "Bucket": str,
        "Delimiter": NotRequired[str],
        "EncodingType": NotRequired[Literal["url"]],
        "MaxKeys": NotRequired[int],
        "Prefix": NotRequired[str],
        "ContinuationToken": NotRequired[str],
        "FetchOwner": NotRequired[bool],
        "StartAfter": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
        "OptionalObjectAttributes": NotRequired[Sequence[Literal["RestoreStatus"]]],
    },
)
PartTypeDef = TypedDict(
    "PartTypeDef",
    {
        "PartNumber": NotRequired[int],
        "LastModified": NotRequired[datetime],
        "ETag": NotRequired[str],
        "Size": NotRequired[int],
        "ChecksumCRC32": NotRequired[str],
        "ChecksumCRC32C": NotRequired[str],
        "ChecksumSHA1": NotRequired[str],
        "ChecksumSHA256": NotRequired[str],
    },
)
ListPartsRequestRequestTypeDef = TypedDict(
    "ListPartsRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "UploadId": str,
        "MaxParts": NotRequired[int],
        "PartNumberMarker": NotRequired[int],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
    },
)
MetadataEntryTypeDef = TypedDict(
    "MetadataEntryTypeDef",
    {
        "Name": NotRequired[str],
        "Value": NotRequired[str],
    },
)
ReplicationTimeValueTypeDef = TypedDict(
    "ReplicationTimeValueTypeDef",
    {
        "Minutes": NotRequired[int],
    },
)
QueueConfigurationDeprecatedOutputTypeDef = TypedDict(
    "QueueConfigurationDeprecatedOutputTypeDef",
    {
        "Id": NotRequired[str],
        "Event": NotRequired[EventType],
        "Events": NotRequired[List[EventType]],
        "Queue": NotRequired[str],
    },
)
TopicConfigurationDeprecatedOutputTypeDef = TypedDict(
    "TopicConfigurationDeprecatedOutputTypeDef",
    {
        "Id": NotRequired[str],
        "Events": NotRequired[List[EventType]],
        "Event": NotRequired[EventType],
        "Topic": NotRequired[str],
    },
)
QueueConfigurationDeprecatedTypeDef = TypedDict(
    "QueueConfigurationDeprecatedTypeDef",
    {
        "Id": NotRequired[str],
        "Event": NotRequired[EventType],
        "Events": NotRequired[Sequence[EventType]],
        "Queue": NotRequired[str],
    },
)
TopicConfigurationDeprecatedTypeDef = TypedDict(
    "TopicConfigurationDeprecatedTypeDef",
    {
        "Id": NotRequired[str],
        "Events": NotRequired[Sequence[EventType]],
        "Event": NotRequired[EventType],
        "Topic": NotRequired[str],
    },
)
ObjectDownloadFileRequestTypeDef = TypedDict(
    "ObjectDownloadFileRequestTypeDef",
    {
        "Filename": str,
        "ExtraArgs": NotRequired[Optional[Dict[str, Any]]],
        "Callback": NotRequired[Optional[Callable[..., Any]]],
        "Config": NotRequired[Optional[TransferConfig]],
    },
)
RestoreStatusTypeDef = TypedDict(
    "RestoreStatusTypeDef",
    {
        "IsRestoreInProgress": NotRequired[bool],
        "RestoreExpiryDate": NotRequired[datetime],
    },
)
ObjectUploadFileRequestTypeDef = TypedDict(
    "ObjectUploadFileRequestTypeDef",
    {
        "Filename": str,
        "ExtraArgs": NotRequired[Optional[Dict[str, Any]]],
        "Callback": NotRequired[Optional[Callable[..., Any]]],
        "Config": NotRequired[Optional[TransferConfig]],
    },
)
OwnershipControlsRuleTypeDef = TypedDict(
    "OwnershipControlsRuleTypeDef",
    {
        "ObjectOwnership": ObjectOwnershipType,
    },
)
PartitionedPrefixTypeDef = TypedDict(
    "PartitionedPrefixTypeDef",
    {
        "PartitionDateSource": NotRequired[PartitionDateSourceType],
    },
)
ProgressTypeDef = TypedDict(
    "ProgressTypeDef",
    {
        "BytesScanned": NotRequired[int],
        "BytesProcessed": NotRequired[int],
        "BytesReturned": NotRequired[int],
    },
)
PutBucketPolicyRequestBucketPolicyPutTypeDef = TypedDict(
    "PutBucketPolicyRequestBucketPolicyPutTypeDef",
    {
        "Policy": str,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ConfirmRemoveSelfBucketAccess": NotRequired[bool],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutBucketPolicyRequestRequestTypeDef = TypedDict(
    "PutBucketPolicyRequestRequestTypeDef",
    {
        "Bucket": str,
        "Policy": str,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ConfirmRemoveSelfBucketAccess": NotRequired[bool],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
RequestPaymentConfigurationTypeDef = TypedDict(
    "RequestPaymentConfigurationTypeDef",
    {
        "Payer": PayerType,
    },
)
PutBucketVersioningRequestBucketVersioningEnableTypeDef = TypedDict(
    "PutBucketVersioningRequestBucketVersioningEnableTypeDef",
    {
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "MFA": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
VersioningConfigurationTypeDef = TypedDict(
    "VersioningConfigurationTypeDef",
    {
        "MFADelete": NotRequired[MFADeleteType],
        "Status": NotRequired[BucketVersioningStatusType],
    },
)
PutBucketVersioningRequestBucketVersioningSuspendTypeDef = TypedDict(
    "PutBucketVersioningRequestBucketVersioningSuspendTypeDef",
    {
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "MFA": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
RecordsEventTypeDef = TypedDict(
    "RecordsEventTypeDef",
    {
        "Payload": NotRequired[bytes],
    },
)
RedirectTypeDef = TypedDict(
    "RedirectTypeDef",
    {
        "HostName": NotRequired[str],
        "HttpRedirectCode": NotRequired[str],
        "Protocol": NotRequired[ProtocolType],
        "ReplaceKeyPrefixWith": NotRequired[str],
        "ReplaceKeyWith": NotRequired[str],
    },
)
ReplicaModificationsTypeDef = TypedDict(
    "ReplicaModificationsTypeDef",
    {
        "Status": ReplicaModificationsStatusType,
    },
)
RequestProgressTypeDef = TypedDict(
    "RequestProgressTypeDef",
    {
        "Enabled": NotRequired[bool],
    },
)
TransitionExtraExtraOutputTypeDef = TypedDict(
    "TransitionExtraExtraOutputTypeDef",
    {
        "Date": NotRequired[datetime],
        "Days": NotRequired[int],
        "StorageClass": NotRequired[TransitionStorageClassType],
    },
)
ScanRangeTypeDef = TypedDict(
    "ScanRangeTypeDef",
    {
        "Start": NotRequired[int],
        "End": NotRequired[int],
    },
)
ServerSideEncryptionByDefaultTypeDef = TypedDict(
    "ServerSideEncryptionByDefaultTypeDef",
    {
        "SSEAlgorithm": ServerSideEncryptionType,
        "KMSMasterKeyID": NotRequired[str],
    },
)
SseKmsEncryptedObjectsTypeDef = TypedDict(
    "SseKmsEncryptedObjectsTypeDef",
    {
        "Status": SseKmsEncryptedObjectsStatusType,
    },
)
StatsTypeDef = TypedDict(
    "StatsTypeDef",
    {
        "BytesScanned": NotRequired[int],
        "BytesProcessed": NotRequired[int],
        "BytesReturned": NotRequired[int],
    },
)
AbortMultipartUploadOutputTypeDef = TypedDict(
    "AbortMultipartUploadOutputTypeDef",
    {
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CompleteMultipartUploadOutputTypeDef = TypedDict(
    "CompleteMultipartUploadOutputTypeDef",
    {
        "Location": str,
        "Bucket": str,
        "Key": str,
        "Expiration": str,
        "ETag": str,
        "ChecksumCRC32": str,
        "ChecksumCRC32C": str,
        "ChecksumSHA1": str,
        "ChecksumSHA256": str,
        "ServerSideEncryption": ServerSideEncryptionType,
        "VersionId": str,
        "SSEKMSKeyId": str,
        "BucketKeyEnabled": bool,
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateBucketOutputTypeDef = TypedDict(
    "CreateBucketOutputTypeDef",
    {
        "Location": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateMultipartUploadOutputTypeDef = TypedDict(
    "CreateMultipartUploadOutputTypeDef",
    {
        "AbortDate": datetime,
        "AbortRuleId": str,
        "Bucket": str,
        "Key": str,
        "UploadId": str,
        "ServerSideEncryption": ServerSideEncryptionType,
        "SSECustomerAlgorithm": str,
        "SSECustomerKeyMD5": str,
        "SSEKMSKeyId": str,
        "SSEKMSEncryptionContext": str,
        "BucketKeyEnabled": bool,
        "RequestCharged": Literal["requester"],
        "ChecksumAlgorithm": ChecksumAlgorithmType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteObjectOutputTypeDef = TypedDict(
    "DeleteObjectOutputTypeDef",
    {
        "DeleteMarker": bool,
        "VersionId": str,
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteObjectTaggingOutputTypeDef = TypedDict(
    "DeleteObjectTaggingOutputTypeDef",
    {
        "VersionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ErrorDocumentResponseTypeDef = TypedDict(
    "ErrorDocumentResponseTypeDef",
    {
        "Key": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetBucketAccelerateConfigurationOutputTypeDef = TypedDict(
    "GetBucketAccelerateConfigurationOutputTypeDef",
    {
        "Status": BucketAccelerateStatusType,
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetBucketLocationOutputTypeDef = TypedDict(
    "GetBucketLocationOutputTypeDef",
    {
        "LocationConstraint": BucketLocationConstraintType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetBucketPolicyOutputTypeDef = TypedDict(
    "GetBucketPolicyOutputTypeDef",
    {
        "Policy": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetBucketRequestPaymentOutputTypeDef = TypedDict(
    "GetBucketRequestPaymentOutputTypeDef",
    {
        "Payer": PayerType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetBucketVersioningOutputTypeDef = TypedDict(
    "GetBucketVersioningOutputTypeDef",
    {
        "Status": BucketVersioningStatusType,
        "MFADelete": MFADeleteStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetObjectOutputTypeDef = TypedDict(
    "GetObjectOutputTypeDef",
    {
        "Body": StreamingBody,
        "DeleteMarker": bool,
        "AcceptRanges": str,
        "Expiration": str,
        "Restore": str,
        "LastModified": datetime,
        "ContentLength": int,
        "ETag": str,
        "ChecksumCRC32": str,
        "ChecksumCRC32C": str,
        "ChecksumSHA1": str,
        "ChecksumSHA256": str,
        "MissingMeta": int,
        "VersionId": str,
        "CacheControl": str,
        "ContentDisposition": str,
        "ContentEncoding": str,
        "ContentLanguage": str,
        "ContentRange": str,
        "ContentType": str,
        "Expires": datetime,
        "WebsiteRedirectLocation": str,
        "ServerSideEncryption": ServerSideEncryptionType,
        "Metadata": Dict[str, str],
        "SSECustomerAlgorithm": str,
        "SSECustomerKeyMD5": str,
        "SSEKMSKeyId": str,
        "BucketKeyEnabled": bool,
        "StorageClass": StorageClassType,
        "RequestCharged": Literal["requester"],
        "ReplicationStatus": ReplicationStatusType,
        "PartsCount": int,
        "TagCount": int,
        "ObjectLockMode": ObjectLockModeType,
        "ObjectLockRetainUntilDate": datetime,
        "ObjectLockLegalHoldStatus": ObjectLockLegalHoldStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetObjectTorrentOutputTypeDef = TypedDict(
    "GetObjectTorrentOutputTypeDef",
    {
        "Body": StreamingBody,
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
HeadBucketOutputTypeDef = TypedDict(
    "HeadBucketOutputTypeDef",
    {
        "BucketLocationType": Literal["AvailabilityZone"],
        "BucketLocationName": str,
        "BucketRegion": str,
        "AccessPointAlias": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
HeadObjectOutputTypeDef = TypedDict(
    "HeadObjectOutputTypeDef",
    {
        "DeleteMarker": bool,
        "AcceptRanges": str,
        "Expiration": str,
        "Restore": str,
        "ArchiveStatus": ArchiveStatusType,
        "LastModified": datetime,
        "ContentLength": int,
        "ChecksumCRC32": str,
        "ChecksumCRC32C": str,
        "ChecksumSHA1": str,
        "ChecksumSHA256": str,
        "ETag": str,
        "MissingMeta": int,
        "VersionId": str,
        "CacheControl": str,
        "ContentDisposition": str,
        "ContentEncoding": str,
        "ContentLanguage": str,
        "ContentType": str,
        "Expires": datetime,
        "WebsiteRedirectLocation": str,
        "ServerSideEncryption": ServerSideEncryptionType,
        "Metadata": Dict[str, str],
        "SSECustomerAlgorithm": str,
        "SSECustomerKeyMD5": str,
        "SSEKMSKeyId": str,
        "BucketKeyEnabled": bool,
        "StorageClass": StorageClassType,
        "RequestCharged": Literal["requester"],
        "ReplicationStatus": ReplicationStatusType,
        "PartsCount": int,
        "ObjectLockMode": ObjectLockModeType,
        "ObjectLockRetainUntilDate": datetime,
        "ObjectLockLegalHoldStatus": ObjectLockLegalHoldStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
IndexDocumentResponseTypeDef = TypedDict(
    "IndexDocumentResponseTypeDef",
    {
        "Suffix": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
InitiatorResponseTypeDef = TypedDict(
    "InitiatorResponseTypeDef",
    {
        "ID": str,
        "DisplayName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
OwnerResponseTypeDef = TypedDict(
    "OwnerResponseTypeDef",
    {
        "DisplayName": str,
        "ID": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutObjectAclOutputTypeDef = TypedDict(
    "PutObjectAclOutputTypeDef",
    {
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutObjectLegalHoldOutputTypeDef = TypedDict(
    "PutObjectLegalHoldOutputTypeDef",
    {
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutObjectLockConfigurationOutputTypeDef = TypedDict(
    "PutObjectLockConfigurationOutputTypeDef",
    {
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutObjectOutputTypeDef = TypedDict(
    "PutObjectOutputTypeDef",
    {
        "Expiration": str,
        "ETag": str,
        "ChecksumCRC32": str,
        "ChecksumCRC32C": str,
        "ChecksumSHA1": str,
        "ChecksumSHA256": str,
        "ServerSideEncryption": ServerSideEncryptionType,
        "VersionId": str,
        "SSECustomerAlgorithm": str,
        "SSECustomerKeyMD5": str,
        "SSEKMSKeyId": str,
        "SSEKMSEncryptionContext": str,
        "BucketKeyEnabled": bool,
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutObjectRetentionOutputTypeDef = TypedDict(
    "PutObjectRetentionOutputTypeDef",
    {
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutObjectTaggingOutputTypeDef = TypedDict(
    "PutObjectTaggingOutputTypeDef",
    {
        "VersionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RedirectAllRequestsToResponseTypeDef = TypedDict(
    "RedirectAllRequestsToResponseTypeDef",
    {
        "HostName": str,
        "Protocol": ProtocolType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RestoreObjectOutputTypeDef = TypedDict(
    "RestoreObjectOutputTypeDef",
    {
        "RequestCharged": Literal["requester"],
        "RestoreOutputPath": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RestoreStatusResponseTypeDef = TypedDict(
    "RestoreStatusResponseTypeDef",
    {
        "IsRestoreInProgress": bool,
        "RestoreExpiryDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UploadPartOutputTypeDef = TypedDict(
    "UploadPartOutputTypeDef",
    {
        "ServerSideEncryption": ServerSideEncryptionType,
        "ETag": str,
        "ChecksumCRC32": str,
        "ChecksumCRC32C": str,
        "ChecksumSHA1": str,
        "ChecksumSHA256": str,
        "SSECustomerAlgorithm": str,
        "SSECustomerKeyMD5": str,
        "SSEKMSKeyId": str,
        "BucketKeyEnabled": bool,
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutBucketAccelerateConfigurationRequestRequestTypeDef = TypedDict(
    "PutBucketAccelerateConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "AccelerateConfiguration": AccelerateConfigurationTypeDef,
        "ExpectedBucketOwner": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
    },
)
DeleteMarkerEntryTypeDef = TypedDict(
    "DeleteMarkerEntryTypeDef",
    {
        "Owner": NotRequired[OwnerTypeDef],
        "Key": NotRequired[str],
        "VersionId": NotRequired[str],
        "IsLatest": NotRequired[bool],
        "LastModified": NotRequired[datetime],
    },
)
AnalyticsAndOperatorOutputTypeDef = TypedDict(
    "AnalyticsAndOperatorOutputTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
AnalyticsAndOperatorTypeDef = TypedDict(
    "AnalyticsAndOperatorTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
GetBucketTaggingOutputTypeDef = TypedDict(
    "GetBucketTaggingOutputTypeDef",
    {
        "TagSet": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetObjectTaggingOutputTypeDef = TypedDict(
    "GetObjectTaggingOutputTypeDef",
    {
        "VersionId": str,
        "TagSet": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
IntelligentTieringAndOperatorOutputTypeDef = TypedDict(
    "IntelligentTieringAndOperatorOutputTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
IntelligentTieringAndOperatorTypeDef = TypedDict(
    "IntelligentTieringAndOperatorTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
LifecycleRuleAndOperatorExtraOutputTypeDef = TypedDict(
    "LifecycleRuleAndOperatorExtraOutputTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
        "ObjectSizeGreaterThan": NotRequired[int],
        "ObjectSizeLessThan": NotRequired[int],
    },
)
LifecycleRuleAndOperatorOutputTypeDef = TypedDict(
    "LifecycleRuleAndOperatorOutputTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
        "ObjectSizeGreaterThan": NotRequired[int],
        "ObjectSizeLessThan": NotRequired[int],
    },
)
LifecycleRuleAndOperatorTypeDef = TypedDict(
    "LifecycleRuleAndOperatorTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "ObjectSizeGreaterThan": NotRequired[int],
        "ObjectSizeLessThan": NotRequired[int],
    },
)
MetricsAndOperatorOutputTypeDef = TypedDict(
    "MetricsAndOperatorOutputTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
        "AccessPointArn": NotRequired[str],
    },
)
MetricsAndOperatorTypeDef = TypedDict(
    "MetricsAndOperatorTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "AccessPointArn": NotRequired[str],
    },
)
ReplicationRuleAndOperatorOutputTypeDef = TypedDict(
    "ReplicationRuleAndOperatorOutputTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
ReplicationRuleAndOperatorTypeDef = TypedDict(
    "ReplicationRuleAndOperatorTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
TaggingTypeDef = TypedDict(
    "TaggingTypeDef",
    {
        "TagSet": Sequence[TagTypeDef],
    },
)
AnalyticsExportDestinationTypeDef = TypedDict(
    "AnalyticsExportDestinationTypeDef",
    {
        "S3BucketDestination": AnalyticsS3BucketDestinationTypeDef,
    },
)
UploadPartRequestMultipartUploadPartUploadTypeDef = TypedDict(
    "UploadPartRequestMultipartUploadPartUploadTypeDef",
    {
        "Body": NotRequired[BlobTypeDef],
        "ContentLength": NotRequired[int],
        "ContentMD5": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ChecksumCRC32": NotRequired[str],
        "ChecksumCRC32C": NotRequired[str],
        "ChecksumSHA1": NotRequired[str],
        "ChecksumSHA256": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
UploadPartRequestRequestTypeDef = TypedDict(
    "UploadPartRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "PartNumber": int,
        "UploadId": str,
        "Body": NotRequired[BlobTypeDef],
        "ContentLength": NotRequired[int],
        "ContentMD5": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ChecksumCRC32": NotRequired[str],
        "ChecksumCRC32C": NotRequired[str],
        "ChecksumSHA1": NotRequired[str],
        "ChecksumSHA256": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
BucketCopyRequestTypeDef = TypedDict(
    "BucketCopyRequestTypeDef",
    {
        "CopySource": CopySourceTypeDef,
        "Key": str,
        "ExtraArgs": NotRequired[Optional[Dict[str, Any]]],
        "Callback": NotRequired[Optional[Callable[..., Any]]],
        "SourceClient": NotRequired[Optional[BaseClient]],
        "Config": NotRequired[Optional[TransferConfig]],
    },
)
ClientCopyRequestTypeDef = TypedDict(
    "ClientCopyRequestTypeDef",
    {
        "CopySource": CopySourceTypeDef,
        "Bucket": str,
        "Key": str,
        "ExtraArgs": NotRequired[Optional[Dict[str, Any]]],
        "Callback": NotRequired[Optional[Callable[..., Any]]],
        "SourceClient": NotRequired[Optional[BaseClient]],
        "Config": NotRequired[Optional[TransferConfig]],
    },
)
CopySourceOrStrTypeDef = Union[str, CopySourceTypeDef]
ObjectCopyRequestTypeDef = TypedDict(
    "ObjectCopyRequestTypeDef",
    {
        "CopySource": CopySourceTypeDef,
        "ExtraArgs": NotRequired[Optional[Dict[str, Any]]],
        "Callback": NotRequired[Optional[Callable[..., Any]]],
        "SourceClient": NotRequired[Optional[BaseClient]],
        "Config": NotRequired[Optional[TransferConfig]],
    },
)
BucketDownloadFileobjRequestTypeDef = TypedDict(
    "BucketDownloadFileobjRequestTypeDef",
    {
        "Key": str,
        "Fileobj": FileobjTypeDef,
        "ExtraArgs": NotRequired[Optional[Dict[str, Any]]],
        "Callback": NotRequired[Optional[Callable[..., Any]]],
        "Config": NotRequired[Optional[TransferConfig]],
    },
)
BucketUploadFileobjRequestTypeDef = TypedDict(
    "BucketUploadFileobjRequestTypeDef",
    {
        "Fileobj": FileobjTypeDef,
        "Key": str,
        "ExtraArgs": NotRequired[Optional[Dict[str, Any]]],
        "Callback": NotRequired[Optional[Callable[..., Any]]],
        "Config": NotRequired[Optional[TransferConfig]],
    },
)
ClientDownloadFileobjRequestTypeDef = TypedDict(
    "ClientDownloadFileobjRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "Fileobj": FileobjTypeDef,
        "ExtraArgs": NotRequired[Optional[Dict[str, Any]]],
        "Callback": NotRequired[Optional[Callable[..., Any]]],
        "Config": NotRequired[Optional[TransferConfig]],
    },
)
ClientUploadFileobjRequestTypeDef = TypedDict(
    "ClientUploadFileobjRequestTypeDef",
    {
        "Fileobj": FileobjTypeDef,
        "Bucket": str,
        "Key": str,
        "ExtraArgs": NotRequired[Optional[Dict[str, Any]]],
        "Callback": NotRequired[Optional[Callable[..., Any]]],
        "Config": NotRequired[Optional[TransferConfig]],
    },
)
ObjectDownloadFileobjRequestTypeDef = TypedDict(
    "ObjectDownloadFileobjRequestTypeDef",
    {
        "Fileobj": FileobjTypeDef,
        "ExtraArgs": NotRequired[Optional[Dict[str, Any]]],
        "Callback": NotRequired[Optional[Callable[..., Any]]],
        "Config": NotRequired[Optional[TransferConfig]],
    },
)
ObjectUploadFileobjRequestTypeDef = TypedDict(
    "ObjectUploadFileobjRequestTypeDef",
    {
        "Fileobj": FileobjTypeDef,
        "ExtraArgs": NotRequired[Optional[Dict[str, Any]]],
        "Callback": NotRequired[Optional[Callable[..., Any]]],
        "Config": NotRequired[Optional[TransferConfig]],
    },
)
ListBucketsOutputTypeDef = TypedDict(
    "ListBucketsOutputTypeDef",
    {
        "Buckets": List[BucketTypeDef],
        "Owner": OwnerTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListDirectoryBucketsOutputTypeDef = TypedDict(
    "ListDirectoryBucketsOutputTypeDef",
    {
        "Buckets": List[BucketTypeDef],
        "ContinuationToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CORSConfigurationTypeDef = TypedDict(
    "CORSConfigurationTypeDef",
    {
        "CORSRules": Sequence[CORSRuleTypeDef],
    },
)
GetBucketCorsOutputTypeDef = TypedDict(
    "GetBucketCorsOutputTypeDef",
    {
        "CORSRules": List[CORSRuleOutputTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CompletedMultipartUploadTypeDef = TypedDict(
    "CompletedMultipartUploadTypeDef",
    {
        "Parts": NotRequired[Sequence[CompletedPartTypeDef]],
    },
)
CopyObjectOutputTypeDef = TypedDict(
    "CopyObjectOutputTypeDef",
    {
        "CopyObjectResult": CopyObjectResultTypeDef,
        "Expiration": str,
        "CopySourceVersionId": str,
        "VersionId": str,
        "ServerSideEncryption": ServerSideEncryptionType,
        "SSECustomerAlgorithm": str,
        "SSECustomerKeyMD5": str,
        "SSEKMSKeyId": str,
        "SSEKMSEncryptionContext": str,
        "BucketKeyEnabled": bool,
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CopyObjectRequestObjectCopyFromTypeDef = TypedDict(
    "CopyObjectRequestObjectCopyFromTypeDef",
    {
        "CopySource": str,
        "ACL": NotRequired[ObjectCannedACLType],
        "CacheControl": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ContentDisposition": NotRequired[str],
        "ContentEncoding": NotRequired[str],
        "ContentLanguage": NotRequired[str],
        "ContentType": NotRequired[str],
        "CopySourceIfMatch": NotRequired[str],
        "CopySourceIfModifiedSince": NotRequired[TimestampTypeDef],
        "CopySourceIfNoneMatch": NotRequired[str],
        "CopySourceIfUnmodifiedSince": NotRequired[TimestampTypeDef],
        "Expires": NotRequired[TimestampTypeDef],
        "GrantFullControl": NotRequired[str],
        "GrantRead": NotRequired[str],
        "GrantReadACP": NotRequired[str],
        "GrantWriteACP": NotRequired[str],
        "Metadata": NotRequired[Mapping[str, str]],
        "MetadataDirective": NotRequired[MetadataDirectiveType],
        "TaggingDirective": NotRequired[TaggingDirectiveType],
        "ServerSideEncryption": NotRequired[ServerSideEncryptionType],
        "StorageClass": NotRequired[StorageClassType],
        "WebsiteRedirectLocation": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "SSEKMSKeyId": NotRequired[str],
        "SSEKMSEncryptionContext": NotRequired[str],
        "BucketKeyEnabled": NotRequired[bool],
        "CopySourceSSECustomerAlgorithm": NotRequired[str],
        "CopySourceSSECustomerKey": NotRequired[str],
        "CopySourceSSECustomerKeyMD5": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "Tagging": NotRequired[str],
        "ObjectLockMode": NotRequired[ObjectLockModeType],
        "ObjectLockRetainUntilDate": NotRequired[TimestampTypeDef],
        "ObjectLockLegalHoldStatus": NotRequired[ObjectLockLegalHoldStatusType],
        "ExpectedBucketOwner": NotRequired[str],
        "ExpectedSourceBucketOwner": NotRequired[str],
    },
)
CopyObjectRequestObjectSummaryCopyFromTypeDef = TypedDict(
    "CopyObjectRequestObjectSummaryCopyFromTypeDef",
    {
        "CopySource": str,
        "ACL": NotRequired[ObjectCannedACLType],
        "CacheControl": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ContentDisposition": NotRequired[str],
        "ContentEncoding": NotRequired[str],
        "ContentLanguage": NotRequired[str],
        "ContentType": NotRequired[str],
        "CopySourceIfMatch": NotRequired[str],
        "CopySourceIfModifiedSince": NotRequired[TimestampTypeDef],
        "CopySourceIfNoneMatch": NotRequired[str],
        "CopySourceIfUnmodifiedSince": NotRequired[TimestampTypeDef],
        "Expires": NotRequired[TimestampTypeDef],
        "GrantFullControl": NotRequired[str],
        "GrantRead": NotRequired[str],
        "GrantReadACP": NotRequired[str],
        "GrantWriteACP": NotRequired[str],
        "Metadata": NotRequired[Mapping[str, str]],
        "MetadataDirective": NotRequired[MetadataDirectiveType],
        "TaggingDirective": NotRequired[TaggingDirectiveType],
        "ServerSideEncryption": NotRequired[ServerSideEncryptionType],
        "StorageClass": NotRequired[StorageClassType],
        "WebsiteRedirectLocation": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "SSEKMSKeyId": NotRequired[str],
        "SSEKMSEncryptionContext": NotRequired[str],
        "BucketKeyEnabled": NotRequired[bool],
        "CopySourceSSECustomerAlgorithm": NotRequired[str],
        "CopySourceSSECustomerKey": NotRequired[str],
        "CopySourceSSECustomerKeyMD5": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "Tagging": NotRequired[str],
        "ObjectLockMode": NotRequired[ObjectLockModeType],
        "ObjectLockRetainUntilDate": NotRequired[TimestampTypeDef],
        "ObjectLockLegalHoldStatus": NotRequired[ObjectLockLegalHoldStatusType],
        "ExpectedBucketOwner": NotRequired[str],
        "ExpectedSourceBucketOwner": NotRequired[str],
    },
)
CreateMultipartUploadRequestObjectInitiateMultipartUploadTypeDef = TypedDict(
    "CreateMultipartUploadRequestObjectInitiateMultipartUploadTypeDef",
    {
        "ACL": NotRequired[ObjectCannedACLType],
        "CacheControl": NotRequired[str],
        "ContentDisposition": NotRequired[str],
        "ContentEncoding": NotRequired[str],
        "ContentLanguage": NotRequired[str],
        "ContentType": NotRequired[str],
        "Expires": NotRequired[TimestampTypeDef],
        "GrantFullControl": NotRequired[str],
        "GrantRead": NotRequired[str],
        "GrantReadACP": NotRequired[str],
        "GrantWriteACP": NotRequired[str],
        "Metadata": NotRequired[Mapping[str, str]],
        "ServerSideEncryption": NotRequired[ServerSideEncryptionType],
        "StorageClass": NotRequired[StorageClassType],
        "WebsiteRedirectLocation": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "SSEKMSKeyId": NotRequired[str],
        "SSEKMSEncryptionContext": NotRequired[str],
        "BucketKeyEnabled": NotRequired[bool],
        "RequestPayer": NotRequired[Literal["requester"]],
        "Tagging": NotRequired[str],
        "ObjectLockMode": NotRequired[ObjectLockModeType],
        "ObjectLockRetainUntilDate": NotRequired[TimestampTypeDef],
        "ObjectLockLegalHoldStatus": NotRequired[ObjectLockLegalHoldStatusType],
        "ExpectedBucketOwner": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
    },
)
CreateMultipartUploadRequestObjectSummaryInitiateMultipartUploadTypeDef = TypedDict(
    "CreateMultipartUploadRequestObjectSummaryInitiateMultipartUploadTypeDef",
    {
        "ACL": NotRequired[ObjectCannedACLType],
        "CacheControl": NotRequired[str],
        "ContentDisposition": NotRequired[str],
        "ContentEncoding": NotRequired[str],
        "ContentLanguage": NotRequired[str],
        "ContentType": NotRequired[str],
        "Expires": NotRequired[TimestampTypeDef],
        "GrantFullControl": NotRequired[str],
        "GrantRead": NotRequired[str],
        "GrantReadACP": NotRequired[str],
        "GrantWriteACP": NotRequired[str],
        "Metadata": NotRequired[Mapping[str, str]],
        "ServerSideEncryption": NotRequired[ServerSideEncryptionType],
        "StorageClass": NotRequired[StorageClassType],
        "WebsiteRedirectLocation": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "SSEKMSKeyId": NotRequired[str],
        "SSEKMSEncryptionContext": NotRequired[str],
        "BucketKeyEnabled": NotRequired[bool],
        "RequestPayer": NotRequired[Literal["requester"]],
        "Tagging": NotRequired[str],
        "ObjectLockMode": NotRequired[ObjectLockModeType],
        "ObjectLockRetainUntilDate": NotRequired[TimestampTypeDef],
        "ObjectLockLegalHoldStatus": NotRequired[ObjectLockLegalHoldStatusType],
        "ExpectedBucketOwner": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
    },
)
CreateMultipartUploadRequestRequestTypeDef = TypedDict(
    "CreateMultipartUploadRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "ACL": NotRequired[ObjectCannedACLType],
        "CacheControl": NotRequired[str],
        "ContentDisposition": NotRequired[str],
        "ContentEncoding": NotRequired[str],
        "ContentLanguage": NotRequired[str],
        "ContentType": NotRequired[str],
        "Expires": NotRequired[TimestampTypeDef],
        "GrantFullControl": NotRequired[str],
        "GrantRead": NotRequired[str],
        "GrantReadACP": NotRequired[str],
        "GrantWriteACP": NotRequired[str],
        "Metadata": NotRequired[Mapping[str, str]],
        "ServerSideEncryption": NotRequired[ServerSideEncryptionType],
        "StorageClass": NotRequired[StorageClassType],
        "WebsiteRedirectLocation": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "SSEKMSKeyId": NotRequired[str],
        "SSEKMSEncryptionContext": NotRequired[str],
        "BucketKeyEnabled": NotRequired[bool],
        "RequestPayer": NotRequired[Literal["requester"]],
        "Tagging": NotRequired[str],
        "ObjectLockMode": NotRequired[ObjectLockModeType],
        "ObjectLockRetainUntilDate": NotRequired[TimestampTypeDef],
        "ObjectLockLegalHoldStatus": NotRequired[ObjectLockLegalHoldStatusType],
        "ExpectedBucketOwner": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
    },
)
GetObjectRequestObjectGetTypeDef = TypedDict(
    "GetObjectRequestObjectGetTypeDef",
    {
        "IfMatch": NotRequired[str],
        "IfModifiedSince": NotRequired[TimestampTypeDef],
        "IfNoneMatch": NotRequired[str],
        "IfUnmodifiedSince": NotRequired[TimestampTypeDef],
        "Range": NotRequired[str],
        "ResponseCacheControl": NotRequired[str],
        "ResponseContentDisposition": NotRequired[str],
        "ResponseContentEncoding": NotRequired[str],
        "ResponseContentLanguage": NotRequired[str],
        "ResponseContentType": NotRequired[str],
        "ResponseExpires": NotRequired[TimestampTypeDef],
        "VersionId": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "PartNumber": NotRequired[int],
        "ExpectedBucketOwner": NotRequired[str],
        "ChecksumMode": NotRequired[Literal["ENABLED"]],
    },
)
GetObjectRequestObjectSummaryGetTypeDef = TypedDict(
    "GetObjectRequestObjectSummaryGetTypeDef",
    {
        "IfMatch": NotRequired[str],
        "IfModifiedSince": NotRequired[TimestampTypeDef],
        "IfNoneMatch": NotRequired[str],
        "IfUnmodifiedSince": NotRequired[TimestampTypeDef],
        "Range": NotRequired[str],
        "ResponseCacheControl": NotRequired[str],
        "ResponseContentDisposition": NotRequired[str],
        "ResponseContentEncoding": NotRequired[str],
        "ResponseContentLanguage": NotRequired[str],
        "ResponseContentType": NotRequired[str],
        "ResponseExpires": NotRequired[TimestampTypeDef],
        "VersionId": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "PartNumber": NotRequired[int],
        "ExpectedBucketOwner": NotRequired[str],
        "ChecksumMode": NotRequired[Literal["ENABLED"]],
    },
)
GetObjectRequestObjectVersionGetTypeDef = TypedDict(
    "GetObjectRequestObjectVersionGetTypeDef",
    {
        "IfMatch": NotRequired[str],
        "IfModifiedSince": NotRequired[TimestampTypeDef],
        "IfNoneMatch": NotRequired[str],
        "IfUnmodifiedSince": NotRequired[TimestampTypeDef],
        "Range": NotRequired[str],
        "ResponseCacheControl": NotRequired[str],
        "ResponseContentDisposition": NotRequired[str],
        "ResponseContentEncoding": NotRequired[str],
        "ResponseContentLanguage": NotRequired[str],
        "ResponseContentType": NotRequired[str],
        "ResponseExpires": NotRequired[TimestampTypeDef],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "PartNumber": NotRequired[int],
        "ExpectedBucketOwner": NotRequired[str],
        "ChecksumMode": NotRequired[Literal["ENABLED"]],
    },
)
GetObjectRequestRequestTypeDef = TypedDict(
    "GetObjectRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "IfMatch": NotRequired[str],
        "IfModifiedSince": NotRequired[TimestampTypeDef],
        "IfNoneMatch": NotRequired[str],
        "IfUnmodifiedSince": NotRequired[TimestampTypeDef],
        "Range": NotRequired[str],
        "ResponseCacheControl": NotRequired[str],
        "ResponseContentDisposition": NotRequired[str],
        "ResponseContentEncoding": NotRequired[str],
        "ResponseContentLanguage": NotRequired[str],
        "ResponseContentType": NotRequired[str],
        "ResponseExpires": NotRequired[TimestampTypeDef],
        "VersionId": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "PartNumber": NotRequired[int],
        "ExpectedBucketOwner": NotRequired[str],
        "ChecksumMode": NotRequired[Literal["ENABLED"]],
    },
)
HeadObjectRequestObjectVersionHeadTypeDef = TypedDict(
    "HeadObjectRequestObjectVersionHeadTypeDef",
    {
        "IfMatch": NotRequired[str],
        "IfModifiedSince": NotRequired[TimestampTypeDef],
        "IfNoneMatch": NotRequired[str],
        "IfUnmodifiedSince": NotRequired[TimestampTypeDef],
        "Range": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "PartNumber": NotRequired[int],
        "ExpectedBucketOwner": NotRequired[str],
        "ChecksumMode": NotRequired[Literal["ENABLED"]],
    },
)
HeadObjectRequestRequestTypeDef = TypedDict(
    "HeadObjectRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "IfMatch": NotRequired[str],
        "IfModifiedSince": NotRequired[TimestampTypeDef],
        "IfNoneMatch": NotRequired[str],
        "IfUnmodifiedSince": NotRequired[TimestampTypeDef],
        "Range": NotRequired[str],
        "VersionId": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "PartNumber": NotRequired[int],
        "ExpectedBucketOwner": NotRequired[str],
        "ChecksumMode": NotRequired[Literal["ENABLED"]],
    },
)
LifecycleExpirationTypeDef = TypedDict(
    "LifecycleExpirationTypeDef",
    {
        "Date": NotRequired[TimestampTypeDef],
        "Days": NotRequired[int],
        "ExpiredObjectDeleteMarker": NotRequired[bool],
    },
)
ObjectLockRetentionTypeDef = TypedDict(
    "ObjectLockRetentionTypeDef",
    {
        "Mode": NotRequired[ObjectLockRetentionModeType],
        "RetainUntilDate": NotRequired[TimestampTypeDef],
    },
)
PutObjectRequestBucketPutObjectTypeDef = TypedDict(
    "PutObjectRequestBucketPutObjectTypeDef",
    {
        "Key": str,
        "ACL": NotRequired[ObjectCannedACLType],
        "Body": NotRequired[BlobTypeDef],
        "CacheControl": NotRequired[str],
        "ContentDisposition": NotRequired[str],
        "ContentEncoding": NotRequired[str],
        "ContentLanguage": NotRequired[str],
        "ContentLength": NotRequired[int],
        "ContentMD5": NotRequired[str],
        "ContentType": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ChecksumCRC32": NotRequired[str],
        "ChecksumCRC32C": NotRequired[str],
        "ChecksumSHA1": NotRequired[str],
        "ChecksumSHA256": NotRequired[str],
        "Expires": NotRequired[TimestampTypeDef],
        "GrantFullControl": NotRequired[str],
        "GrantRead": NotRequired[str],
        "GrantReadACP": NotRequired[str],
        "GrantWriteACP": NotRequired[str],
        "Metadata": NotRequired[Mapping[str, str]],
        "ServerSideEncryption": NotRequired[ServerSideEncryptionType],
        "StorageClass": NotRequired[StorageClassType],
        "WebsiteRedirectLocation": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "SSEKMSKeyId": NotRequired[str],
        "SSEKMSEncryptionContext": NotRequired[str],
        "BucketKeyEnabled": NotRequired[bool],
        "RequestPayer": NotRequired[Literal["requester"]],
        "Tagging": NotRequired[str],
        "ObjectLockMode": NotRequired[ObjectLockModeType],
        "ObjectLockRetainUntilDate": NotRequired[TimestampTypeDef],
        "ObjectLockLegalHoldStatus": NotRequired[ObjectLockLegalHoldStatusType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutObjectRequestObjectPutTypeDef = TypedDict(
    "PutObjectRequestObjectPutTypeDef",
    {
        "ACL": NotRequired[ObjectCannedACLType],
        "Body": NotRequired[BlobTypeDef],
        "CacheControl": NotRequired[str],
        "ContentDisposition": NotRequired[str],
        "ContentEncoding": NotRequired[str],
        "ContentLanguage": NotRequired[str],
        "ContentLength": NotRequired[int],
        "ContentMD5": NotRequired[str],
        "ContentType": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ChecksumCRC32": NotRequired[str],
        "ChecksumCRC32C": NotRequired[str],
        "ChecksumSHA1": NotRequired[str],
        "ChecksumSHA256": NotRequired[str],
        "Expires": NotRequired[TimestampTypeDef],
        "GrantFullControl": NotRequired[str],
        "GrantRead": NotRequired[str],
        "GrantReadACP": NotRequired[str],
        "GrantWriteACP": NotRequired[str],
        "Metadata": NotRequired[Mapping[str, str]],
        "ServerSideEncryption": NotRequired[ServerSideEncryptionType],
        "StorageClass": NotRequired[StorageClassType],
        "WebsiteRedirectLocation": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "SSEKMSKeyId": NotRequired[str],
        "SSEKMSEncryptionContext": NotRequired[str],
        "BucketKeyEnabled": NotRequired[bool],
        "RequestPayer": NotRequired[Literal["requester"]],
        "Tagging": NotRequired[str],
        "ObjectLockMode": NotRequired[ObjectLockModeType],
        "ObjectLockRetainUntilDate": NotRequired[TimestampTypeDef],
        "ObjectLockLegalHoldStatus": NotRequired[ObjectLockLegalHoldStatusType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutObjectRequestObjectSummaryPutTypeDef = TypedDict(
    "PutObjectRequestObjectSummaryPutTypeDef",
    {
        "ACL": NotRequired[ObjectCannedACLType],
        "Body": NotRequired[BlobTypeDef],
        "CacheControl": NotRequired[str],
        "ContentDisposition": NotRequired[str],
        "ContentEncoding": NotRequired[str],
        "ContentLanguage": NotRequired[str],
        "ContentLength": NotRequired[int],
        "ContentMD5": NotRequired[str],
        "ContentType": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ChecksumCRC32": NotRequired[str],
        "ChecksumCRC32C": NotRequired[str],
        "ChecksumSHA1": NotRequired[str],
        "ChecksumSHA256": NotRequired[str],
        "Expires": NotRequired[TimestampTypeDef],
        "GrantFullControl": NotRequired[str],
        "GrantRead": NotRequired[str],
        "GrantReadACP": NotRequired[str],
        "GrantWriteACP": NotRequired[str],
        "Metadata": NotRequired[Mapping[str, str]],
        "ServerSideEncryption": NotRequired[ServerSideEncryptionType],
        "StorageClass": NotRequired[StorageClassType],
        "WebsiteRedirectLocation": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "SSEKMSKeyId": NotRequired[str],
        "SSEKMSEncryptionContext": NotRequired[str],
        "BucketKeyEnabled": NotRequired[bool],
        "RequestPayer": NotRequired[Literal["requester"]],
        "Tagging": NotRequired[str],
        "ObjectLockMode": NotRequired[ObjectLockModeType],
        "ObjectLockRetainUntilDate": NotRequired[TimestampTypeDef],
        "ObjectLockLegalHoldStatus": NotRequired[ObjectLockLegalHoldStatusType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutObjectRequestRequestTypeDef = TypedDict(
    "PutObjectRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "ACL": NotRequired[ObjectCannedACLType],
        "Body": NotRequired[BlobTypeDef],
        "CacheControl": NotRequired[str],
        "ContentDisposition": NotRequired[str],
        "ContentEncoding": NotRequired[str],
        "ContentLanguage": NotRequired[str],
        "ContentLength": NotRequired[int],
        "ContentMD5": NotRequired[str],
        "ContentType": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ChecksumCRC32": NotRequired[str],
        "ChecksumCRC32C": NotRequired[str],
        "ChecksumSHA1": NotRequired[str],
        "ChecksumSHA256": NotRequired[str],
        "Expires": NotRequired[TimestampTypeDef],
        "GrantFullControl": NotRequired[str],
        "GrantRead": NotRequired[str],
        "GrantReadACP": NotRequired[str],
        "GrantWriteACP": NotRequired[str],
        "Metadata": NotRequired[Mapping[str, str]],
        "ServerSideEncryption": NotRequired[ServerSideEncryptionType],
        "StorageClass": NotRequired[StorageClassType],
        "WebsiteRedirectLocation": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "SSEKMSKeyId": NotRequired[str],
        "SSEKMSEncryptionContext": NotRequired[str],
        "BucketKeyEnabled": NotRequired[bool],
        "RequestPayer": NotRequired[Literal["requester"]],
        "Tagging": NotRequired[str],
        "ObjectLockMode": NotRequired[ObjectLockModeType],
        "ObjectLockRetainUntilDate": NotRequired[TimestampTypeDef],
        "ObjectLockLegalHoldStatus": NotRequired[ObjectLockLegalHoldStatusType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
TransitionTypeDef = TypedDict(
    "TransitionTypeDef",
    {
        "Date": NotRequired[TimestampTypeDef],
        "Days": NotRequired[int],
        "StorageClass": NotRequired[TransitionStorageClassType],
    },
)
WriteGetObjectResponseRequestRequestTypeDef = TypedDict(
    "WriteGetObjectResponseRequestRequestTypeDef",
    {
        "RequestRoute": str,
        "RequestToken": str,
        "Body": NotRequired[BlobTypeDef],
        "StatusCode": NotRequired[int],
        "ErrorCode": NotRequired[str],
        "ErrorMessage": NotRequired[str],
        "AcceptRanges": NotRequired[str],
        "CacheControl": NotRequired[str],
        "ContentDisposition": NotRequired[str],
        "ContentEncoding": NotRequired[str],
        "ContentLanguage": NotRequired[str],
        "ContentLength": NotRequired[int],
        "ContentRange": NotRequired[str],
        "ContentType": NotRequired[str],
        "ChecksumCRC32": NotRequired[str],
        "ChecksumCRC32C": NotRequired[str],
        "ChecksumSHA1": NotRequired[str],
        "ChecksumSHA256": NotRequired[str],
        "DeleteMarker": NotRequired[bool],
        "ETag": NotRequired[str],
        "Expires": NotRequired[TimestampTypeDef],
        "Expiration": NotRequired[str],
        "LastModified": NotRequired[TimestampTypeDef],
        "MissingMeta": NotRequired[int],
        "Metadata": NotRequired[Mapping[str, str]],
        "ObjectLockMode": NotRequired[ObjectLockModeType],
        "ObjectLockLegalHoldStatus": NotRequired[ObjectLockLegalHoldStatusType],
        "ObjectLockRetainUntilDate": NotRequired[TimestampTypeDef],
        "PartsCount": NotRequired[int],
        "ReplicationStatus": NotRequired[ReplicationStatusType],
        "RequestCharged": NotRequired[Literal["requester"]],
        "Restore": NotRequired[str],
        "ServerSideEncryption": NotRequired[ServerSideEncryptionType],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSEKMSKeyId": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "StorageClass": NotRequired[StorageClassType],
        "TagCount": NotRequired[int],
        "VersionId": NotRequired[str],
        "BucketKeyEnabled": NotRequired[bool],
    },
)
UploadPartCopyOutputTypeDef = TypedDict(
    "UploadPartCopyOutputTypeDef",
    {
        "CopySourceVersionId": str,
        "CopyPartResult": CopyPartResultTypeDef,
        "ServerSideEncryption": ServerSideEncryptionType,
        "SSECustomerAlgorithm": str,
        "SSECustomerKeyMD5": str,
        "SSEKMSKeyId": str,
        "BucketKeyEnabled": bool,
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateBucketConfigurationTypeDef = TypedDict(
    "CreateBucketConfigurationTypeDef",
    {
        "LocationConstraint": NotRequired[BucketLocationConstraintType],
        "Location": NotRequired[LocationInfoTypeDef],
        "Bucket": NotRequired[BucketInfoTypeDef],
    },
)
CreateSessionOutputTypeDef = TypedDict(
    "CreateSessionOutputTypeDef",
    {
        "Credentials": SessionCredentialsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ObjectLockRuleTypeDef = TypedDict(
    "ObjectLockRuleTypeDef",
    {
        "DefaultRetention": NotRequired[DefaultRetentionTypeDef],
    },
)
DeleteObjectsOutputTypeDef = TypedDict(
    "DeleteObjectsOutputTypeDef",
    {
        "Deleted": List[DeletedObjectTypeDef],
        "RequestCharged": Literal["requester"],
        "Errors": List[ErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteTypeDef = TypedDict(
    "DeleteTypeDef",
    {
        "Objects": Sequence[ObjectIdentifierTypeDef],
        "Quiet": NotRequired[bool],
    },
)
S3KeyFilterExtraOutputTypeDef = TypedDict(
    "S3KeyFilterExtraOutputTypeDef",
    {
        "FilterRules": NotRequired[List[FilterRuleTypeDef]],
    },
)
S3KeyFilterOutputTypeDef = TypedDict(
    "S3KeyFilterOutputTypeDef",
    {
        "FilterRules": NotRequired[List[FilterRuleTypeDef]],
    },
)
S3KeyFilterTypeDef = TypedDict(
    "S3KeyFilterTypeDef",
    {
        "FilterRules": NotRequired[Sequence[FilterRuleTypeDef]],
    },
)
GetBucketPolicyStatusOutputTypeDef = TypedDict(
    "GetBucketPolicyStatusOutputTypeDef",
    {
        "PolicyStatus": PolicyStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetObjectAttributesPartsTypeDef = TypedDict(
    "GetObjectAttributesPartsTypeDef",
    {
        "TotalPartsCount": NotRequired[int],
        "PartNumberMarker": NotRequired[int],
        "NextPartNumberMarker": NotRequired[int],
        "MaxParts": NotRequired[int],
        "IsTruncated": NotRequired[bool],
        "Parts": NotRequired[List[ObjectPartTypeDef]],
    },
)
GetObjectLegalHoldOutputTypeDef = TypedDict(
    "GetObjectLegalHoldOutputTypeDef",
    {
        "LegalHold": ObjectLockLegalHoldTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutObjectLegalHoldRequestRequestTypeDef = TypedDict(
    "PutObjectLegalHoldRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "LegalHold": NotRequired[ObjectLockLegalHoldTypeDef],
        "RequestPayer": NotRequired[Literal["requester"]],
        "VersionId": NotRequired[str],
        "ContentMD5": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetObjectRetentionOutputTypeDef = TypedDict(
    "GetObjectRetentionOutputTypeDef",
    {
        "Retention": ObjectLockRetentionOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetPublicAccessBlockOutputTypeDef = TypedDict(
    "GetPublicAccessBlockOutputTypeDef",
    {
        "PublicAccessBlockConfiguration": PublicAccessBlockConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutPublicAccessBlockRequestRequestTypeDef = TypedDict(
    "PutPublicAccessBlockRequestRequestTypeDef",
    {
        "Bucket": str,
        "PublicAccessBlockConfiguration": PublicAccessBlockConfigurationTypeDef,
        "ContentMD5": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GrantTypeDef = TypedDict(
    "GrantTypeDef",
    {
        "Grantee": NotRequired[GranteeTypeDef],
        "Permission": NotRequired[PermissionType],
    },
)
TargetGrantTypeDef = TypedDict(
    "TargetGrantTypeDef",
    {
        "Grantee": NotRequired[GranteeTypeDef],
        "Permission": NotRequired[BucketLogsPermissionType],
    },
)
HeadBucketRequestBucketExistsWaitTypeDef = TypedDict(
    "HeadBucketRequestBucketExistsWaitTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
HeadBucketRequestBucketNotExistsWaitTypeDef = TypedDict(
    "HeadBucketRequestBucketNotExistsWaitTypeDef",
    {
        "Bucket": str,
        "ExpectedBucketOwner": NotRequired[str],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
HeadObjectRequestObjectExistsWaitTypeDef = TypedDict(
    "HeadObjectRequestObjectExistsWaitTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "IfMatch": NotRequired[str],
        "IfModifiedSince": NotRequired[TimestampTypeDef],
        "IfNoneMatch": NotRequired[str],
        "IfUnmodifiedSince": NotRequired[TimestampTypeDef],
        "Range": NotRequired[str],
        "VersionId": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "PartNumber": NotRequired[int],
        "ExpectedBucketOwner": NotRequired[str],
        "ChecksumMode": NotRequired[Literal["ENABLED"]],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
HeadObjectRequestObjectNotExistsWaitTypeDef = TypedDict(
    "HeadObjectRequestObjectNotExistsWaitTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "IfMatch": NotRequired[str],
        "IfModifiedSince": NotRequired[TimestampTypeDef],
        "IfNoneMatch": NotRequired[str],
        "IfUnmodifiedSince": NotRequired[TimestampTypeDef],
        "Range": NotRequired[str],
        "VersionId": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "PartNumber": NotRequired[int],
        "ExpectedBucketOwner": NotRequired[str],
        "ChecksumMode": NotRequired[Literal["ENABLED"]],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
MultipartUploadTypeDef = TypedDict(
    "MultipartUploadTypeDef",
    {
        "UploadId": NotRequired[str],
        "Key": NotRequired[str],
        "Initiated": NotRequired[datetime],
        "StorageClass": NotRequired[StorageClassType],
        "Owner": NotRequired[OwnerTypeDef],
        "Initiator": NotRequired[InitiatorTypeDef],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
    },
)
InputSerializationTypeDef = TypedDict(
    "InputSerializationTypeDef",
    {
        "CSV": NotRequired[CSVInputTypeDef],
        "CompressionType": NotRequired[CompressionTypeType],
        "JSON": NotRequired[JSONInputTypeDef],
        "Parquet": NotRequired[Mapping[str, Any]],
    },
)
InventoryEncryptionOutputTypeDef = TypedDict(
    "InventoryEncryptionOutputTypeDef",
    {
        "SSES3": NotRequired[Dict[str, Any]],
        "SSEKMS": NotRequired[SSEKMSTypeDef],
    },
)
InventoryEncryptionTypeDef = TypedDict(
    "InventoryEncryptionTypeDef",
    {
        "SSES3": NotRequired[Mapping[str, Any]],
        "SSEKMS": NotRequired[SSEKMSTypeDef],
    },
)
OutputSerializationTypeDef = TypedDict(
    "OutputSerializationTypeDef",
    {
        "CSV": NotRequired[CSVOutputTypeDef],
        "JSON": NotRequired[JSONOutputTypeDef],
    },
)
RuleOutputTypeDef = TypedDict(
    "RuleOutputTypeDef",
    {
        "Prefix": str,
        "Status": ExpirationStatusType,
        "Expiration": NotRequired[LifecycleExpirationOutputTypeDef],
        "ID": NotRequired[str],
        "Transition": NotRequired[TransitionOutputTypeDef],
        "NoncurrentVersionTransition": NotRequired[NoncurrentVersionTransitionTypeDef],
        "NoncurrentVersionExpiration": NotRequired[NoncurrentVersionExpirationTypeDef],
        "AbortIncompleteMultipartUpload": NotRequired[AbortIncompleteMultipartUploadTypeDef],
    },
)
ListDirectoryBucketsRequestListDirectoryBucketsPaginateTypeDef = TypedDict(
    "ListDirectoryBucketsRequestListDirectoryBucketsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListMultipartUploadsRequestListMultipartUploadsPaginateTypeDef = TypedDict(
    "ListMultipartUploadsRequestListMultipartUploadsPaginateTypeDef",
    {
        "Bucket": str,
        "Delimiter": NotRequired[str],
        "EncodingType": NotRequired[Literal["url"]],
        "Prefix": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListObjectVersionsRequestListObjectVersionsPaginateTypeDef = TypedDict(
    "ListObjectVersionsRequestListObjectVersionsPaginateTypeDef",
    {
        "Bucket": str,
        "Delimiter": NotRequired[str],
        "EncodingType": NotRequired[Literal["url"]],
        "Prefix": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "OptionalObjectAttributes": NotRequired[Sequence[Literal["RestoreStatus"]]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListObjectsRequestListObjectsPaginateTypeDef = TypedDict(
    "ListObjectsRequestListObjectsPaginateTypeDef",
    {
        "Bucket": str,
        "Delimiter": NotRequired[str],
        "EncodingType": NotRequired[Literal["url"]],
        "Prefix": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
        "OptionalObjectAttributes": NotRequired[Sequence[Literal["RestoreStatus"]]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListObjectsV2RequestListObjectsV2PaginateTypeDef = TypedDict(
    "ListObjectsV2RequestListObjectsV2PaginateTypeDef",
    {
        "Bucket": str,
        "Delimiter": NotRequired[str],
        "EncodingType": NotRequired[Literal["url"]],
        "Prefix": NotRequired[str],
        "FetchOwner": NotRequired[bool],
        "StartAfter": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
        "OptionalObjectAttributes": NotRequired[Sequence[Literal["RestoreStatus"]]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPartsRequestListPartsPaginateTypeDef = TypedDict(
    "ListPartsRequestListPartsPaginateTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "UploadId": str,
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPartsOutputTypeDef = TypedDict(
    "ListPartsOutputTypeDef",
    {
        "AbortDate": datetime,
        "AbortRuleId": str,
        "Bucket": str,
        "Key": str,
        "UploadId": str,
        "PartNumberMarker": int,
        "NextPartNumberMarker": int,
        "MaxParts": int,
        "IsTruncated": bool,
        "Parts": List[PartTypeDef],
        "Initiator": InitiatorTypeDef,
        "Owner": OwnerTypeDef,
        "StorageClass": StorageClassType,
        "RequestCharged": Literal["requester"],
        "ChecksumAlgorithm": ChecksumAlgorithmType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
MetricsTypeDef = TypedDict(
    "MetricsTypeDef",
    {
        "Status": MetricsStatusType,
        "EventThreshold": NotRequired[ReplicationTimeValueTypeDef],
    },
)
ReplicationTimeTypeDef = TypedDict(
    "ReplicationTimeTypeDef",
    {
        "Status": ReplicationTimeStatusType,
        "Time": ReplicationTimeValueTypeDef,
    },
)
NotificationConfigurationDeprecatedResponseTypeDef = TypedDict(
    "NotificationConfigurationDeprecatedResponseTypeDef",
    {
        "TopicConfiguration": TopicConfigurationDeprecatedOutputTypeDef,
        "QueueConfiguration": QueueConfigurationDeprecatedOutputTypeDef,
        "CloudFunctionConfiguration": CloudFunctionConfigurationOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
NotificationConfigurationDeprecatedTypeDef = TypedDict(
    "NotificationConfigurationDeprecatedTypeDef",
    {
        "TopicConfiguration": NotRequired[TopicConfigurationDeprecatedTypeDef],
        "QueueConfiguration": NotRequired[QueueConfigurationDeprecatedTypeDef],
        "CloudFunctionConfiguration": NotRequired[CloudFunctionConfigurationTypeDef],
    },
)
ObjectTypeDef = TypedDict(
    "ObjectTypeDef",
    {
        "Key": NotRequired[str],
        "LastModified": NotRequired[datetime],
        "ETag": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[List[ChecksumAlgorithmType]],
        "Size": NotRequired[int],
        "StorageClass": NotRequired[ObjectStorageClassType],
        "Owner": NotRequired[OwnerTypeDef],
        "RestoreStatus": NotRequired[RestoreStatusTypeDef],
    },
)
ObjectVersionTypeDef = TypedDict(
    "ObjectVersionTypeDef",
    {
        "ETag": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[List[ChecksumAlgorithmType]],
        "Size": NotRequired[int],
        "StorageClass": NotRequired[Literal["STANDARD"]],
        "Key": NotRequired[str],
        "VersionId": NotRequired[str],
        "IsLatest": NotRequired[bool],
        "LastModified": NotRequired[datetime],
        "Owner": NotRequired[OwnerTypeDef],
        "RestoreStatus": NotRequired[RestoreStatusTypeDef],
    },
)
OwnershipControlsOutputTypeDef = TypedDict(
    "OwnershipControlsOutputTypeDef",
    {
        "Rules": List[OwnershipControlsRuleTypeDef],
    },
)
OwnershipControlsTypeDef = TypedDict(
    "OwnershipControlsTypeDef",
    {
        "Rules": Sequence[OwnershipControlsRuleTypeDef],
    },
)
TargetObjectKeyFormatExtraOutputTypeDef = TypedDict(
    "TargetObjectKeyFormatExtraOutputTypeDef",
    {
        "SimplePrefix": NotRequired[Dict[str, Any]],
        "PartitionedPrefix": NotRequired[PartitionedPrefixTypeDef],
    },
)
TargetObjectKeyFormatOutputTypeDef = TypedDict(
    "TargetObjectKeyFormatOutputTypeDef",
    {
        "SimplePrefix": NotRequired[Dict[str, Any]],
        "PartitionedPrefix": NotRequired[PartitionedPrefixTypeDef],
    },
)
TargetObjectKeyFormatTypeDef = TypedDict(
    "TargetObjectKeyFormatTypeDef",
    {
        "SimplePrefix": NotRequired[Mapping[str, Any]],
        "PartitionedPrefix": NotRequired[PartitionedPrefixTypeDef],
    },
)
ProgressEventTypeDef = TypedDict(
    "ProgressEventTypeDef",
    {
        "Details": NotRequired[ProgressTypeDef],
    },
)
PutBucketRequestPaymentRequestBucketRequestPaymentPutTypeDef = TypedDict(
    "PutBucketRequestPaymentRequestBucketRequestPaymentPutTypeDef",
    {
        "RequestPaymentConfiguration": RequestPaymentConfigurationTypeDef,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutBucketRequestPaymentRequestRequestTypeDef = TypedDict(
    "PutBucketRequestPaymentRequestRequestTypeDef",
    {
        "Bucket": str,
        "RequestPaymentConfiguration": RequestPaymentConfigurationTypeDef,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutBucketVersioningRequestBucketVersioningPutTypeDef = TypedDict(
    "PutBucketVersioningRequestBucketVersioningPutTypeDef",
    {
        "VersioningConfiguration": VersioningConfigurationTypeDef,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "MFA": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutBucketVersioningRequestRequestTypeDef = TypedDict(
    "PutBucketVersioningRequestRequestTypeDef",
    {
        "Bucket": str,
        "VersioningConfiguration": VersioningConfigurationTypeDef,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "MFA": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
RoutingRuleTypeDef = TypedDict(
    "RoutingRuleTypeDef",
    {
        "Redirect": RedirectTypeDef,
        "Condition": NotRequired[ConditionTypeDef],
    },
)
RuleExtraOutputTypeDef = TypedDict(
    "RuleExtraOutputTypeDef",
    {
        "Prefix": str,
        "Status": ExpirationStatusType,
        "Expiration": NotRequired[LifecycleExpirationExtraExtraOutputTypeDef],
        "ID": NotRequired[str],
        "Transition": NotRequired[TransitionExtraExtraOutputTypeDef],
        "NoncurrentVersionTransition": NotRequired[NoncurrentVersionTransitionTypeDef],
        "NoncurrentVersionExpiration": NotRequired[NoncurrentVersionExpirationTypeDef],
        "AbortIncompleteMultipartUpload": NotRequired[AbortIncompleteMultipartUploadTypeDef],
    },
)
ServerSideEncryptionRuleTypeDef = TypedDict(
    "ServerSideEncryptionRuleTypeDef",
    {
        "ApplyServerSideEncryptionByDefault": NotRequired[ServerSideEncryptionByDefaultTypeDef],
        "BucketKeyEnabled": NotRequired[bool],
    },
)
SourceSelectionCriteriaTypeDef = TypedDict(
    "SourceSelectionCriteriaTypeDef",
    {
        "SseKmsEncryptedObjects": NotRequired[SseKmsEncryptedObjectsTypeDef],
        "ReplicaModifications": NotRequired[ReplicaModificationsTypeDef],
    },
)
StatsEventTypeDef = TypedDict(
    "StatsEventTypeDef",
    {
        "Details": NotRequired[StatsTypeDef],
    },
)
AnalyticsFilterOutputTypeDef = TypedDict(
    "AnalyticsFilterOutputTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tag": NotRequired[TagTypeDef],
        "And": NotRequired[AnalyticsAndOperatorOutputTypeDef],
    },
)
AnalyticsFilterTypeDef = TypedDict(
    "AnalyticsFilterTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tag": NotRequired[TagTypeDef],
        "And": NotRequired[AnalyticsAndOperatorTypeDef],
    },
)
IntelligentTieringFilterOutputTypeDef = TypedDict(
    "IntelligentTieringFilterOutputTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tag": NotRequired[TagTypeDef],
        "And": NotRequired[IntelligentTieringAndOperatorOutputTypeDef],
    },
)
IntelligentTieringFilterTypeDef = TypedDict(
    "IntelligentTieringFilterTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tag": NotRequired[TagTypeDef],
        "And": NotRequired[IntelligentTieringAndOperatorTypeDef],
    },
)
LifecycleRuleFilterExtraOutputTypeDef = TypedDict(
    "LifecycleRuleFilterExtraOutputTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tag": NotRequired[TagTypeDef],
        "ObjectSizeGreaterThan": NotRequired[int],
        "ObjectSizeLessThan": NotRequired[int],
        "And": NotRequired[LifecycleRuleAndOperatorExtraOutputTypeDef],
    },
)
LifecycleRuleFilterOutputTypeDef = TypedDict(
    "LifecycleRuleFilterOutputTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tag": NotRequired[TagTypeDef],
        "ObjectSizeGreaterThan": NotRequired[int],
        "ObjectSizeLessThan": NotRequired[int],
        "And": NotRequired[LifecycleRuleAndOperatorOutputTypeDef],
    },
)
LifecycleRuleFilterTypeDef = TypedDict(
    "LifecycleRuleFilterTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tag": NotRequired[TagTypeDef],
        "ObjectSizeGreaterThan": NotRequired[int],
        "ObjectSizeLessThan": NotRequired[int],
        "And": NotRequired[LifecycleRuleAndOperatorTypeDef],
    },
)
MetricsFilterOutputTypeDef = TypedDict(
    "MetricsFilterOutputTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tag": NotRequired[TagTypeDef],
        "AccessPointArn": NotRequired[str],
        "And": NotRequired[MetricsAndOperatorOutputTypeDef],
    },
)
MetricsFilterTypeDef = TypedDict(
    "MetricsFilterTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tag": NotRequired[TagTypeDef],
        "AccessPointArn": NotRequired[str],
        "And": NotRequired[MetricsAndOperatorTypeDef],
    },
)
ReplicationRuleFilterOutputTypeDef = TypedDict(
    "ReplicationRuleFilterOutputTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tag": NotRequired[TagTypeDef],
        "And": NotRequired[ReplicationRuleAndOperatorOutputTypeDef],
    },
)
ReplicationRuleFilterTypeDef = TypedDict(
    "ReplicationRuleFilterTypeDef",
    {
        "Prefix": NotRequired[str],
        "Tag": NotRequired[TagTypeDef],
        "And": NotRequired[ReplicationRuleAndOperatorTypeDef],
    },
)
PutBucketTaggingRequestBucketTaggingPutTypeDef = TypedDict(
    "PutBucketTaggingRequestBucketTaggingPutTypeDef",
    {
        "Tagging": TaggingTypeDef,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutBucketTaggingRequestRequestTypeDef = TypedDict(
    "PutBucketTaggingRequestRequestTypeDef",
    {
        "Bucket": str,
        "Tagging": TaggingTypeDef,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutObjectTaggingRequestRequestTypeDef = TypedDict(
    "PutObjectTaggingRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "Tagging": TaggingTypeDef,
        "VersionId": NotRequired[str],
        "ContentMD5": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
    },
)
StorageClassAnalysisDataExportTypeDef = TypedDict(
    "StorageClassAnalysisDataExportTypeDef",
    {
        "OutputSchemaVersion": Literal["V_1"],
        "Destination": AnalyticsExportDestinationTypeDef,
    },
)
CopyObjectRequestRequestTypeDef = TypedDict(
    "CopyObjectRequestRequestTypeDef",
    {
        "Bucket": str,
        "CopySource": CopySourceOrStrTypeDef,
        "Key": str,
        "ACL": NotRequired[ObjectCannedACLType],
        "CacheControl": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ContentDisposition": NotRequired[str],
        "ContentEncoding": NotRequired[str],
        "ContentLanguage": NotRequired[str],
        "ContentType": NotRequired[str],
        "CopySourceIfMatch": NotRequired[str],
        "CopySourceIfModifiedSince": NotRequired[TimestampTypeDef],
        "CopySourceIfNoneMatch": NotRequired[str],
        "CopySourceIfUnmodifiedSince": NotRequired[TimestampTypeDef],
        "Expires": NotRequired[TimestampTypeDef],
        "GrantFullControl": NotRequired[str],
        "GrantRead": NotRequired[str],
        "GrantReadACP": NotRequired[str],
        "GrantWriteACP": NotRequired[str],
        "Metadata": NotRequired[Mapping[str, str]],
        "MetadataDirective": NotRequired[MetadataDirectiveType],
        "TaggingDirective": NotRequired[TaggingDirectiveType],
        "ServerSideEncryption": NotRequired[ServerSideEncryptionType],
        "StorageClass": NotRequired[StorageClassType],
        "WebsiteRedirectLocation": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "SSEKMSKeyId": NotRequired[str],
        "SSEKMSEncryptionContext": NotRequired[str],
        "BucketKeyEnabled": NotRequired[bool],
        "CopySourceSSECustomerAlgorithm": NotRequired[str],
        "CopySourceSSECustomerKey": NotRequired[str],
        "CopySourceSSECustomerKeyMD5": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "Tagging": NotRequired[str],
        "ObjectLockMode": NotRequired[ObjectLockModeType],
        "ObjectLockRetainUntilDate": NotRequired[TimestampTypeDef],
        "ObjectLockLegalHoldStatus": NotRequired[ObjectLockLegalHoldStatusType],
        "ExpectedBucketOwner": NotRequired[str],
        "ExpectedSourceBucketOwner": NotRequired[str],
    },
)
UploadPartCopyRequestMultipartUploadPartCopyFromTypeDef = TypedDict(
    "UploadPartCopyRequestMultipartUploadPartCopyFromTypeDef",
    {
        "CopySource": CopySourceOrStrTypeDef,
        "CopySourceIfMatch": NotRequired[str],
        "CopySourceIfModifiedSince": NotRequired[TimestampTypeDef],
        "CopySourceIfNoneMatch": NotRequired[str],
        "CopySourceIfUnmodifiedSince": NotRequired[TimestampTypeDef],
        "CopySourceRange": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "CopySourceSSECustomerAlgorithm": NotRequired[str],
        "CopySourceSSECustomerKey": NotRequired[str],
        "CopySourceSSECustomerKeyMD5": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
        "ExpectedSourceBucketOwner": NotRequired[str],
    },
)
UploadPartCopyRequestRequestTypeDef = TypedDict(
    "UploadPartCopyRequestRequestTypeDef",
    {
        "Bucket": str,
        "CopySource": CopySourceOrStrTypeDef,
        "Key": str,
        "PartNumber": int,
        "UploadId": str,
        "CopySourceIfMatch": NotRequired[str],
        "CopySourceIfModifiedSince": NotRequired[TimestampTypeDef],
        "CopySourceIfNoneMatch": NotRequired[str],
        "CopySourceIfUnmodifiedSince": NotRequired[TimestampTypeDef],
        "CopySourceRange": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "CopySourceSSECustomerAlgorithm": NotRequired[str],
        "CopySourceSSECustomerKey": NotRequired[str],
        "CopySourceSSECustomerKeyMD5": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
        "ExpectedSourceBucketOwner": NotRequired[str],
    },
)
PutBucketCorsRequestBucketCorsPutTypeDef = TypedDict(
    "PutBucketCorsRequestBucketCorsPutTypeDef",
    {
        "CORSConfiguration": CORSConfigurationTypeDef,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutBucketCorsRequestRequestTypeDef = TypedDict(
    "PutBucketCorsRequestRequestTypeDef",
    {
        "Bucket": str,
        "CORSConfiguration": CORSConfigurationTypeDef,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
CompleteMultipartUploadRequestMultipartUploadCompleteTypeDef = TypedDict(
    "CompleteMultipartUploadRequestMultipartUploadCompleteTypeDef",
    {
        "MultipartUpload": NotRequired[CompletedMultipartUploadTypeDef],
        "ChecksumCRC32": NotRequired[str],
        "ChecksumCRC32C": NotRequired[str],
        "ChecksumSHA1": NotRequired[str],
        "ChecksumSHA256": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
    },
)
CompleteMultipartUploadRequestRequestTypeDef = TypedDict(
    "CompleteMultipartUploadRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "UploadId": str,
        "MultipartUpload": NotRequired[CompletedMultipartUploadTypeDef],
        "ChecksumCRC32": NotRequired[str],
        "ChecksumCRC32C": NotRequired[str],
        "ChecksumSHA1": NotRequired[str],
        "ChecksumSHA256": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ExpectedBucketOwner": NotRequired[str],
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
    },
)
ObjectLockRetentionUnionTypeDef = Union[
    ObjectLockRetentionTypeDef, ObjectLockRetentionOutputTypeDef
]
PutObjectRetentionRequestRequestTypeDef = TypedDict(
    "PutObjectRetentionRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "Retention": NotRequired[ObjectLockRetentionTypeDef],
        "RequestPayer": NotRequired[Literal["requester"]],
        "VersionId": NotRequired[str],
        "BypassGovernanceRetention": NotRequired[bool],
        "ContentMD5": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
RuleTypeDef = TypedDict(
    "RuleTypeDef",
    {
        "Prefix": str,
        "Status": ExpirationStatusType,
        "Expiration": NotRequired[LifecycleExpirationTypeDef],
        "ID": NotRequired[str],
        "Transition": NotRequired[TransitionTypeDef],
        "NoncurrentVersionTransition": NotRequired[NoncurrentVersionTransitionTypeDef],
        "NoncurrentVersionExpiration": NotRequired[NoncurrentVersionExpirationTypeDef],
        "AbortIncompleteMultipartUpload": NotRequired[AbortIncompleteMultipartUploadTypeDef],
    },
)
CreateBucketRequestBucketCreateTypeDef = TypedDict(
    "CreateBucketRequestBucketCreateTypeDef",
    {
        "ACL": NotRequired[BucketCannedACLType],
        "CreateBucketConfiguration": NotRequired[CreateBucketConfigurationTypeDef],
        "GrantFullControl": NotRequired[str],
        "GrantRead": NotRequired[str],
        "GrantReadACP": NotRequired[str],
        "GrantWrite": NotRequired[str],
        "GrantWriteACP": NotRequired[str],
        "ObjectLockEnabledForBucket": NotRequired[bool],
        "ObjectOwnership": NotRequired[ObjectOwnershipType],
    },
)
CreateBucketRequestRequestTypeDef = TypedDict(
    "CreateBucketRequestRequestTypeDef",
    {
        "Bucket": str,
        "ACL": NotRequired[BucketCannedACLType],
        "CreateBucketConfiguration": NotRequired[CreateBucketConfigurationTypeDef],
        "GrantFullControl": NotRequired[str],
        "GrantRead": NotRequired[str],
        "GrantReadACP": NotRequired[str],
        "GrantWrite": NotRequired[str],
        "GrantWriteACP": NotRequired[str],
        "ObjectLockEnabledForBucket": NotRequired[bool],
        "ObjectOwnership": NotRequired[ObjectOwnershipType],
    },
)
CreateBucketRequestServiceResourceCreateBucketTypeDef = TypedDict(
    "CreateBucketRequestServiceResourceCreateBucketTypeDef",
    {
        "Bucket": str,
        "ACL": NotRequired[BucketCannedACLType],
        "CreateBucketConfiguration": NotRequired[CreateBucketConfigurationTypeDef],
        "GrantFullControl": NotRequired[str],
        "GrantRead": NotRequired[str],
        "GrantReadACP": NotRequired[str],
        "GrantWrite": NotRequired[str],
        "GrantWriteACP": NotRequired[str],
        "ObjectLockEnabledForBucket": NotRequired[bool],
        "ObjectOwnership": NotRequired[ObjectOwnershipType],
    },
)
ObjectLockConfigurationTypeDef = TypedDict(
    "ObjectLockConfigurationTypeDef",
    {
        "ObjectLockEnabled": NotRequired[Literal["Enabled"]],
        "Rule": NotRequired[ObjectLockRuleTypeDef],
    },
)
DeleteObjectsRequestBucketDeleteObjectsTypeDef = TypedDict(
    "DeleteObjectsRequestBucketDeleteObjectsTypeDef",
    {
        "Delete": DeleteTypeDef,
        "MFA": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "BypassGovernanceRetention": NotRequired[bool],
        "ExpectedBucketOwner": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
    },
)
DeleteObjectsRequestRequestTypeDef = TypedDict(
    "DeleteObjectsRequestRequestTypeDef",
    {
        "Bucket": str,
        "Delete": DeleteTypeDef,
        "MFA": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "BypassGovernanceRetention": NotRequired[bool],
        "ExpectedBucketOwner": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
    },
)
NotificationConfigurationFilterExtraOutputTypeDef = TypedDict(
    "NotificationConfigurationFilterExtraOutputTypeDef",
    {
        "Key": NotRequired[S3KeyFilterExtraOutputTypeDef],
    },
)
NotificationConfigurationFilterOutputTypeDef = TypedDict(
    "NotificationConfigurationFilterOutputTypeDef",
    {
        "Key": NotRequired[S3KeyFilterOutputTypeDef],
    },
)
NotificationConfigurationFilterTypeDef = TypedDict(
    "NotificationConfigurationFilterTypeDef",
    {
        "Key": NotRequired[S3KeyFilterTypeDef],
    },
)
GetObjectAttributesOutputTypeDef = TypedDict(
    "GetObjectAttributesOutputTypeDef",
    {
        "DeleteMarker": bool,
        "LastModified": datetime,
        "VersionId": str,
        "RequestCharged": Literal["requester"],
        "ETag": str,
        "Checksum": ChecksumTypeDef,
        "ObjectParts": GetObjectAttributesPartsTypeDef,
        "StorageClass": StorageClassType,
        "ObjectSize": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AccessControlPolicyTypeDef = TypedDict(
    "AccessControlPolicyTypeDef",
    {
        "Grants": NotRequired[Sequence[GrantTypeDef]],
        "Owner": NotRequired[OwnerTypeDef],
    },
)
GetBucketAclOutputTypeDef = TypedDict(
    "GetBucketAclOutputTypeDef",
    {
        "Owner": OwnerTypeDef,
        "Grants": List[GrantTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetObjectAclOutputTypeDef = TypedDict(
    "GetObjectAclOutputTypeDef",
    {
        "Owner": OwnerTypeDef,
        "Grants": List[GrantTypeDef],
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
S3LocationTypeDef = TypedDict(
    "S3LocationTypeDef",
    {
        "BucketName": str,
        "Prefix": str,
        "Encryption": NotRequired[EncryptionTypeDef],
        "CannedACL": NotRequired[ObjectCannedACLType],
        "AccessControlList": NotRequired[Sequence[GrantTypeDef]],
        "Tagging": NotRequired[TaggingTypeDef],
        "UserMetadata": NotRequired[Sequence[MetadataEntryTypeDef]],
        "StorageClass": NotRequired[StorageClassType],
    },
)
ListMultipartUploadsOutputTypeDef = TypedDict(
    "ListMultipartUploadsOutputTypeDef",
    {
        "Bucket": str,
        "KeyMarker": str,
        "UploadIdMarker": str,
        "NextKeyMarker": str,
        "Prefix": str,
        "Delimiter": str,
        "NextUploadIdMarker": str,
        "MaxUploads": int,
        "IsTruncated": bool,
        "Uploads": List[MultipartUploadTypeDef],
        "EncodingType": Literal["url"],
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "CommonPrefixes": NotRequired[List[CommonPrefixTypeDef]],
    },
)
InventoryS3BucketDestinationOutputTypeDef = TypedDict(
    "InventoryS3BucketDestinationOutputTypeDef",
    {
        "Bucket": str,
        "Format": InventoryFormatType,
        "AccountId": NotRequired[str],
        "Prefix": NotRequired[str],
        "Encryption": NotRequired[InventoryEncryptionOutputTypeDef],
    },
)
InventoryS3BucketDestinationTypeDef = TypedDict(
    "InventoryS3BucketDestinationTypeDef",
    {
        "Bucket": str,
        "Format": InventoryFormatType,
        "AccountId": NotRequired[str],
        "Prefix": NotRequired[str],
        "Encryption": NotRequired[InventoryEncryptionTypeDef],
    },
)
SelectObjectContentRequestRequestTypeDef = TypedDict(
    "SelectObjectContentRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "Expression": str,
        "ExpressionType": Literal["SQL"],
        "InputSerialization": InputSerializationTypeDef,
        "OutputSerialization": OutputSerializationTypeDef,
        "SSECustomerAlgorithm": NotRequired[str],
        "SSECustomerKey": NotRequired[str],
        "SSECustomerKeyMD5": NotRequired[str],
        "RequestProgress": NotRequired[RequestProgressTypeDef],
        "ScanRange": NotRequired[ScanRangeTypeDef],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
SelectParametersTypeDef = TypedDict(
    "SelectParametersTypeDef",
    {
        "InputSerialization": InputSerializationTypeDef,
        "ExpressionType": Literal["SQL"],
        "Expression": str,
        "OutputSerialization": OutputSerializationTypeDef,
    },
)
GetBucketLifecycleOutputTypeDef = TypedDict(
    "GetBucketLifecycleOutputTypeDef",
    {
        "Rules": List[RuleOutputTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DestinationTypeDef = TypedDict(
    "DestinationTypeDef",
    {
        "Bucket": str,
        "Account": NotRequired[str],
        "StorageClass": NotRequired[StorageClassType],
        "AccessControlTranslation": NotRequired[AccessControlTranslationTypeDef],
        "EncryptionConfiguration": NotRequired[EncryptionConfigurationTypeDef],
        "ReplicationTime": NotRequired[ReplicationTimeTypeDef],
        "Metrics": NotRequired[MetricsTypeDef],
    },
)
PutBucketNotificationRequestRequestTypeDef = TypedDict(
    "PutBucketNotificationRequestRequestTypeDef",
    {
        "Bucket": str,
        "NotificationConfiguration": NotificationConfigurationDeprecatedTypeDef,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
ListObjectsOutputTypeDef = TypedDict(
    "ListObjectsOutputTypeDef",
    {
        "IsTruncated": bool,
        "Marker": str,
        "NextMarker": str,
        "Name": str,
        "Prefix": str,
        "Delimiter": str,
        "MaxKeys": int,
        "EncodingType": Literal["url"],
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "Contents": NotRequired[List[ObjectTypeDef]],
        "CommonPrefixes": NotRequired[List[CommonPrefixTypeDef]],
    },
)
ListObjectsV2OutputTypeDef = TypedDict(
    "ListObjectsV2OutputTypeDef",
    {
        "IsTruncated": bool,
        "Name": str,
        "Prefix": str,
        "Delimiter": str,
        "MaxKeys": int,
        "EncodingType": Literal["url"],
        "KeyCount": int,
        "ContinuationToken": str,
        "NextContinuationToken": str,
        "StartAfter": str,
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "Contents": NotRequired[List[ObjectTypeDef]],
        "CommonPrefixes": NotRequired[List[CommonPrefixTypeDef]],
    },
)
ListObjectVersionsOutputTypeDef = TypedDict(
    "ListObjectVersionsOutputTypeDef",
    {
        "IsTruncated": bool,
        "KeyMarker": str,
        "VersionIdMarker": str,
        "NextKeyMarker": str,
        "NextVersionIdMarker": str,
        "Versions": List[ObjectVersionTypeDef],
        "DeleteMarkers": List[DeleteMarkerEntryTypeDef],
        "Name": str,
        "Prefix": str,
        "Delimiter": str,
        "MaxKeys": int,
        "EncodingType": Literal["url"],
        "RequestCharged": Literal["requester"],
        "ResponseMetadata": ResponseMetadataTypeDef,
        "CommonPrefixes": NotRequired[List[CommonPrefixTypeDef]],
    },
)
GetBucketOwnershipControlsOutputTypeDef = TypedDict(
    "GetBucketOwnershipControlsOutputTypeDef",
    {
        "OwnershipControls": OwnershipControlsOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
OwnershipControlsUnionTypeDef = Union[OwnershipControlsTypeDef, OwnershipControlsOutputTypeDef]
PutBucketOwnershipControlsRequestRequestTypeDef = TypedDict(
    "PutBucketOwnershipControlsRequestRequestTypeDef",
    {
        "Bucket": str,
        "OwnershipControls": OwnershipControlsTypeDef,
        "ContentMD5": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
LoggingEnabledResponseTypeDef = TypedDict(
    "LoggingEnabledResponseTypeDef",
    {
        "TargetBucket": str,
        "TargetGrants": List[TargetGrantTypeDef],
        "TargetPrefix": str,
        "TargetObjectKeyFormat": TargetObjectKeyFormatExtraOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
LoggingEnabledOutputTypeDef = TypedDict(
    "LoggingEnabledOutputTypeDef",
    {
        "TargetBucket": str,
        "TargetPrefix": str,
        "TargetGrants": NotRequired[List[TargetGrantTypeDef]],
        "TargetObjectKeyFormat": NotRequired[TargetObjectKeyFormatOutputTypeDef],
    },
)
LoggingEnabledTypeDef = TypedDict(
    "LoggingEnabledTypeDef",
    {
        "TargetBucket": str,
        "TargetPrefix": str,
        "TargetGrants": NotRequired[Sequence[TargetGrantTypeDef]],
        "TargetObjectKeyFormat": NotRequired[TargetObjectKeyFormatTypeDef],
    },
)
GetBucketWebsiteOutputTypeDef = TypedDict(
    "GetBucketWebsiteOutputTypeDef",
    {
        "RedirectAllRequestsTo": RedirectAllRequestsToTypeDef,
        "IndexDocument": IndexDocumentTypeDef,
        "ErrorDocument": ErrorDocumentTypeDef,
        "RoutingRules": List[RoutingRuleTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
WebsiteConfigurationTypeDef = TypedDict(
    "WebsiteConfigurationTypeDef",
    {
        "ErrorDocument": NotRequired[ErrorDocumentTypeDef],
        "IndexDocument": NotRequired[IndexDocumentTypeDef],
        "RedirectAllRequestsTo": NotRequired[RedirectAllRequestsToTypeDef],
        "RoutingRules": NotRequired[Sequence[RoutingRuleTypeDef]],
    },
)
ServerSideEncryptionConfigurationOutputTypeDef = TypedDict(
    "ServerSideEncryptionConfigurationOutputTypeDef",
    {
        "Rules": List[ServerSideEncryptionRuleTypeDef],
    },
)
ServerSideEncryptionConfigurationTypeDef = TypedDict(
    "ServerSideEncryptionConfigurationTypeDef",
    {
        "Rules": Sequence[ServerSideEncryptionRuleTypeDef],
    },
)
SelectObjectContentEventStreamTypeDef = TypedDict(
    "SelectObjectContentEventStreamTypeDef",
    {
        "Records": NotRequired[RecordsEventTypeDef],
        "Stats": NotRequired[StatsEventTypeDef],
        "Progress": NotRequired[ProgressEventTypeDef],
        "Cont": NotRequired[Dict[str, Any]],
        "End": NotRequired[Dict[str, Any]],
    },
)
IntelligentTieringConfigurationOutputTypeDef = TypedDict(
    "IntelligentTieringConfigurationOutputTypeDef",
    {
        "Id": str,
        "Status": IntelligentTieringStatusType,
        "Tierings": List[TieringTypeDef],
        "Filter": NotRequired[IntelligentTieringFilterOutputTypeDef],
    },
)
IntelligentTieringConfigurationTypeDef = TypedDict(
    "IntelligentTieringConfigurationTypeDef",
    {
        "Id": str,
        "Status": IntelligentTieringStatusType,
        "Tierings": Sequence[TieringTypeDef],
        "Filter": NotRequired[IntelligentTieringFilterTypeDef],
    },
)
LifecycleRuleExtraOutputTypeDef = TypedDict(
    "LifecycleRuleExtraOutputTypeDef",
    {
        "Status": ExpirationStatusType,
        "Expiration": NotRequired[LifecycleExpirationExtraOutputTypeDef],
        "ID": NotRequired[str],
        "Prefix": NotRequired[str],
        "Filter": NotRequired[LifecycleRuleFilterExtraOutputTypeDef],
        "Transitions": NotRequired[List[TransitionExtraOutputTypeDef]],
        "NoncurrentVersionTransitions": NotRequired[List[NoncurrentVersionTransitionTypeDef]],
        "NoncurrentVersionExpiration": NotRequired[NoncurrentVersionExpirationTypeDef],
        "AbortIncompleteMultipartUpload": NotRequired[AbortIncompleteMultipartUploadTypeDef],
    },
)
LifecycleRuleOutputTypeDef = TypedDict(
    "LifecycleRuleOutputTypeDef",
    {
        "Status": ExpirationStatusType,
        "Expiration": NotRequired[LifecycleExpirationOutputTypeDef],
        "ID": NotRequired[str],
        "Prefix": NotRequired[str],
        "Filter": NotRequired[LifecycleRuleFilterOutputTypeDef],
        "Transitions": NotRequired[List[TransitionOutputTypeDef]],
        "NoncurrentVersionTransitions": NotRequired[List[NoncurrentVersionTransitionTypeDef]],
        "NoncurrentVersionExpiration": NotRequired[NoncurrentVersionExpirationTypeDef],
        "AbortIncompleteMultipartUpload": NotRequired[AbortIncompleteMultipartUploadTypeDef],
    },
)
LifecycleRuleTypeDef = TypedDict(
    "LifecycleRuleTypeDef",
    {
        "Status": ExpirationStatusType,
        "Expiration": NotRequired[LifecycleExpirationTypeDef],
        "ID": NotRequired[str],
        "Prefix": NotRequired[str],
        "Filter": NotRequired[LifecycleRuleFilterTypeDef],
        "Transitions": NotRequired[Sequence[TransitionTypeDef]],
        "NoncurrentVersionTransitions": NotRequired[Sequence[NoncurrentVersionTransitionTypeDef]],
        "NoncurrentVersionExpiration": NotRequired[NoncurrentVersionExpirationTypeDef],
        "AbortIncompleteMultipartUpload": NotRequired[AbortIncompleteMultipartUploadTypeDef],
    },
)
MetricsConfigurationOutputTypeDef = TypedDict(
    "MetricsConfigurationOutputTypeDef",
    {
        "Id": str,
        "Filter": NotRequired[MetricsFilterOutputTypeDef],
    },
)
MetricsConfigurationTypeDef = TypedDict(
    "MetricsConfigurationTypeDef",
    {
        "Id": str,
        "Filter": NotRequired[MetricsFilterTypeDef],
    },
)
StorageClassAnalysisTypeDef = TypedDict(
    "StorageClassAnalysisTypeDef",
    {
        "DataExport": NotRequired[StorageClassAnalysisDataExportTypeDef],
    },
)
LifecycleConfigurationTypeDef = TypedDict(
    "LifecycleConfigurationTypeDef",
    {
        "Rules": Sequence[RuleTypeDef],
    },
)
GetObjectLockConfigurationOutputTypeDef = TypedDict(
    "GetObjectLockConfigurationOutputTypeDef",
    {
        "ObjectLockConfiguration": ObjectLockConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutObjectLockConfigurationRequestRequestTypeDef = TypedDict(
    "PutObjectLockConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "ObjectLockConfiguration": NotRequired[ObjectLockConfigurationTypeDef],
        "RequestPayer": NotRequired[Literal["requester"]],
        "Token": NotRequired[str],
        "ContentMD5": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
LambdaFunctionConfigurationExtraOutputTypeDef = TypedDict(
    "LambdaFunctionConfigurationExtraOutputTypeDef",
    {
        "LambdaFunctionArn": str,
        "Events": List[EventType],
        "Id": NotRequired[str],
        "Filter": NotRequired[NotificationConfigurationFilterExtraOutputTypeDef],
    },
)
QueueConfigurationExtraOutputTypeDef = TypedDict(
    "QueueConfigurationExtraOutputTypeDef",
    {
        "QueueArn": str,
        "Events": List[EventType],
        "Id": NotRequired[str],
        "Filter": NotRequired[NotificationConfigurationFilterExtraOutputTypeDef],
    },
)
TopicConfigurationExtraOutputTypeDef = TypedDict(
    "TopicConfigurationExtraOutputTypeDef",
    {
        "TopicArn": str,
        "Events": List[EventType],
        "Id": NotRequired[str],
        "Filter": NotRequired[NotificationConfigurationFilterExtraOutputTypeDef],
    },
)
LambdaFunctionConfigurationOutputTypeDef = TypedDict(
    "LambdaFunctionConfigurationOutputTypeDef",
    {
        "LambdaFunctionArn": str,
        "Events": List[EventType],
        "Id": NotRequired[str],
        "Filter": NotRequired[NotificationConfigurationFilterOutputTypeDef],
    },
)
QueueConfigurationOutputTypeDef = TypedDict(
    "QueueConfigurationOutputTypeDef",
    {
        "QueueArn": str,
        "Events": List[EventType],
        "Id": NotRequired[str],
        "Filter": NotRequired[NotificationConfigurationFilterOutputTypeDef],
    },
)
TopicConfigurationOutputTypeDef = TypedDict(
    "TopicConfigurationOutputTypeDef",
    {
        "TopicArn": str,
        "Events": List[EventType],
        "Id": NotRequired[str],
        "Filter": NotRequired[NotificationConfigurationFilterOutputTypeDef],
    },
)
LambdaFunctionConfigurationTypeDef = TypedDict(
    "LambdaFunctionConfigurationTypeDef",
    {
        "LambdaFunctionArn": str,
        "Events": Sequence[EventType],
        "Id": NotRequired[str],
        "Filter": NotRequired[NotificationConfigurationFilterTypeDef],
    },
)
QueueConfigurationTypeDef = TypedDict(
    "QueueConfigurationTypeDef",
    {
        "QueueArn": str,
        "Events": Sequence[EventType],
        "Id": NotRequired[str],
        "Filter": NotRequired[NotificationConfigurationFilterTypeDef],
    },
)
TopicConfigurationTypeDef = TypedDict(
    "TopicConfigurationTypeDef",
    {
        "TopicArn": str,
        "Events": Sequence[EventType],
        "Id": NotRequired[str],
        "Filter": NotRequired[NotificationConfigurationFilterTypeDef],
    },
)
PutBucketAclRequestBucketAclPutTypeDef = TypedDict(
    "PutBucketAclRequestBucketAclPutTypeDef",
    {
        "ACL": NotRequired[BucketCannedACLType],
        "AccessControlPolicy": NotRequired[AccessControlPolicyTypeDef],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "GrantFullControl": NotRequired[str],
        "GrantRead": NotRequired[str],
        "GrantReadACP": NotRequired[str],
        "GrantWrite": NotRequired[str],
        "GrantWriteACP": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutBucketAclRequestRequestTypeDef = TypedDict(
    "PutBucketAclRequestRequestTypeDef",
    {
        "Bucket": str,
        "ACL": NotRequired[BucketCannedACLType],
        "AccessControlPolicy": NotRequired[AccessControlPolicyTypeDef],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "GrantFullControl": NotRequired[str],
        "GrantRead": NotRequired[str],
        "GrantReadACP": NotRequired[str],
        "GrantWrite": NotRequired[str],
        "GrantWriteACP": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutObjectAclRequestObjectAclPutTypeDef = TypedDict(
    "PutObjectAclRequestObjectAclPutTypeDef",
    {
        "ACL": NotRequired[ObjectCannedACLType],
        "AccessControlPolicy": NotRequired[AccessControlPolicyTypeDef],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "GrantFullControl": NotRequired[str],
        "GrantRead": NotRequired[str],
        "GrantReadACP": NotRequired[str],
        "GrantWrite": NotRequired[str],
        "GrantWriteACP": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "VersionId": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutObjectAclRequestRequestTypeDef = TypedDict(
    "PutObjectAclRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "ACL": NotRequired[ObjectCannedACLType],
        "AccessControlPolicy": NotRequired[AccessControlPolicyTypeDef],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "GrantFullControl": NotRequired[str],
        "GrantRead": NotRequired[str],
        "GrantReadACP": NotRequired[str],
        "GrantWrite": NotRequired[str],
        "GrantWriteACP": NotRequired[str],
        "RequestPayer": NotRequired[Literal["requester"]],
        "VersionId": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
OutputLocationTypeDef = TypedDict(
    "OutputLocationTypeDef",
    {
        "S3": NotRequired[S3LocationTypeDef],
    },
)
InventoryDestinationOutputTypeDef = TypedDict(
    "InventoryDestinationOutputTypeDef",
    {
        "S3BucketDestination": InventoryS3BucketDestinationOutputTypeDef,
    },
)
InventoryDestinationTypeDef = TypedDict(
    "InventoryDestinationTypeDef",
    {
        "S3BucketDestination": InventoryS3BucketDestinationTypeDef,
    },
)
ReplicationRuleOutputTypeDef = TypedDict(
    "ReplicationRuleOutputTypeDef",
    {
        "Status": ReplicationRuleStatusType,
        "Destination": DestinationTypeDef,
        "ID": NotRequired[str],
        "Priority": NotRequired[int],
        "Prefix": NotRequired[str],
        "Filter": NotRequired[ReplicationRuleFilterOutputTypeDef],
        "SourceSelectionCriteria": NotRequired[SourceSelectionCriteriaTypeDef],
        "ExistingObjectReplication": NotRequired[ExistingObjectReplicationTypeDef],
        "DeleteMarkerReplication": NotRequired[DeleteMarkerReplicationTypeDef],
    },
)
ReplicationRuleTypeDef = TypedDict(
    "ReplicationRuleTypeDef",
    {
        "Status": ReplicationRuleStatusType,
        "Destination": DestinationTypeDef,
        "ID": NotRequired[str],
        "Priority": NotRequired[int],
        "Prefix": NotRequired[str],
        "Filter": NotRequired[ReplicationRuleFilterTypeDef],
        "SourceSelectionCriteria": NotRequired[SourceSelectionCriteriaTypeDef],
        "ExistingObjectReplication": NotRequired[ExistingObjectReplicationTypeDef],
        "DeleteMarkerReplication": NotRequired[DeleteMarkerReplicationTypeDef],
    },
)
GetBucketLoggingOutputTypeDef = TypedDict(
    "GetBucketLoggingOutputTypeDef",
    {
        "LoggingEnabled": LoggingEnabledOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BucketLoggingStatusTypeDef = TypedDict(
    "BucketLoggingStatusTypeDef",
    {
        "LoggingEnabled": NotRequired[LoggingEnabledTypeDef],
    },
)
PutBucketWebsiteRequestBucketWebsitePutTypeDef = TypedDict(
    "PutBucketWebsiteRequestBucketWebsitePutTypeDef",
    {
        "WebsiteConfiguration": WebsiteConfigurationTypeDef,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutBucketWebsiteRequestRequestTypeDef = TypedDict(
    "PutBucketWebsiteRequestRequestTypeDef",
    {
        "Bucket": str,
        "WebsiteConfiguration": WebsiteConfigurationTypeDef,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketEncryptionOutputTypeDef = TypedDict(
    "GetBucketEncryptionOutputTypeDef",
    {
        "ServerSideEncryptionConfiguration": ServerSideEncryptionConfigurationOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutBucketEncryptionRequestRequestTypeDef = TypedDict(
    "PutBucketEncryptionRequestRequestTypeDef",
    {
        "Bucket": str,
        "ServerSideEncryptionConfiguration": ServerSideEncryptionConfigurationTypeDef,
        "ContentMD5": NotRequired[str],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
ServerSideEncryptionConfigurationUnionTypeDef = Union[
    ServerSideEncryptionConfigurationTypeDef, ServerSideEncryptionConfigurationOutputTypeDef
]
SelectObjectContentOutputTypeDef = TypedDict(
    "SelectObjectContentOutputTypeDef",
    {
        "Payload": "EventStream[SelectObjectContentEventStreamTypeDef]",
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetBucketIntelligentTieringConfigurationOutputTypeDef = TypedDict(
    "GetBucketIntelligentTieringConfigurationOutputTypeDef",
    {
        "IntelligentTieringConfiguration": IntelligentTieringConfigurationOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListBucketIntelligentTieringConfigurationsOutputTypeDef = TypedDict(
    "ListBucketIntelligentTieringConfigurationsOutputTypeDef",
    {
        "IsTruncated": bool,
        "ContinuationToken": str,
        "NextContinuationToken": str,
        "IntelligentTieringConfigurationList": List[IntelligentTieringConfigurationOutputTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
IntelligentTieringConfigurationUnionTypeDef = Union[
    IntelligentTieringConfigurationTypeDef, IntelligentTieringConfigurationOutputTypeDef
]
PutBucketIntelligentTieringConfigurationRequestRequestTypeDef = TypedDict(
    "PutBucketIntelligentTieringConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "Id": str,
        "IntelligentTieringConfiguration": IntelligentTieringConfigurationTypeDef,
    },
)
GetBucketLifecycleConfigurationOutputTypeDef = TypedDict(
    "GetBucketLifecycleConfigurationOutputTypeDef",
    {
        "Rules": List[LifecycleRuleOutputTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BucketLifecycleConfigurationTypeDef = TypedDict(
    "BucketLifecycleConfigurationTypeDef",
    {
        "Rules": Sequence[LifecycleRuleTypeDef],
    },
)
GetBucketMetricsConfigurationOutputTypeDef = TypedDict(
    "GetBucketMetricsConfigurationOutputTypeDef",
    {
        "MetricsConfiguration": MetricsConfigurationOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListBucketMetricsConfigurationsOutputTypeDef = TypedDict(
    "ListBucketMetricsConfigurationsOutputTypeDef",
    {
        "IsTruncated": bool,
        "ContinuationToken": str,
        "NextContinuationToken": str,
        "MetricsConfigurationList": List[MetricsConfigurationOutputTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
MetricsConfigurationUnionTypeDef = Union[
    MetricsConfigurationTypeDef, MetricsConfigurationOutputTypeDef
]
PutBucketMetricsConfigurationRequestRequestTypeDef = TypedDict(
    "PutBucketMetricsConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "Id": str,
        "MetricsConfiguration": MetricsConfigurationTypeDef,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
AnalyticsConfigurationOutputTypeDef = TypedDict(
    "AnalyticsConfigurationOutputTypeDef",
    {
        "Id": str,
        "StorageClassAnalysis": StorageClassAnalysisTypeDef,
        "Filter": NotRequired[AnalyticsFilterOutputTypeDef],
    },
)
AnalyticsConfigurationTypeDef = TypedDict(
    "AnalyticsConfigurationTypeDef",
    {
        "Id": str,
        "StorageClassAnalysis": StorageClassAnalysisTypeDef,
        "Filter": NotRequired[AnalyticsFilterTypeDef],
    },
)
PutBucketLifecycleRequestBucketLifecyclePutTypeDef = TypedDict(
    "PutBucketLifecycleRequestBucketLifecyclePutTypeDef",
    {
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "LifecycleConfiguration": NotRequired[LifecycleConfigurationTypeDef],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutBucketLifecycleRequestRequestTypeDef = TypedDict(
    "PutBucketLifecycleRequestRequestTypeDef",
    {
        "Bucket": str,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "LifecycleConfiguration": NotRequired[LifecycleConfigurationTypeDef],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
NotificationConfigurationResponseTypeDef = TypedDict(
    "NotificationConfigurationResponseTypeDef",
    {
        "TopicConfigurations": List[TopicConfigurationOutputTypeDef],
        "QueueConfigurations": List[QueueConfigurationOutputTypeDef],
        "LambdaFunctionConfigurations": List[LambdaFunctionConfigurationOutputTypeDef],
        "EventBridgeConfiguration": Dict[str, Any],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
NotificationConfigurationTypeDef = TypedDict(
    "NotificationConfigurationTypeDef",
    {
        "TopicConfigurations": NotRequired[Sequence[TopicConfigurationTypeDef]],
        "QueueConfigurations": NotRequired[Sequence[QueueConfigurationTypeDef]],
        "LambdaFunctionConfigurations": NotRequired[Sequence[LambdaFunctionConfigurationTypeDef]],
        "EventBridgeConfiguration": NotRequired[Mapping[str, Any]],
    },
)
RestoreRequestTypeDef = TypedDict(
    "RestoreRequestTypeDef",
    {
        "Days": NotRequired[int],
        "GlacierJobParameters": NotRequired[GlacierJobParametersTypeDef],
        "Type": NotRequired[Literal["SELECT"]],
        "Tier": NotRequired[TierType],
        "Description": NotRequired[str],
        "SelectParameters": NotRequired[SelectParametersTypeDef],
        "OutputLocation": NotRequired[OutputLocationTypeDef],
    },
)
InventoryConfigurationOutputTypeDef = TypedDict(
    "InventoryConfigurationOutputTypeDef",
    {
        "Destination": InventoryDestinationOutputTypeDef,
        "IsEnabled": bool,
        "Id": str,
        "IncludedObjectVersions": InventoryIncludedObjectVersionsType,
        "Schedule": InventoryScheduleTypeDef,
        "Filter": NotRequired[InventoryFilterTypeDef],
        "OptionalFields": NotRequired[List[InventoryOptionalFieldType]],
    },
)
InventoryConfigurationTypeDef = TypedDict(
    "InventoryConfigurationTypeDef",
    {
        "Destination": InventoryDestinationTypeDef,
        "IsEnabled": bool,
        "Id": str,
        "IncludedObjectVersions": InventoryIncludedObjectVersionsType,
        "Schedule": InventoryScheduleTypeDef,
        "Filter": NotRequired[InventoryFilterTypeDef],
        "OptionalFields": NotRequired[Sequence[InventoryOptionalFieldType]],
    },
)
ReplicationConfigurationOutputTypeDef = TypedDict(
    "ReplicationConfigurationOutputTypeDef",
    {
        "Role": str,
        "Rules": List[ReplicationRuleOutputTypeDef],
    },
)
ReplicationConfigurationTypeDef = TypedDict(
    "ReplicationConfigurationTypeDef",
    {
        "Role": str,
        "Rules": Sequence[ReplicationRuleTypeDef],
    },
)
PutBucketLoggingRequestBucketLoggingPutTypeDef = TypedDict(
    "PutBucketLoggingRequestBucketLoggingPutTypeDef",
    {
        "BucketLoggingStatus": BucketLoggingStatusTypeDef,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutBucketLoggingRequestRequestTypeDef = TypedDict(
    "PutBucketLoggingRequestRequestTypeDef",
    {
        "Bucket": str,
        "BucketLoggingStatus": BucketLoggingStatusTypeDef,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutBucketLifecycleConfigurationRequestBucketLifecycleConfigurationPutTypeDef = TypedDict(
    "PutBucketLifecycleConfigurationRequestBucketLifecycleConfigurationPutTypeDef",
    {
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "LifecycleConfiguration": NotRequired[BucketLifecycleConfigurationTypeDef],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutBucketLifecycleConfigurationRequestRequestTypeDef = TypedDict(
    "PutBucketLifecycleConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "LifecycleConfiguration": NotRequired[BucketLifecycleConfigurationTypeDef],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketAnalyticsConfigurationOutputTypeDef = TypedDict(
    "GetBucketAnalyticsConfigurationOutputTypeDef",
    {
        "AnalyticsConfiguration": AnalyticsConfigurationOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListBucketAnalyticsConfigurationsOutputTypeDef = TypedDict(
    "ListBucketAnalyticsConfigurationsOutputTypeDef",
    {
        "IsTruncated": bool,
        "ContinuationToken": str,
        "NextContinuationToken": str,
        "AnalyticsConfigurationList": List[AnalyticsConfigurationOutputTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AnalyticsConfigurationUnionTypeDef = Union[
    AnalyticsConfigurationTypeDef, AnalyticsConfigurationOutputTypeDef
]
PutBucketAnalyticsConfigurationRequestRequestTypeDef = TypedDict(
    "PutBucketAnalyticsConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "Id": str,
        "AnalyticsConfiguration": AnalyticsConfigurationTypeDef,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
PutBucketNotificationConfigurationRequestBucketNotificationPutTypeDef = TypedDict(
    "PutBucketNotificationConfigurationRequestBucketNotificationPutTypeDef",
    {
        "NotificationConfiguration": NotificationConfigurationTypeDef,
        "ExpectedBucketOwner": NotRequired[str],
        "SkipDestinationValidation": NotRequired[bool],
    },
)
PutBucketNotificationConfigurationRequestRequestTypeDef = TypedDict(
    "PutBucketNotificationConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "NotificationConfiguration": NotificationConfigurationTypeDef,
        "ExpectedBucketOwner": NotRequired[str],
        "SkipDestinationValidation": NotRequired[bool],
    },
)
RestoreObjectRequestObjectRestoreObjectTypeDef = TypedDict(
    "RestoreObjectRequestObjectRestoreObjectTypeDef",
    {
        "VersionId": NotRequired[str],
        "RestoreRequest": NotRequired[RestoreRequestTypeDef],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
RestoreObjectRequestObjectSummaryRestoreObjectTypeDef = TypedDict(
    "RestoreObjectRequestObjectSummaryRestoreObjectTypeDef",
    {
        "VersionId": NotRequired[str],
        "RestoreRequest": NotRequired[RestoreRequestTypeDef],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
RestoreObjectRequestRequestTypeDef = TypedDict(
    "RestoreObjectRequestRequestTypeDef",
    {
        "Bucket": str,
        "Key": str,
        "VersionId": NotRequired[str],
        "RestoreRequest": NotRequired[RestoreRequestTypeDef],
        "RequestPayer": NotRequired[Literal["requester"]],
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketInventoryConfigurationOutputTypeDef = TypedDict(
    "GetBucketInventoryConfigurationOutputTypeDef",
    {
        "InventoryConfiguration": InventoryConfigurationOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListBucketInventoryConfigurationsOutputTypeDef = TypedDict(
    "ListBucketInventoryConfigurationsOutputTypeDef",
    {
        "ContinuationToken": str,
        "InventoryConfigurationList": List[InventoryConfigurationOutputTypeDef],
        "IsTruncated": bool,
        "NextContinuationToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
InventoryConfigurationUnionTypeDef = Union[
    InventoryConfigurationTypeDef, InventoryConfigurationOutputTypeDef
]
PutBucketInventoryConfigurationRequestRequestTypeDef = TypedDict(
    "PutBucketInventoryConfigurationRequestRequestTypeDef",
    {
        "Bucket": str,
        "Id": str,
        "InventoryConfiguration": InventoryConfigurationTypeDef,
        "ExpectedBucketOwner": NotRequired[str],
    },
)
GetBucketReplicationOutputTypeDef = TypedDict(
    "GetBucketReplicationOutputTypeDef",
    {
        "ReplicationConfiguration": ReplicationConfigurationOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutBucketReplicationRequestRequestTypeDef = TypedDict(
    "PutBucketReplicationRequestRequestTypeDef",
    {
        "Bucket": str,
        "ReplicationConfiguration": ReplicationConfigurationTypeDef,
        "ChecksumAlgorithm": NotRequired[ChecksumAlgorithmType],
        "Token": NotRequired[str],
        "ExpectedBucketOwner": NotRequired[str],
    },
)
ReplicationConfigurationUnionTypeDef = Union[
    ReplicationConfigurationTypeDef, ReplicationConfigurationOutputTypeDef
]
