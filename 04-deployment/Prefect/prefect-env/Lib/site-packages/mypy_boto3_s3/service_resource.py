"""
Type annotations for s3 service ServiceResource

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/)

Usage::

    ```python
    from boto3.session import Session

    from mypy_boto3_s3.service_resource import S3ServiceResource
    import mypy_boto3_s3.service_resource as s3_resources

    session = Session()
    resource: S3ServiceResource = session.resource("s3")

    my_bucket: s3_resources.Bucket = resource.Bucket(...)
    my_bucket_acl: s3_resources.BucketAcl = resource.BucketAcl(...)
    my_bucket_cors: s3_resources.BucketCors = resource.BucketCors(...)
    my_bucket_lifecycle: s3_resources.BucketLifecycle = resource.BucketLifecycle(...)
    my_bucket_lifecycle_configuration: s3_resources.BucketLifecycleConfiguration = resource.BucketLifecycleConfiguration(...)
    my_bucket_logging: s3_resources.BucketLogging = resource.BucketLogging(...)
    my_bucket_notification: s3_resources.BucketNotification = resource.BucketNotification(...)
    my_bucket_policy: s3_resources.BucketPolicy = resource.BucketPolicy(...)
    my_bucket_request_payment: s3_resources.BucketRequestPayment = resource.BucketRequestPayment(...)
    my_bucket_tagging: s3_resources.BucketTagging = resource.BucketTagging(...)
    my_bucket_versioning: s3_resources.BucketVersioning = resource.BucketVersioning(...)
    my_bucket_website: s3_resources.BucketWebsite = resource.BucketWebsite(...)
    my_multipart_upload: s3_resources.MultipartUpload = resource.MultipartUpload(...)
    my_multipart_upload_part: s3_resources.MultipartUploadPart = resource.MultipartUploadPart(...)
    my_object: s3_resources.Object = resource.Object(...)
    my_object_acl: s3_resources.ObjectAcl = resource.ObjectAcl(...)
    my_object_summary: s3_resources.ObjectSummary = resource.ObjectSummary(...)
    my_object_version: s3_resources.ObjectVersion = resource.ObjectVersion(...)
```
"""

import sys
from datetime import datetime
from typing import Any, Callable, Dict, Iterator, List, Mapping, Optional, Sequence

from boto3.resources.base import ResourceMeta, ServiceResource
from boto3.resources.collection import ResourceCollection
from boto3.s3.transfer import TransferConfig
from botocore.client import BaseClient

