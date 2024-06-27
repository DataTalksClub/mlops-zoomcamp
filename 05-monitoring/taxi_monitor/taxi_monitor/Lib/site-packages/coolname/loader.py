"""
This module provides `load_config` function,
which loads configuration from file or directory.

You will need this only if you are creating
custom instance of RandomGenerator.
"""


import codecs
import json
import os
import re

from .config import _CONF
from .exceptions import InitializationError, ConfigurationError


def load_config(path):
    """
    Loads configuration from a path.

    Path can be a json file, or a directory containing config.json
    and zero or more *.txt files with word lists or phrase lists.

    Returns config dict.

    Raises InitializationError when something is wrong.
    """
    path = os.path.abspath(path)
    if os.path.isdir(path):
        config, wordlists = _load_data(path)
    elif os.path.isfile(path):
        config = _load_config(path)
        wordlists = {}
    else:
        raise InitializationError('File or directory not found: {0}'.format(path))
    for name, wordlist in wordlists.items():
        if name in config:
            raise InitializationError("Conflict: list {!r} is defined both in config "
                                      "and in *.txt file. If it's a {!r} list, "
                                      "you should remove it from config."
                                      .format(name, _CONF.TYPE.WORDS))
        config[name] = wordlist
    return config


def _load_data(path):
    """
    Loads data from a directory.
    Returns tuple (config_dict, wordlists).
    Raises Exception on failure (e.g. if data is corrupted).
    """
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        raise InitializationError('Directory not found: {0}'.format(path))
    wordlists = {}
    for file_name in os.listdir(path):
        if os.path.splitext(file_name)[1] != '.txt':
            continue
        file_path = os.path.join(path, file_name)
        name = os.path.splitext(os.path.split(file_path)[1])[0]
        try:
            with codecs.open(file_path, encoding='utf-8') as file:
                wordlists[name] = _load_wordlist(name, file)
        except OSError as ex:
            raise InitializationError('Failed to read {}: {}'.format(file_path, ex))
    config = _load_config(os.path.join(path, 'config.json'))
    return (config, wordlists)


def _load_config(config_file_path):
    try:
        with codecs.open(config_file_path, encoding='utf-8') as file:
            return json.load(file)
    except OSError as ex:
        raise InitializationError('Failed to read config from {}: {}'.format(config_file_path, ex))
    except ValueError as ex:
        raise ConfigurationError('Invalid JSON: {}'.format(ex))


# Word must be in English, 1-N letters, lowercase.
_WORD_REGEX = re.compile(r'^[a-z]+$')
_PHRASE_REGEX = re.compile(r'^\w+(?: \w+)*$')


# Options are defined using simple notation: 'option = value'
_OPTION_REGEX = re.compile(r'^([a-z_]+)\s*=\s*(\w+)$', re.UNICODE)
_OPTIONS = [
    (_CONF.FIELD.MAX_LENGTH, int),
    (_CONF.FIELD.NUMBER_OF_WORDS, int)
]


def _parse_option(line):
    """
    Parses option line.
    Returns (name, value).
    Raises ValueError on invalid syntax or unknown option.
    """
    match = _OPTION_REGEX.match(line)
    if not match:
        raise ValueError('Invalid syntax')
    for name, type_ in _OPTIONS:
        if name == match.group(1):
            return name, type_(match.group(2))
    raise ValueError('Unknown option')


def _load_wordlist(name, stream):
    """
    Loads list of words or phrases from file.

    Returns "words" or "phrases" dictionary, the same as used in config.
    Raises Exception if file is missing or invalid.
    """
    items = []
    max_length = None
    multiword = False
    multiword_start = None
    number_of_words = None
    for i, line in enumerate(stream, start=1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Is it an option line, e.g. 'max_length = 10'?
        if '=' in line:
            if items:
                raise ConfigurationError('Invalid assignment at list {!r} line {}: {!r} '
                                         '(options must be defined before words)'
                                         .format(name, i, line))
            try:
                option, option_value = _parse_option(line)
            except ValueError as ex:
                raise ConfigurationError('Invalid assignment at list {!r} line {}: {!r} '
                                         '({})'
                                         .format(name, i, line, ex))
            if option == _CONF.FIELD.MAX_LENGTH:
                max_length = option_value
            elif option == _CONF.FIELD.NUMBER_OF_WORDS:
                number_of_words = option_value
            continue  # pragma: no cover
        # Parse words
        if not multiword and _WORD_REGEX.match(line):
            if max_length is not None and len(line) > max_length:
                raise ConfigurationError('Word is too long at list {!r} line {}: {!r}'
                                         .format(name, i, line))
            items.append(line)
        elif _PHRASE_REGEX.match(line):
            if not multiword:
                multiword = True
                multiword_start = len(items)
            phrase = tuple(line.split(' '))
            if number_of_words is not None and len(phrase) != number_of_words:
                raise ConfigurationError('Phrase has {} word(s) (while number_of_words={}) '
                                         'at list {!r} line {}: {!r}'
                                         .format(len(phrase), number_of_words, name, i, line))
            if max_length is not None and sum(len(x) for x in phrase) > max_length:
                raise ConfigurationError('Phrase is too long at list {!r} line {}: {!r}'
                                         .format(name, i, line))
            items.append(phrase)
        else:
            raise ConfigurationError('Invalid syntax at list {!r} line {}: {!r}'
                                     .format(name, i, line))
    if multiword:
        # If in phrase mode, convert everything to tuples
        for i in range(0, multiword_start):
            items[i] = (items[i], )
        result = {
            _CONF.FIELD.TYPE: _CONF.TYPE.PHRASES,
            _CONF.FIELD.PHRASES: items
        }
        if number_of_words is not None:
            result[_CONF.FIELD.NUMBER_OF_WORDS] = number_of_words
    else:
        result = {
            _CONF.FIELD.TYPE: _CONF.TYPE.WORDS,
            _CONF.FIELD.WORDS: items
        }
    if max_length is not None:
        result[_CONF.FIELD.MAX_LENGTH] = max_length
    return result
