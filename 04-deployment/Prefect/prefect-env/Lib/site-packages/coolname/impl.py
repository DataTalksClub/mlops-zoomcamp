"""
Do not import anything directly from this module.
"""
from functools import partial
import hashlib
import itertools
import os
import os.path as op
import random
from random import randrange
import re
from typing import List, Union

from .config import _CONF
from .exceptions import ConfigurationError, InitializationError

# For new Python versions with (possible) OpenSSL FIPS support,
# we should pass usedforsecurity=False argument to md5().
try:
    hashlib.md5(b'', usedforsecurity=False)  # noqa
    _md5 = partial(hashlib.md5, usedforsecurity=False)
except TypeError:
    _md5 = hashlib.md5


class AbstractNestedList:

    def __init__(self, lists):
        super().__init__()
        self._lists = [WordList(x) if x.__class__ is list else x
                       for x in lists]
        # If this is set to True in a subclass,
        # then subclass yields sequences instead of single words.
        self.multiword = any(x.multiword for x in self._lists)

    def __str__(self):
        return f'{self.__class__.__name__}({len(self._lists)}, len={self.length})'

    def __repr__(self):
        return self.__str__()

    def squash(self, hard, cache):
        if len(self._lists) == 1:
            return self._lists[0].squash(hard, cache)
        else:
            self._lists = [x.squash(hard, cache) for x in self._lists]
            return self

    def _dump(self, stream, indent='', object_ids=False):
        stream.write(indent + str(self) +
                     (f' [id={id(self)}]' if object_ids else '') +
                     '\n')
        indent += '  '
        for sublist in self._lists:
            sublist._dump(stream, indent, object_ids=object_ids)  # noqa


# Convert value to bytes, for hashing
# (used to calculate WordList or PhraseList hash)
def _to_bytes(value):
    if isinstance(value, str):
        return value.encode('utf-8')
    elif isinstance(value, tuple):
        return str(value).encode('utf-8')
    else:
        return value


class _BasicList(list, AbstractNestedList):

    def __init__(self, sequence=None):
        list.__init__(self, sequence)
        AbstractNestedList.__init__(self, [])
        self.length = len(self)
        self.__hash = None

    def __str__(self):
        ls = [repr(x) for x in self[:4]]
        if len(ls) == 4:
            ls[3] = '...'
        return '{}([{}], len={})'.format(self.__class__.__name__, ', '.join(ls), len(self))

    def __repr__(self):
        return self.__str__()

    def squash(self, hard, cache):
        return self

    @property
    def _hash(self):
        if self.__hash:
            return self.__hash
        md5 = _md5()
        md5.update(_to_bytes(str(len(self))))
        for x in self:  # noqa
            md5.update(_to_bytes(x))
        self.__hash = md5.digest()
        return self.__hash


class WordList(_BasicList):
    """List of single words."""


class PhraseList(_BasicList):
    """List of phrases (sequences of one or more words)."""

    def __init__(self, sequence=None):
        super().__init__(tuple(_split_phrase(x)) for x in sequence)
        self.multiword = True


class WordAsPhraseWrapper:

    multiword = True

    def __init__(self, wordlist):
        self._list = wordlist
        self.length = len(wordlist)

    def __len__(self):
        return self.length

    def __getitem__(self, i):
        return self._list[i],

    def squash(self, hard, cache):  # noqa
        return self

    def __str__(self):
        return f'{self.__class__.__name__}({self._list})'

    def __repr__(self):
        return f'{self.__class__.__name__}({self._list!r})'