from .client import S3Client
from .literals import (
    ArchiveStatusType,
    BucketCannedACLType,
    BucketVersioningStatusType,
    ChecksumAlgorithmType,
    MetadataDirectiveType,
    MFADeleteStatusType,
    ObjectCannedACLType,
    ObjectLockLegalHoldStatusType,
    ObjectLockModeType,
    ObjectOwnershipType,
    ObjectStorageClassType,
    PayerType,
    ReplicationStatusType,
    ServerSideEncryptionType,
    StorageClassType,
    TaggingDirectiveType,
)
from .type_defs import (
    AbortMultipartUploadOutputTypeDef,
    AccessControlPolicyTypeDef,
    BlobTypeDef,
    BucketLifecycleConfigurationTypeDef,
    BucketLoggingStatusTypeDef,
    CompletedMultipartUploadTypeDef,
    CopyObjectOutputTypeDef,
    CopySourceOrStrTypeDef,
    CopySourceTypeDef,
    CORSConfigurationTypeDef,
    CORSRuleExtraOutputTypeDef,
    CreateBucketConfigurationTypeDef,
    CreateBucketOutputTypeDef,
    DeleteObjectOutputTypeDef,
    DeleteObjectsOutputTypeDef,
    DeleteTypeDef,
    ErrorDocumentResponseTypeDef,
    FileobjTypeDef,
    GetObjectOutputTypeDef,
    GrantTypeDef,
    HeadObjectOutputTypeDef,
    IndexDocumentResponseTypeDef,
    InitiatorResponseTypeDef,
    LambdaFunctionConfigurationExtraOutputTypeDef,
    LifecycleConfigurationTypeDef,
    LifecycleRuleExtraOutputTypeDef,
    LoggingEnabledResponseTypeDef,
    NotificationConfigurationTypeDef,
    OwnerResponseTypeDef,
    PutObjectAclOutputTypeDef,
    PutObjectOutputTypeDef,
    QueueConfigurationExtraOutputTypeDef,
    RedirectAllRequestsToResponseTypeDef,
    RequestPaymentConfigurationTypeDef,
    RestoreObjectOutputTypeDef,
    RestoreRequestTypeDef,
    RestoreStatusResponseTypeDef,
    RoutingRuleTypeDef,
    RuleExtraOutputTypeDef,
    TaggingTypeDef,
    TagTypeDef,
    TimestampTypeDef,
    TopicConfigurationExtraOutputTypeDef,
    UploadPartCopyOutputTypeDef,
    UploadPartOutputTypeDef,
    VersioningConfigurationTypeDef,
    WebsiteConfigurationTypeDef,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal

__all__ = (
    "S3ServiceResource",
    "Bucket",
    "BucketAcl",
    "BucketCors",
    "BucketLifecycle",
    "BucketLifecycleConfiguration",
    "BucketLogging",
    "BucketNotification",
    "BucketPolicy",
    "BucketRequestPayment",
    "BucketTagging",
    "BucketVersioning",
    "BucketWebsite",
    "MultipartUpload",
    "MultipartUploadPart",
    "Object",
    "ObjectAcl",
    "ObjectSummary",
    "ObjectVersion",
    "ServiceResourceBucketsCollection",
    "BucketMultipartUploadsCollection",
    "BucketObjectVersionsCollection",
    "BucketObjectsCollection",
    "MultipartUploadPartsCollection",
)


class ServiceResourceBucketsCollection(ResourceCollection):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.buckets)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#serviceresourcebucketscollection)
    """

    def all(self) -> "ServiceResourceBucketsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.buckets)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#serviceresourcebucketscollection)
        """

    def filter(self) -> "ServiceResourceBucketsCollection":  # type: ignore
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.buckets)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#serviceresourcebucketscollection)
        """

    def limit(self, count: int) -> "ServiceResourceBucketsCollection":
        """
        Return at most this many Buckets.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.buckets)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#serviceresourcebucketscollection)
        """

    def page_size(self, count: int) -> "ServiceResourceBucketsCollection":
        """
        Fetch at most this many Buckets per service request.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.buckets)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#serviceresourcebucketscollection)
        """

    def pages(self) -> Iterator[List["Bucket"]]:
        """
        A generator which yields pages of Buckets.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.buckets)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#serviceresourcebucketscollection)
        """

    def __iter__(self) -> Iterator["Bucket"]:
        """
        A generator which yields Buckets.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.buckets)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#serviceresourcebucketscollection)
        """


class BucketMultipartUploadsCollection(ResourceCollection):
    def all(self) -> "BucketMultipartUploadsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Delimiter: str = ...,
        EncodingType: Literal["url"] = ...,
        KeyMarker: str = ...,
        MaxUploads: int = ...,
        Prefix: str = ...,
        UploadIdMarker: str = ...,
        ExpectedBucketOwner: str = ...,
        RequestPayer: Literal["requester"] = ...,
    ) -> "BucketMultipartUploadsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "BucketMultipartUploadsCollection":
        """
        Return at most this many MultipartUploads.
        """

    def page_size(self, count: int) -> "BucketMultipartUploadsCollection":
        """
        Fetch at most this many MultipartUploads per service request.
        """

    def pages(self) -> Iterator[List["MultipartUpload"]]:
        """
        A generator which yields pages of MultipartUploads.
        """

    def __iter__(self) -> Iterator["MultipartUpload"]:
        """
        A generator which yields MultipartUploads.
        """


class BucketObjectVersionsCollection(ResourceCollection):
    def all(self) -> "BucketObjectVersionsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Delimiter: str = ...,
        EncodingType: Literal["url"] = ...,
        KeyMarker: str = ...,
        MaxKeys: int = ...,
        Prefix: str = ...,
        VersionIdMarker: str = ...,
        ExpectedBucketOwner: str = ...,
        RequestPayer: Literal["requester"] = ...,
        OptionalObjectAttributes: Sequence[Literal["RestoreStatus"]] = ...,
    ) -> "BucketObjectVersionsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def delete(
        self,
        *,
        MFA: str = ...,
        RequestPayer: Literal["requester"] = ...,
        BypassGovernanceRetention: bool = ...,
        ExpectedBucketOwner: str = ...,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
    ) -> List[DeleteObjectsOutputTypeDef]:
        """
        Batch method.
        """

    def limit(self, count: int) -> "BucketObjectVersionsCollection":
        """
        Return at most this many ObjectVersions.
        """

    def page_size(self, count: int) -> "BucketObjectVersionsCollection":
        """
        Fetch at most this many ObjectVersions per service request.
        """

    def pages(self) -> Iterator[List["ObjectVersion"]]:
        """
        A generator which yields pages of ObjectVersions.
        """

    def __iter__(self) -> Iterator["ObjectVersion"]:
        """
        A generator which yields ObjectVersions.
        """


class BucketObjectsCollection(ResourceCollection):
    def all(self) -> "BucketObjectsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        Delimiter: str = ...,
        EncodingType: Literal["url"] = ...,
        Marker: str = ...,
        MaxKeys: int = ...,
        Prefix: str = ...,
        RequestPayer: Literal["requester"] = ...,
        ExpectedBucketOwner: str = ...,
        OptionalObjectAttributes: Sequence[Literal["RestoreStatus"]] = ...,
    ) -> "BucketObjectsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def delete(
        self,
        *,
        MFA: str = ...,
        RequestPayer: Literal["requester"] = ...,
        BypassGovernanceRetention: bool = ...,
        ExpectedBucketOwner: str = ...,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
    ) -> List[DeleteObjectsOutputTypeDef]:
        """
        Batch method.
        """

    def limit(self, count: int) -> "BucketObjectsCollection":
        """
        Return at most this many ObjectSummarys.
        """

    def page_size(self, count: int) -> "BucketObjectsCollection":
        """
        Fetch at most this many ObjectSummarys per service request.
        """

    def pages(self) -> Iterator[List["ObjectSummary"]]:
        """
        A generator which yields pages of ObjectSummarys.
        """

    def __iter__(self) -> Iterator["ObjectSummary"]:
        """
        A generator which yields ObjectSummarys.
        """


class MultipartUploadPartsCollection(ResourceCollection):
    def all(self) -> "MultipartUploadPartsCollection":
        """
        Get all items from the collection, optionally with a custom page size and item count limit.
        """

    def filter(  # type: ignore
        self,
        *,
        MaxParts: int = ...,
        PartNumberMarker: int = ...,
        RequestPayer: Literal["requester"] = ...,
        ExpectedBucketOwner: str = ...,
        SSECustomerAlgorithm: str = ...,
        SSECustomerKey: str = ...,
        SSECustomerKeyMD5: str = ...,
    ) -> "MultipartUploadPartsCollection":
        """
        Get items from the collection, passing keyword arguments along as parameters to the underlying service operation, which are typically used to filter the results.
        """

    def limit(self, count: int) -> "MultipartUploadPartsCollection":
        """
        Return at most this many MultipartUploadParts.
        """

    def page_size(self, count: int) -> "MultipartUploadPartsCollection":
        """
        Fetch at most this many MultipartUploadParts per service request.
        """

    def pages(self) -> Iterator[List["MultipartUploadPart"]]:
        """
        A generator which yields pages of MultipartUploadParts.
        """

    def __iter__(self) -> Iterator["MultipartUploadPart"]:
        """
        A generator which yields MultipartUploadParts.
        """


class BucketAcl(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketAcl)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketacl)
    """

    owner: OwnerResponseTypeDef
    grants: List[GrantTypeDef]
    bucket_name: str
    meta: "S3ResourceMeta"

    def Bucket(self) -> "_Bucket":
        """
        Creates a Bucket resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketAcl.Bucket)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketaclbucket-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketAcl.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketaclget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_acl` to update the attributes of the
        BucketAcl
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketAcl.load)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketaclload-method)
        """

    def put(
        self,
        *,
        ACL: BucketCannedACLType = ...,
        AccessControlPolicy: AccessControlPolicyTypeDef = ...,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        GrantFullControl: str = ...,
        GrantRead: str = ...,
        GrantReadACP: str = ...,
        GrantWrite: str = ...,
        GrantWriteACP: str = ...,
        ExpectedBucketOwner: str = ...,
    ) -> None:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketAcl.put)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketaclput-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_acl` to update the attributes of the
        BucketAcl
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketAcl.reload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketaclreload-method)
        """


_BucketAcl = BucketAcl


class BucketCors(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketCors)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketcors)
    """

    cors_rules: List[CORSRuleExtraOutputTypeDef]
    bucket_name: str
    meta: "S3ResourceMeta"

    def Bucket(self) -> "_Bucket":
        """
        Creates a Bucket resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketCors.Bucket)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketcorsbucket-method)
        """

    def delete(self, *, ExpectedBucketOwner: str = ...) -> None:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketCors.delete)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketcorsdelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketCors.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketcorsget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_cors` to update the attributes of the
        BucketCors
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketCors.load)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketcorsload-method)
        """

    def put(
        self,
        *,
        CORSConfiguration: CORSConfigurationTypeDef,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        ExpectedBucketOwner: str = ...,
    ) -> None:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketCors.put)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketcorsput-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_cors` to update the attributes of the
        BucketCors
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketCors.reload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketcorsreload-method)
        """


_BucketCors = BucketCors


class BucketLifecycle(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketLifecycle)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlifecycle)
    """

    rules: List[RuleExtraOutputTypeDef]
    bucket_name: str
    meta: "S3ResourceMeta"

    def Bucket(self) -> "_Bucket":
        """
        Creates a Bucket resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketLifecycle.Bucket)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlifecyclebucket-method)
        """

    def delete(self, *, ExpectedBucketOwner: str = ...) -> None:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketLifecycle.delete)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlifecycledelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketLifecycle.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlifecycleget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_lifecycle` to update the attributes of the
        BucketLifecycle
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketLifecycle.load)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlifecycleload-method)
        """

    def put(
        self,
        *,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        LifecycleConfiguration: LifecycleConfigurationTypeDef = ...,
        ExpectedBucketOwner: str = ...,
    ) -> None:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketLifecycle.put)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlifecycleput-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_lifecycle` to update the attributes of the
        BucketLifecycle
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketLifecycle.reload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlifecyclereload-method)
        """


_BucketLifecycle = BucketLifecycle


class BucketLifecycleConfiguration(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketLifecycleConfiguration)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlifecycleconfiguration)
    """

    rules: List[LifecycleRuleExtraOutputTypeDef]
    bucket_name: str
    meta: "S3ResourceMeta"

    def Bucket(self) -> "_Bucket":
        """
        Creates a Bucket resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketLifecycleConfiguration.Bucket)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlifecycleconfigurationbucket-method)
        """

    def delete(self, *, ExpectedBucketOwner: str = ...) -> None:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketLifecycleConfiguration.delete)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlifecycleconfigurationdelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketLifecycleConfiguration.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlifecycleconfigurationget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_lifecycle_configuration` to update the
        attributes of the BucketLifecycleConfiguration
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketLifecycleConfiguration.load)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlifecycleconfigurationload-method)
        """

    def put(
        self,
        *,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        LifecycleConfiguration: BucketLifecycleConfigurationTypeDef = ...,
        ExpectedBucketOwner: str = ...,
    ) -> None:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketLifecycleConfiguration.put)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlifecycleconfigurationput-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_lifecycle_configuration` to update the
        attributes of the BucketLifecycleConfiguration
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketLifecycleConfiguration.reload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlifecycleconfigurationreload-method)
        """


_BucketLifecycleConfiguration = BucketLifecycleConfiguration


