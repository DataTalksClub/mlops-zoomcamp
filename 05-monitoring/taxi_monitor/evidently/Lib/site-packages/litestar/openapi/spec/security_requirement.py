from __future__ import annotations

from typing import Dict, List

SecurityRequirement = Dict[str, List[str]]
"""Lists the required security schemes to execute this operation. The name used for each property MUST correspond to a
security scheme declared in the.

`Security Schemes <https://spec.openapis.org/oas/v3.1.0#componentsSecuritySchemes>`_ under the
`Components Object <https://spec.openapis.org/oas/v3.1.0#componentsObject>`_.

Security Requirement Objects that contain multiple schemes require that all schemes MUST be satisfied for a request to
be authorized. This enables support for scenarios where multiple query parameters or HTTP headers are required to convey
security information.

When a list of Security Requirement Objects is defined on the
`OpenAPI Object <https://spec.openapis.org/oas/v3.1.0#oasObject>`_ or
`Operation Object <https://spec.openapis.org/oas/v3.1.0#operationObject>`_, only one of the Security Requirement
Objects in the list needs to be satisfied to authorize the request.

Patterned Fields

{name}: ``List[str]``
Each name MUST correspond to a security scheme which is declared
in the `Security Schemes <https://spec.openapis.org/oas/v3.1.0#componentsSecuritySchemes>`_ under the
`Components Object <https://spec.openapis.org/oas/v3.1.0#componentsObject>`_. if the security scheme is of type
``"oauth2"`` or ``"openIdConnect"``, then the value is a list of scope names required for the execution, and the list
MAY be empty if authorization does not require a specified scope. For other security scheme types, the array MAY contain
a list of role names which are required for the execution,but are not otherwise defined or exchanged in-band.
"""
