class _CONF:
    """All strings related to config, to avoid hardcoding."""

    class TYPE:
        """Node type in configuration."""
        NESTED = 'nested'
        CARTESIAN = 'cartesian'
        WORDS = 'words'
        PHRASES = 'phrases'
        CONST = 'const'

    class FIELD:
        """Allowed fields."""
        TYPE = 'type'
        LISTS = 'lists'
        WORDS = 'words'
        PHRASES = 'phrases'
        NUMBER_OF_WORDS = 'number_of_words'
        VALUE = 'value'
        GENERATOR = 'generator'
        MAX_LENGTH = 'max_length'
        MAX_SLUG_LENGTH = 'max_slug_length'
        ENSURE_UNIQUE = 'ensure_unique'
        ENSURE_UNIQUE_PREFIX = 'ensure_unique_prefix'