class BucketLogging(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketLogging)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlogging)
    """

    logging_enabled: LoggingEnabledResponseTypeDef
    bucket_name: str
    meta: "S3ResourceMeta"

    def Bucket(self) -> "_Bucket":
        """
        Creates a Bucket resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketLogging.Bucket)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketloggingbucket-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketLogging.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketloggingget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_logging` to update the attributes of the
        BucketLogging
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketLogging.load)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketloggingload-method)
        """

    def put(
        self,
        *,
        BucketLoggingStatus: BucketLoggingStatusTypeDef,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        ExpectedBucketOwner: str = ...,
    ) -> None:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketLogging.put)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketloggingput-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_logging` to update the attributes of the
        BucketLogging
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketLogging.reload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketloggingreload-method)
        """


_BucketLogging = BucketLogging


class BucketNotification(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketNotification)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketnotification)
    """

    topic_configurations: List[TopicConfigurationExtraOutputTypeDef]
    queue_configurations: List[QueueConfigurationExtraOutputTypeDef]
    lambda_function_configurations: List[LambdaFunctionConfigurationExtraOutputTypeDef]
    event_bridge_configuration: Dict[str, Any]
    bucket_name: str
    meta: "S3ResourceMeta"

    def Bucket(self) -> "_Bucket":
        """
        Creates a Bucket resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketNotification.Bucket)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketnotificationbucket-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketNotification.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketnotificationget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_notification_configuration` to update the
        attributes of the BucketNotification
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketNotification.load)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketnotificationload-method)
        """

    def put(
        self,
        *,
        NotificationConfiguration: NotificationConfigurationTypeDef,
        ExpectedBucketOwner: str = ...,
        SkipDestinationValidation: bool = ...,
    ) -> None:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketNotification.put)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketnotificationput-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_notification_configuration` to update the
        attributes of the BucketNotification
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketNotification.reload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketnotificationreload-method)
        """


_BucketNotification = BucketNotification


class BucketPolicy(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketPolicy)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketpolicy)
    """

    policy: str
    bucket_name: str
    meta: "S3ResourceMeta"

    def Bucket(self) -> "_Bucket":
        """
        Creates a Bucket resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketPolicy.Bucket)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketpolicybucket-method)
        """

    def delete(self, *, ExpectedBucketOwner: str = ...) -> None:
        """
        Deletes the policy of a specified bucket.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketPolicy.delete)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketpolicydelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketPolicy.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketpolicyget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_policy` to update the attributes of the
        BucketPolicy
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketPolicy.load)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketpolicyload-method)
        """

    def put(
        self,
        *,
        Policy: str,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        ConfirmRemoveSelfBucketAccess: bool = ...,
        ExpectedBucketOwner: str = ...,
    ) -> None:
        """
        Applies an Amazon S3 bucket policy to an Amazon S3 bucket.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketPolicy.put)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketpolicyput-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_policy` to update the attributes of the
        BucketPolicy
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketPolicy.reload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketpolicyreload-method)
        """


_BucketPolicy = BucketPolicy


class BucketRequestPayment(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketRequestPayment)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketrequestpayment)
    """

    payer: PayerType
    bucket_name: str
    meta: "S3ResourceMeta"

    def Bucket(self) -> "_Bucket":
        """
        Creates a Bucket resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketRequestPayment.Bucket)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketrequestpaymentbucket-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketRequestPayment.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketrequestpaymentget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_request_payment` to update the attributes
        of the BucketRequestPayment
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketRequestPayment.load)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketrequestpaymentload-method)
        """

    def put(
        self,
        *,
        RequestPaymentConfiguration: RequestPaymentConfigurationTypeDef,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        ExpectedBucketOwner: str = ...,
    ) -> None:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketRequestPayment.put)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketrequestpaymentput-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_request_payment` to update the attributes
        of the BucketRequestPayment
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketRequestPayment.reload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketrequestpaymentreload-method)
        """


_BucketRequestPayment = BucketRequestPayment


class BucketTagging(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketTagging)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#buckettagging)
    """

    tag_set: List[TagTypeDef]
    bucket_name: str
    meta: "S3ResourceMeta"

    def Bucket(self) -> "_Bucket":
        """
        Creates a Bucket resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketTagging.Bucket)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#buckettaggingbucket-method)
        """

    def delete(self, *, ExpectedBucketOwner: str = ...) -> None:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketTagging.delete)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#buckettaggingdelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketTagging.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#buckettaggingget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_tagging` to update the attributes of the
        BucketTagging
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketTagging.load)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#buckettaggingload-method)
        """

    def put(
        self,
        *,
        Tagging: TaggingTypeDef,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        ExpectedBucketOwner: str = ...,
    ) -> None:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketTagging.put)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#buckettaggingput-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_tagging` to update the attributes of the
        BucketTagging
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketTagging.reload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#buckettaggingreload-method)
        """


_BucketTagging = BucketTagging


class BucketVersioning(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketVersioning)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketversioning)
    """

    status: BucketVersioningStatusType
    mfa_delete: MFADeleteStatusType
    bucket_name: str
    meta: "S3ResourceMeta"

    def Bucket(self) -> "_Bucket":
        """
        Creates a Bucket resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketVersioning.Bucket)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketversioningbucket-method)
        """

    def enable(
        self,
        *,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        MFA: str = ...,
        ExpectedBucketOwner: str = ...,
    ) -> None:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketVersioning.enable)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketversioningenable-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketVersioning.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketversioningget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_versioning` to update the attributes of
        the BucketVersioning
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketVersioning.load)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketversioningload-method)
        """

    def put(
        self,
        *,
        VersioningConfiguration: VersioningConfigurationTypeDef,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        MFA: str = ...,
        ExpectedBucketOwner: str = ...,
    ) -> None:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketVersioning.put)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketversioningput-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_versioning` to update the attributes of
        the BucketVersioning
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketVersioning.reload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketversioningreload-method)
        """

    def suspend(
        self,
        *,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        MFA: str = ...,
        ExpectedBucketOwner: str = ...,
    ) -> None:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketVersioning.suspend)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketversioningsuspend-method)
        """


_BucketVersioning = BucketVersioning


