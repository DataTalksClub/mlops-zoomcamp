from __future__ import annotations

from dataclasses import dataclass

from litestar.openapi.spec.base import BaseSchemaObject

__all__ = ("XML",)


@dataclass()
class XML(BaseSchemaObject):
    """A metadata object that allows for more fine-tuned XML model definitions.

    When using arrays, XML element names are *not* inferred (for singular/plural forms) and the ``name`` property SHOULD
    be used to add that information. See examples for expected behavior.
    """

    name: str | None = None
    """
    Replaces the name of the element/attribute used for the described schema property. When defined within ``items``, it
    will affect the name of the individual XML elements within the list. When defined alongside ``type`` being ``array``
    (outside the ``items``), it will affect the wrapping element and only if ``wrapped`` is ``True``. If ``wrapped`` is
    ``False``, it will be ignored.
    """

    namespace: str | None = None
    """The URI of the namespace definition. Value MUST be in the form of an absolute URI."""

    prefix: str | None = None
    """The prefix to be used for the
    `xmlName <https://spec.openapis.org/oas/v3.1.0#xmlName>`_
    """

    attribute: bool = False
    """Declares whether the property definition translates to an attribute instead of an element. Default value is
    ``False``.
    """

    wrapped: bool = False
    """
    MAY be used only for an array definition. Signifies whether the array is wrapped (for example,
    ``<books><book/><book/></books>``) or unwrapped (``<book/><book/>``). Default value is ``False``. The definition
    takes effect only when defined alongside ``type`` being ``array`` (outside the ``items``).
    """
