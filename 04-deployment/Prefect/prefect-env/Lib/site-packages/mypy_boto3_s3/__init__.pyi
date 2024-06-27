"""
Main interface for s3 service.

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_s3 import (
        BucketExistsWaiter,
        BucketNotExistsWaiter,
        Client,
        ListDirectoryBucketsPaginator,
        ListMultipartUploadsPaginator,
        ListObjectVersionsPaginator,
        ListObjectsPaginator,
        ListObjectsV2Paginator,
        ListPartsPaginator,
        ObjectExistsWaiter,
        ObjectNotExistsWaiter,
        S3Client,
        S3ServiceResource,
        ServiceResource,
    )

    session = Session()
    client: S3Client = session.client("s3")

    resource: S3ServiceResource = session.resource("s3")

    bucket_exists_waiter: BucketExistsWaiter = client.get_waiter("bucket_exists")
    bucket_not_exists_waiter: BucketNotExistsWaiter = client.get_waiter("bucket_not_exists")
    object_exists_waiter: ObjectExistsWaiter = client.get_waiter("object_exists")
    object_not_exists_waiter: ObjectNotExistsWaiter = client.get_waiter("object_not_exists")

    list_directory_buckets_paginator: ListDirectoryBucketsPaginator = client.get_paginator("list_directory_buckets")
    list_multipart_uploads_paginator: ListMultipartUploadsPaginator = client.get_paginator("list_multipart_uploads")
    list_object_versions_paginator: ListObjectVersionsPaginator = client.get_paginator("list_object_versions")
    list_objects_paginator: ListObjectsPaginator = client.get_paginator("list_objects")
    list_objects_v2_paginator: ListObjectsV2Paginator = client.get_paginator("list_objects_v2")
    list_parts_paginator: ListPartsPaginator = client.get_paginator("list_parts")
    ```
"""

from .client import S3Client
from .paginator import (
    ListDirectoryBucketsPaginator,
    ListMultipartUploadsPaginator,
    ListObjectsPaginator,
    ListObjectsV2Paginator,
    ListObjectVersionsPaginator,
    ListPartsPaginator,
)
from .service_resource import S3ServiceResource
from .waiter import (
    BucketExistsWaiter,
    BucketNotExistsWaiter,
    ObjectExistsWaiter,
    ObjectNotExistsWaiter,
)

Client = S3Client

ServiceResource = S3ServiceResource

__all__ = (
    "BucketExistsWaiter",
    "BucketNotExistsWaiter",
    "Client",
    "ListDirectoryBucketsPaginator",
    "ListMultipartUploadsPaginator",
    "ListObjectVersionsPaginator",
    "ListObjectsPaginator",
    "ListObjectsV2Paginator",
    "ListPartsPaginator",
    "ObjectExistsWaiter",
    "ObjectNotExistsWaiter",
    "S3Client",
    "S3ServiceResource",
    "ServiceResource",
)