class BucketWebsite(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketWebsite)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketwebsite)
    """

    redirect_all_requests_to: RedirectAllRequestsToResponseTypeDef
    index_document: IndexDocumentResponseTypeDef
    error_document: ErrorDocumentResponseTypeDef
    routing_rules: List[RoutingRuleTypeDef]
    bucket_name: str
    meta: "S3ResourceMeta"

    def Bucket(self) -> "_Bucket":
        """
        Creates a Bucket resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketWebsite.Bucket)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketwebsitebucket-method)
        """

    def delete(self, *, ExpectedBucketOwner: str = ...) -> None:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketWebsite.delete)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketwebsitedelete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketWebsite.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketwebsiteget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_website` to update the attributes of the
        BucketWebsite
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketWebsite.load)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketwebsiteload-method)
        """

    def put(
        self,
        *,
        WebsiteConfiguration: WebsiteConfigurationTypeDef,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        ExpectedBucketOwner: str = ...,
    ) -> None:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketWebsite.put)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketwebsiteput-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_bucket_website` to update the attributes of the
        BucketWebsite
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.BucketWebsite.reload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketwebsitereload-method)
        """


_BucketWebsite = BucketWebsite


class MultipartUploadPart(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.MultipartUploadPart)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#multipartuploadpart)
    """

    last_modified: datetime
    e_tag: str
    size: int
    checksum_crc32: str
    checksum_crc32_c: str
    checksum_sha1: str
    checksum_sha256: str
    bucket_name: str
    object_key: str
    multipart_upload_id: str
    part_number: str
    meta: "S3ResourceMeta"

    def MultipartUpload(self) -> "_MultipartUpload":
        """
        Creates a MultipartUpload resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.MultipartUploadPart.MultipartUpload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#multipartuploadpartmultipartupload-method)
        """

    def copy_from(
        self,
        *,
        CopySource: CopySourceOrStrTypeDef,
        CopySourceIfMatch: str = ...,
        CopySourceIfModifiedSince: TimestampTypeDef = ...,
        CopySourceIfNoneMatch: str = ...,
        CopySourceIfUnmodifiedSince: TimestampTypeDef = ...,
        CopySourceRange: str = ...,
        SSECustomerAlgorithm: str = ...,
        SSECustomerKey: str = ...,
        SSECustomerKeyMD5: str = ...,
        CopySourceSSECustomerAlgorithm: str = ...,
        CopySourceSSECustomerKey: str = ...,
        CopySourceSSECustomerKeyMD5: str = ...,
        RequestPayer: Literal["requester"] = ...,
        ExpectedBucketOwner: str = ...,
        ExpectedSourceBucketOwner: str = ...,
    ) -> UploadPartCopyOutputTypeDef:
        """
        Uploads a part by copying data from an existing object as data source.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.MultipartUploadPart.copy_from)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#multipartuploadpartcopy_from-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.MultipartUploadPart.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#multipartuploadpartget_available_subresources-method)
        """

    def upload(
        self,
        *,
        Body: BlobTypeDef = ...,
        ContentLength: int = ...,
        ContentMD5: str = ...,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        ChecksumCRC32: str = ...,
        ChecksumCRC32C: str = ...,
        ChecksumSHA1: str = ...,
        ChecksumSHA256: str = ...,
        SSECustomerAlgorithm: str = ...,
        SSECustomerKey: str = ...,
        SSECustomerKeyMD5: str = ...,
        RequestPayer: Literal["requester"] = ...,
        ExpectedBucketOwner: str = ...,
    ) -> UploadPartOutputTypeDef:
        """
        Uploads a part in a multipart upload.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.MultipartUploadPart.upload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#multipartuploadpartupload-method)
        """


_MultipartUploadPart = MultipartUploadPart


class ObjectAcl(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.ObjectAcl)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectacl)
    """

    owner: OwnerResponseTypeDef
    grants: List[GrantTypeDef]
    request_charged: Literal["requester"]
    bucket_name: str
    object_key: str
    meta: "S3ResourceMeta"

    def Object(self) -> "_Object":
        """
        Creates a Object resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectAcl.Object)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectaclobject-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectAcl.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectaclget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_object_acl` to update the attributes of the
        ObjectAcl
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectAcl.load)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectaclload-method)
        """

    def put(
        self,
        *,
        ACL: ObjectCannedACLType = ...,
        AccessControlPolicy: AccessControlPolicyTypeDef = ...,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        GrantFullControl: str = ...,
        GrantRead: str = ...,
        GrantReadACP: str = ...,
        GrantWrite: str = ...,
        GrantWriteACP: str = ...,
        RequestPayer: Literal["requester"] = ...,
        VersionId: str = ...,
        ExpectedBucketOwner: str = ...,
    ) -> PutObjectAclOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectAcl.put)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectaclput-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`S3.Client.get_object_acl` to update the attributes of the
        ObjectAcl
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectAcl.reload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectaclreload-method)
        """


_ObjectAcl = ObjectAcl


class ObjectVersion(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.ObjectVersion)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectversion)
    """

    e_tag: str
    checksum_algorithm: List[ChecksumAlgorithmType]
    size: int
    storage_class: Literal["STANDARD"]
    key: str
    version_id: str
    is_latest: bool
    last_modified: datetime
    owner: OwnerResponseTypeDef
    restore_status: RestoreStatusResponseTypeDef
    bucket_name: str
    object_key: str
    id: str
    meta: "S3ResourceMeta"

    def Object(self) -> "_Object":
        """
        Creates a Object resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectVersion.Object)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectversionobject-method)
        """

    def delete(
        self,
        *,
        MFA: str = ...,
        RequestPayer: Literal["requester"] = ...,
        BypassGovernanceRetention: bool = ...,
        ExpectedBucketOwner: str = ...,
    ) -> DeleteObjectOutputTypeDef:
        """
        Removes an object from a bucket.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectVersion.delete)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectversiondelete-method)
        """

    def get(
        self,
        *,
        IfMatch: str = ...,
        IfModifiedSince: TimestampTypeDef = ...,
        IfNoneMatch: str = ...,
        IfUnmodifiedSince: TimestampTypeDef = ...,
        Range: str = ...,
        ResponseCacheControl: str = ...,
        ResponseContentDisposition: str = ...,
        ResponseContentEncoding: str = ...,
        ResponseContentLanguage: str = ...,
        ResponseContentType: str = ...,
        ResponseExpires: TimestampTypeDef = ...,
        SSECustomerAlgorithm: str = ...,
        SSECustomerKey: str = ...,
        SSECustomerKeyMD5: str = ...,
        RequestPayer: Literal["requester"] = ...,
        PartNumber: int = ...,
        ExpectedBucketOwner: str = ...,
        ChecksumMode: Literal["ENABLED"] = ...,
    ) -> GetObjectOutputTypeDef:
        """
        Retrieves an object from Amazon S3.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectVersion.get)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectversionget-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectVersion.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectversionget_available_subresources-method)
        """

    def head(
        self,
        *,
        IfMatch: str = ...,
        IfModifiedSince: TimestampTypeDef = ...,
        IfNoneMatch: str = ...,
        IfUnmodifiedSince: TimestampTypeDef = ...,
        Range: str = ...,
        SSECustomerAlgorithm: str = ...,
        SSECustomerKey: str = ...,
        SSECustomerKeyMD5: str = ...,
        RequestPayer: Literal["requester"] = ...,
        PartNumber: int = ...,
        ExpectedBucketOwner: str = ...,
        ChecksumMode: Literal["ENABLED"] = ...,
    ) -> HeadObjectOutputTypeDef:
        """
        The `HEAD` operation retrieves metadata from an object without returning the
        object
        itself.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectVersion.head)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectversionhead-method)
        """


_ObjectVersion = ObjectVersion


class MultipartUpload(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.MultipartUpload)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#multipartupload)
    """

    upload_id: str
    key: str
    initiated: datetime
    storage_class: StorageClassType
    owner: OwnerResponseTypeDef
    initiator: InitiatorResponseTypeDef
    checksum_algorithm: ChecksumAlgorithmType
    bucket_name: str
    object_key: str
    id: str
    parts: MultipartUploadPartsCollection
    meta: "S3ResourceMeta"

    def Object(self) -> "_Object":
        """
        Creates a Object resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.MultipartUpload.Object)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#multipartuploadobject-method)
        """

    def Part(self, part_number: str) -> "_MultipartUploadPart":
        """
        Creates a MultipartUploadPart resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.MultipartUpload.Part)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#multipartuploadpart-method)
        """

    def abort(
        self, *, RequestPayer: Literal["requester"] = ..., ExpectedBucketOwner: str = ...
    ) -> AbortMultipartUploadOutputTypeDef:
        """
        This operation aborts a multipart upload.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.MultipartUpload.abort)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#multipartuploadabort-method)
        """

    def complete(
        self,
        *,
        MultipartUpload: CompletedMultipartUploadTypeDef = ...,
        ChecksumCRC32: str = ...,
        ChecksumCRC32C: str = ...,
        ChecksumSHA1: str = ...,
        ChecksumSHA256: str = ...,
        RequestPayer: Literal["requester"] = ...,
        ExpectedBucketOwner: str = ...,
        SSECustomerAlgorithm: str = ...,
        SSECustomerKey: str = ...,
        SSECustomerKeyMD5: str = ...,
    ) -> "_Object":
        """
        Completes a multipart upload by assembling previously uploaded parts.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.MultipartUpload.complete)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#multipartuploadcomplete-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.MultipartUpload.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#multipartuploadget_available_subresources-method)
        """


_MultipartUpload = MultipartUpload