class NestedList(AbstractNestedList):

    def __init__(self, lists):
        super().__init__(lists)
        # If user mixes WordList and PhraseList in the same NestedList,
        # we need to make sure that __getitem__ always returns tuple.
        # For that, we wrap WordList instances.
        if any(isinstance(x, WordList) for x in self._lists) and any(x.multiword for x in self._lists):
            self._lists = [WordAsPhraseWrapper(x) if isinstance(x, WordList) else x for x in self._lists]
        # Fattest lists first (to reduce average __getitem__ time)
        self._lists.sort(key=lambda x: -x.length)
        self.length = sum(x.length for x in self._lists)

    def __getitem__(self, i):
        # Retrieve item from appropriate list
        for x in self._lists:
            n = x.length
            if i < n:
                return x[i]
            else:
                i -= n
        raise IndexError('list index out of range')

    def squash(self, hard, cache):
        # Cache is used to avoid data duplication.
        # If we have 4 branches which finally point to the same list of nouns,
        # why not using the same WordList instance for all 4 branches?
        # This optimization is also applied to PhraseLists, just in case.
        result = super().squash(hard, cache)
        if result is self and hard:
            for cls in (WordList, PhraseList):
                if all(isinstance(x, cls) for x in self._lists):
                    # Creating combined WordList/PhraseList and then checking cache
                    # is a little wasteful, but it has no long-term consequences.
                    # And it's simple!
                    result = cls(sorted(set(itertools.chain.from_iterable(self._lists))))
                    if result._hash in cache:  # noqa
                        result = cache.get(result._hash)  # noqa
                    else:
                        cache[result._hash] = result  # noqa
        return result


