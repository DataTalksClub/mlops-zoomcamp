from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Union

if TYPE_CHECKING:
    from litestar.openapi.spec.reference import Reference
    from litestar.openapi.spec.response import OpenAPIResponse

Responses = Dict[str, Union["OpenAPIResponse", "Reference"]]
"""A container for the expected responses of an operation. The container maps a
HTTP response code to the expected response.

The documentation is not necessarily expected to cover all possible HTTP response codes because they may not be known in
advance. However, documentation is expected to cover a successful operation response and any known errors.

The ``default`` MAY be used as a default response object for all HTTP codes hat are not covered individually by the
specification.

The ``Responses Object`` MUST contain at least one response code, and it SHOULD be the response for a successful
operation call.

Fixed Fields

default: ``Optional[Union[Response, Reference]]``

The documentation of responses other than the ones declared for specific HTTP response codes. Use this field to cover
undeclared responses. A `Reference Object <https://spec.openapis.org/oas/v3.1.0#referenceObject>`_ can link to a
response that the `OpenAPI Object's components/responses <https://spec.openapis.org/oas/v3.1.0#componentsResponses>`_
section defines.

Patterned Fields
{httpStatusCode}: ``Optional[Union[Response, Reference]]``

Any `HTTP status code <https://spec.openapis.org/oas/v3.1.0#httpCodes>`_ can be used as the property name, but only one
property per code, to describe the expected response for that HTTP status code.

A `Reference Object <https://spec.openapis.org/oas/v3.1.0#referenceObject>`_ can link to a response that is defined in
the `OpenAPI Object's components/responses <https://spec.openapis.org/oas/v3.1.0#componentsResponses>`_ section. This
field MUST be enclosed in quotation marks (for example, ``200``) for compatibility between JSON and YAML. To define a
range of response codes, this field MAY contain the uppercase wildcard character ``X``. For example, ``2XX`` represents
all response codes between ``[200-299]``. Only the following range definitions are allowed: ``1XX``, ``2XX``, ``3XX``,
``4XX``, and ``5XX``. If a response is defined using an explicit code, the explicit code definition takes precedence
over the range definition for that code.
"""