class Object(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.Object)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#object)
    """

    delete_marker: bool
    accept_ranges: str
    expiration: str
    restore: str
    archive_status: ArchiveStatusType
    last_modified: datetime
    content_length: int
    checksum_crc32: str
    checksum_crc32_c: str
    checksum_sha1: str
    checksum_sha256: str
    e_tag: str
    missing_meta: int
    version_id: str
    cache_control: str
    content_disposition: str
    content_encoding: str
    content_language: str
    content_type: str
    expires: datetime
    website_redirect_location: str
    server_side_encryption: ServerSideEncryptionType
    metadata: Dict[str, str]
    sse_customer_algorithm: str
    sse_customer_key_md5: str
    ssekms_key_id: str
    bucket_key_enabled: bool
    storage_class: StorageClassType
    request_charged: Literal["requester"]
    replication_status: ReplicationStatusType
    parts_count: int
    object_lock_mode: ObjectLockModeType
    object_lock_retain_until_date: datetime
    object_lock_legal_hold_status: ObjectLockLegalHoldStatusType
    bucket_name: str
    key: str
    meta: "S3ResourceMeta"

    def Acl(self) -> "_ObjectAcl":
        """
        Creates a ObjectAcl resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.Acl)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectacl-method)
        """

    def Bucket(self) -> "_Bucket":
        """
        Creates a Bucket resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.Bucket)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectbucket-method)
        """

    def MultipartUpload(self, id: str) -> "_MultipartUpload":
        """
        Creates a MultipartUpload resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.MultipartUpload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectmultipartupload-method)
        """

    def Version(self, id: str) -> "_ObjectVersion":
        """
        Creates a ObjectVersion resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.Version)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectversion-method)
        """

    def copy(
        self,
        CopySource: CopySourceTypeDef,
        ExtraArgs: Optional[Dict[str, Any]] = ...,
        Callback: Optional[Callable[..., Any]] = ...,
        SourceClient: Optional[BaseClient] = ...,
        Config: Optional[TransferConfig] = ...,
    ) -> None:
        """
        Copy an object from one S3 location to this object.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.copy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectcopy-method)
        """

    def copy_from(
        self,
        *,
        CopySource: str,
        ACL: ObjectCannedACLType = ...,
        CacheControl: str = ...,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        ContentDisposition: str = ...,
        ContentEncoding: str = ...,
        ContentLanguage: str = ...,
        ContentType: str = ...,
        CopySourceIfMatch: str = ...,
        CopySourceIfModifiedSince: TimestampTypeDef = ...,
        CopySourceIfNoneMatch: str = ...,
        CopySourceIfUnmodifiedSince: TimestampTypeDef = ...,
        Expires: TimestampTypeDef = ...,
        GrantFullControl: str = ...,
        GrantRead: str = ...,
        GrantReadACP: str = ...,
        GrantWriteACP: str = ...,
        Metadata: Mapping[str, str] = ...,
        MetadataDirective: MetadataDirectiveType = ...,
        TaggingDirective: TaggingDirectiveType = ...,
        ServerSideEncryption: ServerSideEncryptionType = ...,
        StorageClass: StorageClassType = ...,
        WebsiteRedirectLocation: str = ...,
        SSECustomerAlgorithm: str = ...,
        SSECustomerKey: str = ...,
        SSECustomerKeyMD5: str = ...,
        SSEKMSKeyId: str = ...,
        SSEKMSEncryptionContext: str = ...,
        BucketKeyEnabled: bool = ...,
        CopySourceSSECustomerAlgorithm: str = ...,
        CopySourceSSECustomerKey: str = ...,
        CopySourceSSECustomerKeyMD5: str = ...,
        RequestPayer: Literal["requester"] = ...,
        Tagging: str = ...,
        ObjectLockMode: ObjectLockModeType = ...,
        ObjectLockRetainUntilDate: TimestampTypeDef = ...,
        ObjectLockLegalHoldStatus: ObjectLockLegalHoldStatusType = ...,
        ExpectedBucketOwner: str = ...,
        ExpectedSourceBucketOwner: str = ...,
    ) -> CopyObjectOutputTypeDef:
        """
        Creates a copy of an object that is already stored in Amazon S3.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.copy_from)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectcopy_from-method)
        """

    def delete(
        self,
        *,
        MFA: str = ...,
        VersionId: str = ...,
        RequestPayer: Literal["requester"] = ...,
        BypassGovernanceRetention: bool = ...,
        ExpectedBucketOwner: str = ...,
    ) -> DeleteObjectOutputTypeDef:
        """
        Removes an object from a bucket.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.delete)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectdelete-method)
        """

    def download_file(
        self,
        Filename: str,
        ExtraArgs: Optional[Dict[str, Any]] = ...,
        Callback: Optional[Callable[..., Any]] = ...,
        Config: Optional[TransferConfig] = ...,
    ) -> None:
        """
        Download an S3 object to a file.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.download_file)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectdownload_file-method)
        """

    def download_fileobj(
        self,
        Fileobj: FileobjTypeDef,
        ExtraArgs: Optional[Dict[str, Any]] = ...,
        Callback: Optional[Callable[..., Any]] = ...,
        Config: Optional[TransferConfig] = ...,
    ) -> None:
        """
        Download this object from S3 to a file-like object.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.download_fileobj)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectdownload_fileobj-method)
        """

    def get(
        self,
        *,
        IfMatch: str = ...,
        IfModifiedSince: TimestampTypeDef = ...,
        IfNoneMatch: str = ...,
        IfUnmodifiedSince: TimestampTypeDef = ...,
        Range: str = ...,
        ResponseCacheControl: str = ...,
        ResponseContentDisposition: str = ...,
        ResponseContentEncoding: str = ...,
        ResponseContentLanguage: str = ...,
        ResponseContentType: str = ...,
        ResponseExpires: TimestampTypeDef = ...,
        VersionId: str = ...,
        SSECustomerAlgorithm: str = ...,
        SSECustomerKey: str = ...,
        SSECustomerKeyMD5: str = ...,
        RequestPayer: Literal["requester"] = ...,
        PartNumber: int = ...,
        ExpectedBucketOwner: str = ...,
        ChecksumMode: Literal["ENABLED"] = ...,
    ) -> GetObjectOutputTypeDef:
        """
        Retrieves an object from Amazon S3.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.get)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectget-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectget_available_subresources-method)
        """

    def initiate_multipart_upload(
        self,
        *,
        ACL: ObjectCannedACLType = ...,
        CacheControl: str = ...,
        ContentDisposition: str = ...,
        ContentEncoding: str = ...,
        ContentLanguage: str = ...,
        ContentType: str = ...,
        Expires: TimestampTypeDef = ...,
        GrantFullControl: str = ...,
        GrantRead: str = ...,
        GrantReadACP: str = ...,
        GrantWriteACP: str = ...,
        Metadata: Mapping[str, str] = ...,
        ServerSideEncryption: ServerSideEncryptionType = ...,
        StorageClass: StorageClassType = ...,
        WebsiteRedirectLocation: str = ...,
        SSECustomerAlgorithm: str = ...,
        SSECustomerKey: str = ...,
        SSECustomerKeyMD5: str = ...,
        SSEKMSKeyId: str = ...,
        SSEKMSEncryptionContext: str = ...,
        BucketKeyEnabled: bool = ...,
        RequestPayer: Literal["requester"] = ...,
        Tagging: str = ...,
        ObjectLockMode: ObjectLockModeType = ...,
        ObjectLockRetainUntilDate: TimestampTypeDef = ...,
        ObjectLockLegalHoldStatus: ObjectLockLegalHoldStatusType = ...,
        ExpectedBucketOwner: str = ...,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
    ) -> "_MultipartUpload":
        """
        This action initiates a multipart upload and returns an upload ID.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.initiate_multipart_upload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectinitiate_multipart_upload-method)
        """

    def load(self) -> None:
        """
        Calls :py:meth:`S3.Client.head_object` to update the attributes of the Object
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.load)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectload-method)
        """

    def put(
        self,
        *,
        ACL: ObjectCannedACLType = ...,
        Body: BlobTypeDef = ...,
        CacheControl: str = ...,
        ContentDisposition: str = ...,
        ContentEncoding: str = ...,
        ContentLanguage: str = ...,
        ContentLength: int = ...,
        ContentMD5: str = ...,
        ContentType: str = ...,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        ChecksumCRC32: str = ...,
        ChecksumCRC32C: str = ...,
        ChecksumSHA1: str = ...,
        ChecksumSHA256: str = ...,
        Expires: TimestampTypeDef = ...,
        GrantFullControl: str = ...,
        GrantRead: str = ...,
        GrantReadACP: str = ...,
        GrantWriteACP: str = ...,
        Metadata: Mapping[str, str] = ...,
        ServerSideEncryption: ServerSideEncryptionType = ...,
        StorageClass: StorageClassType = ...,
        WebsiteRedirectLocation: str = ...,
        SSECustomerAlgorithm: str = ...,
        SSECustomerKey: str = ...,
        SSECustomerKeyMD5: str = ...,
        SSEKMSKeyId: str = ...,
        SSEKMSEncryptionContext: str = ...,
        BucketKeyEnabled: bool = ...,
        RequestPayer: Literal["requester"] = ...,
        Tagging: str = ...,
        ObjectLockMode: ObjectLockModeType = ...,
        ObjectLockRetainUntilDate: TimestampTypeDef = ...,
        ObjectLockLegalHoldStatus: ObjectLockLegalHoldStatusType = ...,
        ExpectedBucketOwner: str = ...,
    ) -> PutObjectOutputTypeDef:
        """
        Adds an object to a bucket.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.put)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectput-method)
        """

    def reload(self) -> None:
        """
        Calls :py:meth:`S3.Client.head_object` to update the attributes of the Object
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.reload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectreload-method)
        """

    def restore_object(
        self,
        *,
        VersionId: str = ...,
        RestoreRequest: RestoreRequestTypeDef = ...,
        RequestPayer: Literal["requester"] = ...,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        ExpectedBucketOwner: str = ...,
    ) -> RestoreObjectOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.restore_object)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectrestore_object-method)
        """

    def upload_file(
        self,
        Filename: str,
        ExtraArgs: Optional[Dict[str, Any]] = ...,
        Callback: Optional[Callable[..., Any]] = ...,
        Config: Optional[TransferConfig] = ...,
    ) -> None:
        """
        Upload a file to an S3 object.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.upload_file)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectupload_file-method)
        """

    def upload_fileobj(
        self,
        Fileobj: FileobjTypeDef,
        ExtraArgs: Optional[Dict[str, Any]] = ...,
        Callback: Optional[Callable[..., Any]] = ...,
        Config: Optional[TransferConfig] = ...,
    ) -> None:
        """
        Upload a file-like object to this object.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.upload_fileobj)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectupload_fileobj-method)
        """

    def wait_until_exists(self) -> None:
        """
        Waits until this Object is exists.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.wait_until_exists)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectwait_until_exists-method)
        """

    def wait_until_not_exists(self) -> None:
        """
        Waits until this Object is not exists.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.wait_until_not_exists)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectwait_until_not_exists-method)
        """


