__version__ = '2.2.0'

# Hint: set COOLNAME_DATA_DIR and/or COOLNAME_DATA_MODULE
# before `import coolname` to change the default generator.

from .exceptions import InitializationError
from .impl import generate, generate_slug, get_combinations_count,\
    RandomGenerator, replace_random