class CartesianList(AbstractNestedList):

    def __init__(self, lists):
        super().__init__(lists)
        self.length = 1
        for x in self._lists:
            self.length *= x.length
        # Let's say list lengths are 5, 7, 11, 13.
        # divs = [7*11*13, 11*13, 13, 1]
        divs = [1]
        prod = 1
        for x in reversed(self._lists[1:]):
            prod *= x.length
            divs.append(prod)
        self._list_divs = tuple(zip(self._lists, reversed(divs)))
        self.multiword = True

    def __getitem__(self, i):
        result = []
        for sublist, n in self._list_divs:
            x = sublist[i // n]
            if sublist.multiword:
                result.extend(x)
            else:
                result.append(x)
            i %= n
        return result


class Scalar(AbstractNestedList):

    def __init__(self, value):
        super().__init__([])
        self.value = value
        self.length = 1

    def __getitem__(self, i):
        return self.value

    def __str__(self):
        return f'{self.__class__.__name__}(value={self.value!r})'

    def random(self):
        return self.value


class RandomGenerator:
    """
    This class provides random name generation interface.

    Create an instance of this class if you want to create custom
    configuration.
    If default implementation is enough, just use `generate`,
    `generate_slug` and other exported functions.
    """

    def __init__(self, config, rand=None):
        self.random = rand  # sets _random and _randrange
        config = dict(config)
        _validate_config(config)
        lists = {}
        _create_lists(config, lists, 'all', [])
        self._lists = {}
        for key, listdef in config.items():
            # Other generators independent from 'all'
            if listdef.get(_CONF.FIELD.GENERATOR) and key not in lists:
                _create_lists(config, lists, key, [])
            if key == 'all' or key.isdigit() or listdef.get(_CONF.FIELD.GENERATOR):
                if key.isdigit():
                    pattern = int(key)
                elif key == 'all':
                    pattern = None
                else:
                    pattern = key
                self._lists[pattern] = lists[key]
        self._lists[None] = self._lists[None].squash(True, {})
        # Should we avoid duplicates?
        try:
            ensure_unique = config['all'][_CONF.FIELD.ENSURE_UNIQUE]
            if not isinstance(ensure_unique, bool):
                raise ValueError(f'expected boolean, got {ensure_unique!r}')
            self._ensure_unique = ensure_unique
        except KeyError:
            self._ensure_unique = False
        except ValueError as ex:
            raise ConfigurationError(f'Invalid {_CONF.FIELD.ENSURE_UNIQUE} value: {ex}')
        # Should we avoid duplicating prefixes?
        try:
            self._check_prefix = int(config['all'][_CONF.FIELD.ENSURE_UNIQUE_PREFIX])
            if self._check_prefix <= 0:
                raise ValueError(f'expected a positive integer, got {self._check_prefix!r}')
        except KeyError:
            self._check_prefix = None
        except ValueError as ex:
            raise ConfigurationError(f'Invalid {_CONF.FIELD.ENSURE_UNIQUE_PREFIX} value: {ex}')
        # Get max slug length
        try:
            self._max_slug_length = int(config['all'][_CONF.FIELD.MAX_SLUG_LENGTH])
        except KeyError:
            self._max_slug_length = None
        except ValueError as ex:
            raise ConfigurationError(f'Invalid {_CONF.FIELD.MAX_SLUG_LENGTH} value: {ex}')
        # Make sure that generate() does not go into long loop.
        # Default generator is a special case, we don't need check.
        if (not config['all'].get('__nocheck') and
                self._ensure_unique or self._check_prefix or self._max_slug_length):
            self._check_not_hanging()
        # Fire it up
        assert self.generate_slug()

    @property
    def random(self):
        return self._random

    @random.setter
    def random(self, rand):
        if rand:
            self._random = rand
        else:
            self._random = random
        self._randrange = self._random.randrange

    def generate(self, pattern: Union[None, str, int] = None) -> List[str]:
        """
        Generates and returns random name as a list of strings.
        """
        lst = self._lists[pattern]
        while True:
            result = lst[self._randrange(lst.length)]
            # 1. Check that there are no duplicates
            # 2. Check that there are no duplicate prefixes
            # 3. Check max slug length
            n = len(result)
            if (self._ensure_unique and len(set(result)) != n or
                    self._check_prefix and len(set(x[:self._check_prefix] for x in result)) != n or
                    self._max_slug_length and sum(len(x) for x in result) + n - 1 > self._max_slug_length):
                continue
            return result

    def generate_slug(self, pattern: Union[None, str, int] = None) -> str:
        """
        Generates and returns random name as a slug.
        """
        return '-'.join(self.generate(pattern))

    def get_combinations_count(self, pattern: Union[None, str, int] = None) -> int:
        """
        Returns total number of unique combinations
        for the given pattern.
        """
        lst = self._lists[pattern]
        return lst.length

    def _dump(self, stream, pattern=None, object_ids=False):
        """Dumps current tree into a text stream."""
        return self._lists[pattern]._dump(stream, '', object_ids=object_ids)  # noqa

    def _check_not_hanging(self):
        """
        Rough check that generate() will not hang or be very slow.

        Raises ConfigurationError if generate() spends too much time in retry loop.
        Issues a warning.warn() if there is a risk of slowdown.
        """
        # (field_name, predicate, warning_msg, exception_msg)
        # predicate(g) is a function that returns True if generated combination g must be rejected,
        # see checks in generate()
        checks = []
        # ensure_unique can lead to infinite loops for some tiny erroneous configs
        if self._ensure_unique:
            checks.append((
                _CONF.FIELD.ENSURE_UNIQUE,
                self._ensure_unique,
                lambda g: len(set(g)) != len(g),
                '{generate} may be slow because a significant fraction of combinations contain repeating words and {field_name} is set',  # noqa
                'Impossible to generate with {field_name}'
            ))
        #
        # max_slug_length can easily slow down or block generation if set too small
        if self._max_slug_length:
            checks.append((
                _CONF.FIELD.MAX_SLUG_LENGTH,
                self._max_slug_length,
                lambda g: sum(len(x) for x in g) + len(g) - 1 > self._max_slug_length,
                '{generate} may be slow because a significant fraction of combinations exceed {field_name}={field_value}',  # noqa
                'Impossible to generate with {field_name}={field_value}'
            ))
        # Perform the relevant checks for all generators, starting from 'all'
        n = 100
        warning_threshold = 20  # fail probability: 0.04 for 2 attempts, 0.008 for 3 attempts, etc.
        for lst_id, lst in sorted(self._lists.items(), key=lambda x: '' if x is None else str(x)):
            context = {'generate': 'coolname.generate({})'.format('' if lst_id is None else repr(lst_id))}
            # For each generator, perform checks
            for field_name, field_value, predicate, warning_msg, exception_msg in checks:
                context.update({'field_name': field_name, 'field_value': field_value})
                bad_count = 0
                for _ in range(n):
                    if predicate(lst[randrange(lst.length)]):
                        bad_count += 1
                if bad_count >= n:
                    raise ConfigurationError(exception_msg.format(**context))
                elif bad_count >= warning_threshold:
                    import warnings
                    warnings.warn(warning_msg.format(**context))


def _is_str(value):
    return value.__class__.__name__ in ('str', 'unicode')


# Translate phrases defined as strings to tuples
def _split_phrase(x):
    try:
        return re.split(r'\s+', x.strip())
    except AttributeError:  # Not str
        return x


def _validate_config(config):
    """
    A big and ugly method for config validation.
    It would be nice to use cerberus, but we don't
    want to introduce dependencies just for that.
    """
    try:
        referenced_sublists = set()
        for key, listdef in list(config.items()):
            # Check if section is a list
            if not isinstance(listdef, dict):
                raise ValueError(f'Value at key {key!r} is not a dict')
            # Check if it has correct type
            if _CONF.FIELD.TYPE not in listdef:
                raise ValueError(f'Config at key {key!r} has no {_CONF.FIELD.TYPE!r}')
            # Nested or Cartesian
            if listdef[_CONF.FIELD.TYPE] in (_CONF.TYPE.NESTED, _CONF.TYPE.CARTESIAN):
                sublists = listdef.get(_CONF.FIELD.LISTS)
                if sublists is None:
                    raise ValueError('Config at key {!r} has no {!r}'
                                     .format(key, _CONF.FIELD.LISTS))
                if (not isinstance(sublists, list) or not sublists or
                        not all(_is_str(x) for x in sublists)):
                    raise ValueError('Config at key {!r} has invalid {!r}'
                                     .format(key, _CONF.FIELD.LISTS))
                referenced_sublists.update(sublists)
            # Const
            elif listdef[_CONF.FIELD.TYPE] == _CONF.TYPE.CONST:
                try:
                    value = listdef[_CONF.FIELD.VALUE]
                except KeyError:
                    raise ValueError('Config at key {!r} has no {!r}'
                                     .format(key, _CONF.FIELD.VALUE))
                if not _is_str(value):
                    raise ValueError('Config at key {!r} has invalid {!r}'
                                     .format(key, _CONF.FIELD.VALUE))
            # Words
            elif listdef[_CONF.FIELD.TYPE] == _CONF.TYPE.WORDS:
                try:
                    words = listdef[_CONF.FIELD.WORDS]
                except KeyError:
                    raise ValueError('Config at key {!r} has no {!r}'
                                     .format(key, _CONF.FIELD.WORDS))
                if not isinstance(words, list) or not words:
                    raise ValueError('Config at key {!r} has invalid {!r}'
                                     .format(key, _CONF.FIELD.WORDS))
                # Validate word length
                try:
                    max_length = int(listdef[_CONF.FIELD.MAX_LENGTH])
                except KeyError:
                    max_length = None
                if max_length is not None:
                    for word in words:
                        if len(word) > max_length:
                            raise ValueError('Config at key {!r} has invalid word {!r} '
                                             '(longer than {} characters)'
                                             .format(key, word, max_length))
            # Phrases (sequences of one or more words)
            elif listdef[_CONF.FIELD.TYPE] == _CONF.TYPE.PHRASES:
                try:
                    phrases = listdef[_CONF.FIELD.PHRASES]
                except KeyError:
                    raise ValueError('Config at key {!r} has no {!r}'
                                     .format(key, _CONF.FIELD.PHRASES))
                if not isinstance(phrases, list) or not phrases:
                    raise ValueError('Config at key {!r} has invalid {!r}'
                                     .format(key, _CONF.FIELD.PHRASES))
                # Validate multi-word and max length
                try:
                    number_of_words = int(listdef[_CONF.FIELD.NUMBER_OF_WORDS])
                except KeyError:
                    number_of_words = None
                try:
                    max_length = int(listdef[_CONF.FIELD.MAX_LENGTH])
                except KeyError:
                    max_length = None
                for phrase in phrases:
                    phrase = _split_phrase(phrase)  # str -> sequence, if necessary
                    if not isinstance(phrase, (tuple, list)) or not all(isinstance(x, str) for x in phrase):
                        raise ValueError('Config at key {!r} has invalid {!r}: '
                                         'must be all string/tuple/list'
                                         .format(key, _CONF.FIELD.PHRASES))
                    if number_of_words is not None and len(phrase) != number_of_words:
                        raise ValueError('Config at key {!r} has invalid phrase {!r} '
                                         '({} word(s) but {}={})'
                                         .format(key, ' '.join(phrase),
                                                 len(phrase), _CONF.FIELD.NUMBER_OF_WORDS, number_of_words))
                    if max_length is not None and sum(len(word) for word in phrase) > max_length:
                        raise ValueError('Config at key {!r} has invalid phrase {!r} '
                                         '(longer than {} characters)'
                                         .format(key, ' '.join(phrase), max_length))
            else:
                raise ValueError('Config at key {!r} has invalid {!r}'
                                 .format(key, _CONF.FIELD.TYPE))
        # Check that all sublists are defined
        diff = referenced_sublists.difference(config.keys())
        if diff:
            raise ValueError('Lists are referenced but not defined: {}'
                             .format(', '.join(sorted(diff)[:10])))
    except (KeyError, ValueError) as ex:
        raise ConfigurationError(str(ex))


def _create_lists(config, results, current, stack, inside_cartesian=None):
    """
    An ugly recursive method to transform config dict
    into a tree of AbstractNestedList.
    """
    # Have we done it already?
    try:
        return results[current]
    except KeyError:
        pass
    # Check recursion depth and detect loops
    if current in stack:
        raise ConfigurationError('Rule {!r} is recursive: {!r}'.format(stack[0], stack))
    if len(stack) > 99:
        raise ConfigurationError('Rule {!r} is too deep'.format(stack[0]))
    # Track recursion depth
    stack.append(current)
    try:
        # Check what kind of list we have
        listdef = config[current]
        list_type = listdef[_CONF.FIELD.TYPE]
        # 1. List of words
        if list_type == _CONF.TYPE.WORDS:
            results[current] = WordList(listdef['words'])
        # List of phrases
        elif list_type == _CONF.TYPE.PHRASES:
            results[current] = PhraseList(listdef['phrases'])
        # 2. Simple list of lists
        elif list_type == _CONF.TYPE.NESTED:
            results[current] = NestedList([_create_lists(config, results, x, stack,
                                                         inside_cartesian=inside_cartesian)
                                           for x in listdef[_CONF.FIELD.LISTS]])

        # 3. Cartesian list of lists
        elif list_type == _CONF.TYPE.CARTESIAN:
            if inside_cartesian is not None:
                raise ConfigurationError("Cartesian list {!r} contains another Cartesian list "
                                         "{!r}. Nested Cartesian lists are not allowed."
                                         .format(inside_cartesian, current))
            results[current] = CartesianList([_create_lists(config, results, x, stack,
                                                            inside_cartesian=current)
                                              for x in listdef[_CONF.FIELD.LISTS]])
        # 4. Scalar
        elif list_type == _CONF.TYPE.CONST:
            results[current] = Scalar(listdef[_CONF.FIELD.VALUE])
        # Unknown type
        else:
            raise InitializationError("Unknown list type: {!r}".format(list_type))
        # Return the result
        return results[current]
    finally:
        stack.pop()


def _create_default_generator():
    data_dir = os.getenv('COOLNAME_DATA_DIR')
    data_module = os.getenv('COOLNAME_DATA_MODULE')
    if not data_dir and not data_module:
        data_dir = op.join(op.dirname(op.abspath(__file__)), 'data')
        data_module = 'coolname.data'  # used when imported from egg; consumes more memory
    if data_dir and op.isdir(data_dir):
        from coolname.loader import load_config
        config = load_config(data_dir)
    elif data_module:
        import importlib
        config = importlib.import_module(data_module).config
    else:
        raise ImportError('Configure valid COOLNAME_DATA_DIR and/or COOLNAME_DATA_MODULE')
    config['all']['__nocheck'] = True
    return RandomGenerator(config)


# Default generator is a global object
_default = _create_default_generator()

# Global functions are actually methods of the default generator.
# (most users don't care about creating generator instances)
generate = _default.generate
generate_slug = _default.generate_slug
get_combinations_count = _default.get_combinations_count


def replace_random(rand):
    """Replaces random number generator for the default RandomGenerator instance."""
    _default.random = rand