_Object = Object


class ObjectSummary(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.ObjectSummary)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectsummary)
    """

    last_modified: datetime
    e_tag: str
    checksum_algorithm: List[ChecksumAlgorithmType]
    size: int
    storage_class: ObjectStorageClassType
    owner: OwnerResponseTypeDef
    restore_status: RestoreStatusResponseTypeDef
    bucket_name: str
    key: str
    meta: "S3ResourceMeta"

    def Acl(self) -> "_ObjectAcl":
        """
        Creates a ObjectAcl resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectSummary.Acl)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectsummaryacl-method)
        """

    def Bucket(self) -> "_Bucket":
        """
        Creates a Bucket resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectSummary.Bucket)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectsummarybucket-method)
        """

    def MultipartUpload(self, id: str) -> "_MultipartUpload":
        """
        Creates a MultipartUpload resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectSummary.MultipartUpload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectsummarymultipartupload-method)
        """

    def Object(self) -> "_Object":
        """
        Creates a Object resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectSummary.Object)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectsummaryobject-method)
        """

    def Version(self, id: str) -> "_ObjectVersion":
        """
        Creates a ObjectVersion resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectSummary.Version)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectsummaryversion-method)
        """

    def copy_from(
        self,
        *,
        CopySource: str,
        ACL: ObjectCannedACLType = ...,
        CacheControl: str = ...,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        ContentDisposition: str = ...,
        ContentEncoding: str = ...,
        ContentLanguage: str = ...,
        ContentType: str = ...,
        CopySourceIfMatch: str = ...,
        CopySourceIfModifiedSince: TimestampTypeDef = ...,
        CopySourceIfNoneMatch: str = ...,
        CopySourceIfUnmodifiedSince: TimestampTypeDef = ...,
        Expires: TimestampTypeDef = ...,
        GrantFullControl: str = ...,
        GrantRead: str = ...,
        GrantReadACP: str = ...,
        GrantWriteACP: str = ...,
        Metadata: Mapping[str, str] = ...,
        MetadataDirective: MetadataDirectiveType = ...,
        TaggingDirective: TaggingDirectiveType = ...,
        ServerSideEncryption: ServerSideEncryptionType = ...,
        StorageClass: StorageClassType = ...,
        WebsiteRedirectLocation: str = ...,
        SSECustomerAlgorithm: str = ...,
        SSECustomerKey: str = ...,
        SSECustomerKeyMD5: str = ...,
        SSEKMSKeyId: str = ...,
        SSEKMSEncryptionContext: str = ...,
        BucketKeyEnabled: bool = ...,
        CopySourceSSECustomerAlgorithm: str = ...,
        CopySourceSSECustomerKey: str = ...,
        CopySourceSSECustomerKeyMD5: str = ...,
        RequestPayer: Literal["requester"] = ...,
        Tagging: str = ...,
        ObjectLockMode: ObjectLockModeType = ...,
        ObjectLockRetainUntilDate: TimestampTypeDef = ...,
        ObjectLockLegalHoldStatus: ObjectLockLegalHoldStatusType = ...,
        ExpectedBucketOwner: str = ...,
        ExpectedSourceBucketOwner: str = ...,
    ) -> CopyObjectOutputTypeDef:
        """
        Creates a copy of an object that is already stored in Amazon S3.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectSummary.copy_from)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectsummarycopy_from-method)
        """

    def delete(
        self,
        *,
        MFA: str = ...,
        VersionId: str = ...,
        RequestPayer: Literal["requester"] = ...,
        BypassGovernanceRetention: bool = ...,
        ExpectedBucketOwner: str = ...,
    ) -> DeleteObjectOutputTypeDef:
        """
        Removes an object from a bucket.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectSummary.delete)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectsummarydelete-method)
        """

    def get(
        self,
        *,
        IfMatch: str = ...,
        IfModifiedSince: TimestampTypeDef = ...,
        IfNoneMatch: str = ...,
        IfUnmodifiedSince: TimestampTypeDef = ...,
        Range: str = ...,
        ResponseCacheControl: str = ...,
        ResponseContentDisposition: str = ...,
        ResponseContentEncoding: str = ...,
        ResponseContentLanguage: str = ...,
        ResponseContentType: str = ...,
        ResponseExpires: TimestampTypeDef = ...,
        VersionId: str = ...,
        SSECustomerAlgorithm: str = ...,
        SSECustomerKey: str = ...,
        SSECustomerKeyMD5: str = ...,
        RequestPayer: Literal["requester"] = ...,
        PartNumber: int = ...,
        ExpectedBucketOwner: str = ...,
        ChecksumMode: Literal["ENABLED"] = ...,
    ) -> GetObjectOutputTypeDef:
        """
        Retrieves an object from Amazon S3.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectSummary.get)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectsummaryget-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectSummary.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectsummaryget_available_subresources-method)
        """

    def initiate_multipart_upload(
        self,
        *,
        ACL: ObjectCannedACLType = ...,
        CacheControl: str = ...,
        ContentDisposition: str = ...,
        ContentEncoding: str = ...,
        ContentLanguage: str = ...,
        ContentType: str = ...,
        Expires: TimestampTypeDef = ...,
        GrantFullControl: str = ...,
        GrantRead: str = ...,
        GrantReadACP: str = ...,
        GrantWriteACP: str = ...,
        Metadata: Mapping[str, str] = ...,
        ServerSideEncryption: ServerSideEncryptionType = ...,
        StorageClass: StorageClassType = ...,
        WebsiteRedirectLocation: str = ...,
        SSECustomerAlgorithm: str = ...,
        SSECustomerKey: str = ...,
        SSECustomerKeyMD5: str = ...,
        SSEKMSKeyId: str = ...,
        SSEKMSEncryptionContext: str = ...,
        BucketKeyEnabled: bool = ...,
        RequestPayer: Literal["requester"] = ...,
        Tagging: str = ...,
        ObjectLockMode: ObjectLockModeType = ...,
        ObjectLockRetainUntilDate: TimestampTypeDef = ...,
        ObjectLockLegalHoldStatus: ObjectLockLegalHoldStatusType = ...,
        ExpectedBucketOwner: str = ...,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
    ) -> "_MultipartUpload":
        """
        This action initiates a multipart upload and returns an upload ID.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectSummary.initiate_multipart_upload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectsummaryinitiate_multipart_upload-method)
        """

    def load(self) -> None:
        """
        Calls s3.Client.head_object to update the attributes of the ObjectSummary
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectSummary.load)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectsummaryload-method)
        """

    def put(
        self,
        *,
        ACL: ObjectCannedACLType = ...,
        Body: BlobTypeDef = ...,
        CacheControl: str = ...,
        ContentDisposition: str = ...,
        ContentEncoding: str = ...,
        ContentLanguage: str = ...,
        ContentLength: int = ...,
        ContentMD5: str = ...,
        ContentType: str = ...,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        ChecksumCRC32: str = ...,
        ChecksumCRC32C: str = ...,
        ChecksumSHA1: str = ...,
        ChecksumSHA256: str = ...,
        Expires: TimestampTypeDef = ...,
        GrantFullControl: str = ...,
        GrantRead: str = ...,
        GrantReadACP: str = ...,
        GrantWriteACP: str = ...,
        Metadata: Mapping[str, str] = ...,
        ServerSideEncryption: ServerSideEncryptionType = ...,
        StorageClass: StorageClassType = ...,
        WebsiteRedirectLocation: str = ...,
        SSECustomerAlgorithm: str = ...,
        SSECustomerKey: str = ...,
        SSECustomerKeyMD5: str = ...,
        SSEKMSKeyId: str = ...,
        SSEKMSEncryptionContext: str = ...,
        BucketKeyEnabled: bool = ...,
        RequestPayer: Literal["requester"] = ...,
        Tagging: str = ...,
        ObjectLockMode: ObjectLockModeType = ...,
        ObjectLockRetainUntilDate: TimestampTypeDef = ...,
        ObjectLockLegalHoldStatus: ObjectLockLegalHoldStatusType = ...,
        ExpectedBucketOwner: str = ...,
    ) -> PutObjectOutputTypeDef:
        """
        Adds an object to a bucket.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectSummary.put)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectsummaryput-method)
        """

    def restore_object(
        self,
        *,
        VersionId: str = ...,
        RestoreRequest: RestoreRequestTypeDef = ...,
        RequestPayer: Literal["requester"] = ...,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        ExpectedBucketOwner: str = ...,
    ) -> RestoreObjectOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectSummary.restore_object)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectsummaryrestore_object-method)
        """

    def wait_until_exists(self) -> None:
        """
        Waits until this ObjectSummary is exists.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectSummary.wait_until_exists)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectsummarywait_until_exists-method)
        """

    def wait_until_not_exists(self) -> None:
        """
        Waits until this ObjectSummary is not exists.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ObjectSummary.wait_until_not_exists)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#objectsummarywait_until_not_exists-method)
        """


_ObjectSummary = ObjectSummary


class Bucket(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.Bucket)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucket)
    """

    creation_date: datetime
    name: str
    multipart_uploads: BucketMultipartUploadsCollection
    object_versions: BucketObjectVersionsCollection
    objects: BucketObjectsCollection
    meta: "S3ResourceMeta"

    def Acl(self) -> "_BucketAcl":
        """
        Creates a BucketAcl resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.Acl)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketacl-method)
        """

    def Cors(self) -> "_BucketCors":
        """
        Creates a BucketCors resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.Cors)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketcors-method)
        """

    def Lifecycle(self) -> "_BucketLifecycle":
        """
        Creates a BucketLifecycle resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.Lifecycle)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlifecycle-method)
        """

    def LifecycleConfiguration(self) -> "_BucketLifecycleConfiguration":
        """
        Creates a BucketLifecycleConfiguration resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.LifecycleConfiguration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlifecycleconfiguration-method)
        """

    def Logging(self) -> "_BucketLogging":
        """
        Creates a BucketLogging resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.Logging)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketlogging-method)
        """

    def Notification(self) -> "_BucketNotification":
        """
        Creates a BucketNotification resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.Notification)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketnotification-method)
        """

    def Object(self, key: str) -> "_Object":
        """
        Creates a Object resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.Object)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketobject-method)
        """

    def Policy(self) -> "_BucketPolicy":
        """
        Creates a BucketPolicy resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.Policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketpolicy-method)
        """

    def RequestPayment(self) -> "_BucketRequestPayment":
        """
        Creates a BucketRequestPayment resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.RequestPayment)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketrequestpayment-method)
        """

    def Tagging(self) -> "_BucketTagging":
        """
        Creates a BucketTagging resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.Tagging)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#buckettagging-method)
        """

    def Versioning(self) -> "_BucketVersioning":
        """
        Creates a BucketVersioning resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.Versioning)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketversioning-method)
        """

    def Website(self) -> "_BucketWebsite":
        """
        Creates a BucketWebsite resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.Website)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketwebsite-method)
        """

    def copy(
        self,
        CopySource: CopySourceTypeDef,
        Key: str,
        ExtraArgs: Optional[Dict[str, Any]] = ...,
        Callback: Optional[Callable[..., Any]] = ...,
        SourceClient: Optional[BaseClient] = ...,
        Config: Optional[TransferConfig] = ...,
    ) -> None:
        """
        Copy an object from one S3 location to an object in this bucket.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.copy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketcopy-method)
        """

    def create(
        self,
        *,
        ACL: BucketCannedACLType = ...,
        CreateBucketConfiguration: CreateBucketConfigurationTypeDef = ...,
        GrantFullControl: str = ...,
        GrantRead: str = ...,
        GrantReadACP: str = ...,
        GrantWrite: str = ...,
        GrantWriteACP: str = ...,
        ObjectLockEnabledForBucket: bool = ...,
        ObjectOwnership: ObjectOwnershipType = ...,
    ) -> CreateBucketOutputTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.create)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketcreate-method)
        """

    def delete(self, *, ExpectedBucketOwner: str = ...) -> None:
        """
        Deletes the S3 bucket.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.delete)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketdelete-method)
        """

    def delete_objects(
        self,
        *,
        Delete: DeleteTypeDef,
        MFA: str = ...,
        RequestPayer: Literal["requester"] = ...,
        BypassGovernanceRetention: bool = ...,
        ExpectedBucketOwner: str = ...,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
    ) -> DeleteObjectsOutputTypeDef:
        """
        This operation enables you to delete multiple objects from a bucket using a
        single HTTP
        request.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.delete_objects)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketdelete_objects-method)
        """

    def download_file(
        self,
        Key: str,
        Filename: str,
        ExtraArgs: Optional[Dict[str, Any]] = ...,
        Callback: Optional[Callable[..., Any]] = ...,
        Config: Optional[TransferConfig] = ...,
    ) -> None:
        """
        Download an S3 object to a file.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.download_file)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketdownload_file-method)
        """

    def download_fileobj(
        self,
        Key: str,
        Fileobj: FileobjTypeDef,
        ExtraArgs: Optional[Dict[str, Any]] = ...,
        Callback: Optional[Callable[..., Any]] = ...,
        Config: Optional[TransferConfig] = ...,
    ) -> None:
        """
        Download an object from this bucket to a file-like-object.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.download_fileobj)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketdownload_fileobj-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketget_available_subresources-method)
        """

    def load(self) -> None:
        """
        Calls s3.Client.list_buckets() to update the attributes of the Bucket resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.load)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketload-method)
        """

    def put_object(
        self,
        *,
        Key: str,
        ACL: ObjectCannedACLType = ...,
        Body: BlobTypeDef = ...,
        CacheControl: str = ...,
        ContentDisposition: str = ...,
        ContentEncoding: str = ...,
        ContentLanguage: str = ...,
        ContentLength: int = ...,
        ContentMD5: str = ...,
        ContentType: str = ...,
        ChecksumAlgorithm: ChecksumAlgorithmType = ...,
        ChecksumCRC32: str = ...,
        ChecksumCRC32C: str = ...,
        ChecksumSHA1: str = ...,
        ChecksumSHA256: str = ...,
        Expires: TimestampTypeDef = ...,
        GrantFullControl: str = ...,
        GrantRead: str = ...,
        GrantReadACP: str = ...,
        GrantWriteACP: str = ...,
        Metadata: Mapping[str, str] = ...,
        ServerSideEncryption: ServerSideEncryptionType = ...,
        StorageClass: StorageClassType = ...,
        WebsiteRedirectLocation: str = ...,
        SSECustomerAlgorithm: str = ...,
        SSECustomerKey: str = ...,
        SSECustomerKeyMD5: str = ...,
        SSEKMSKeyId: str = ...,
        SSEKMSEncryptionContext: str = ...,
        BucketKeyEnabled: bool = ...,
        RequestPayer: Literal["requester"] = ...,
        Tagging: str = ...,
        ObjectLockMode: ObjectLockModeType = ...,
        ObjectLockRetainUntilDate: TimestampTypeDef = ...,
        ObjectLockLegalHoldStatus: ObjectLockLegalHoldStatusType = ...,
        ExpectedBucketOwner: str = ...,
    ) -> "_Object":
        """
        Adds an object to a bucket.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.put_object)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketput_object-method)
        """

    def upload_file(
        self,
        Filename: str,
        Key: str,
        ExtraArgs: Optional[Dict[str, Any]] = ...,
        Callback: Optional[Callable[..., Any]] = ...,
        Config: Optional[TransferConfig] = ...,
    ) -> None:
        """
        Upload a file to an S3 object.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.upload_file)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketupload_file-method)
        """

    def upload_fileobj(
        self,
        Fileobj: FileobjTypeDef,
        Key: str,
        ExtraArgs: Optional[Dict[str, Any]] = ...,
        Callback: Optional[Callable[..., Any]] = ...,
        Config: Optional[TransferConfig] = ...,
    ) -> None:
        """
        Upload a file-like object to this bucket.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.upload_fileobj)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketupload_fileobj-method)
        """

    def wait_until_exists(self) -> None:
        """
        Waits until this Bucket is exists.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.wait_until_exists)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketwait_until_exists-method)
        """

    def wait_until_not_exists(self) -> None:
        """
        Waits until this Bucket is not exists.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.wait_until_not_exists)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#bucketwait_until_not_exists-method)
        """


_Bucket = Bucket


class S3ResourceMeta(ResourceMeta):
    client: S3Client


class S3ServiceResource(ServiceResource):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/)
    """

    meta: "S3ResourceMeta"
    buckets: ServiceResourceBucketsCollection

    def Bucket(self, name: str) -> "_Bucket":
        """
        Creates a Bucket resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.Bucket)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourcebucket-method)
        """

    def BucketAcl(self, bucket_name: str) -> "_BucketAcl":
        """
        Creates a BucketAcl resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketAcl)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourcebucketacl-method)
        """

    def BucketCors(self, bucket_name: str) -> "_BucketCors":
        """
        Creates a BucketCors resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketCors)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourcebucketcors-method)
        """

    def BucketLifecycle(self, bucket_name: str) -> "_BucketLifecycle":
        """
        Creates a BucketLifecycle resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketLifecycle)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourcebucketlifecycle-method)
        """

    def BucketLifecycleConfiguration(self, bucket_name: str) -> "_BucketLifecycleConfiguration":
        """
        Creates a BucketLifecycleConfiguration resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketLifecycleConfiguration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourcebucketlifecycleconfiguration-method)
        """

    def BucketLogging(self, bucket_name: str) -> "_BucketLogging":
        """
        Creates a BucketLogging resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketLogging)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourcebucketlogging-method)
        """

    def BucketNotification(self, bucket_name: str) -> "_BucketNotification":
        """
        Creates a BucketNotification resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketNotification)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourcebucketnotification-method)
        """

    def BucketPolicy(self, bucket_name: str) -> "_BucketPolicy":
        """
        Creates a BucketPolicy resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketPolicy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourcebucketpolicy-method)
        """

    def BucketRequestPayment(self, bucket_name: str) -> "_BucketRequestPayment":
        """
        Creates a BucketRequestPayment resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketRequestPayment)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourcebucketrequestpayment-method)
        """

    def BucketTagging(self, bucket_name: str) -> "_BucketTagging":
        """
        Creates a BucketTagging resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketTagging)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourcebuckettagging-method)
        """

    def BucketVersioning(self, bucket_name: str) -> "_BucketVersioning":
        """
        Creates a BucketVersioning resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketVersioning)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourcebucketversioning-method)
        """

    def BucketWebsite(self, bucket_name: str) -> "_BucketWebsite":
        """
        Creates a BucketWebsite resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.BucketWebsite)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourcebucketwebsite-method)
        """

    def MultipartUpload(self, bucket_name: str, object_key: str, id: str) -> "_MultipartUpload":
        """
        Creates a MultipartUpload resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.MultipartUpload)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourcemultipartupload-method)
        """

    def MultipartUploadPart(
        self, bucket_name: str, object_key: str, multipart_upload_id: str, part_number: str
    ) -> "_MultipartUploadPart":
        """
        Creates a MultipartUploadPart resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.MultipartUploadPart)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourcemultipartuploadpart-method)
        """

    def Object(self, bucket_name: str, key: str) -> "_Object":
        """
        Creates a Object resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.Object)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourceobject-method)
        """

    def ObjectAcl(self, bucket_name: str, object_key: str) -> "_ObjectAcl":
        """
        Creates a ObjectAcl resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.ObjectAcl)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourceobjectacl-method)
        """

    def ObjectSummary(self, bucket_name: str, key: str) -> "_ObjectSummary":
        """
        Creates a ObjectSummary resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.ObjectSummary)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourceobjectsummary-method)
        """

    def ObjectVersion(self, bucket_name: str, object_key: str, id: str) -> "_ObjectVersion":
        """
        Creates a ObjectVersion resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.ObjectVersion)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourceobjectversion-method)
        """

    def create_bucket(
        self,
        *,
        Bucket: str,
        ACL: BucketCannedACLType = ...,
        CreateBucketConfiguration: CreateBucketConfigurationTypeDef = ...,
        GrantFullControl: str = ...,
        GrantRead: str = ...,
        GrantReadACP: str = ...,
        GrantWrite: str = ...,
        GrantWriteACP: str = ...,
        ObjectLockEnabledForBucket: bool = ...,
        ObjectOwnership: ObjectOwnershipType = ...,
    ) -> "_Bucket":
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.create_bucket)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourcecreate_bucket-method)
        """

    def get_available_subresources(self) -> Sequence[str]:
        """
        Returns a list of all the available sub-resources for this Resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.ServiceResource.get_available_subresources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_s3/service_resource/#s3serviceresourceget_available_subresources-method)
        """
