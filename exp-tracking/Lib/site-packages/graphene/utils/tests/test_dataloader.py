from asyncio import gather
from collections import namedtuple
from functools import partial
from unittest.mock import Mock

from graphene.utils.dataloader import DataLoader
from pytest import mark, raises

from graphene import ObjectType, String, Schema, Field, List

CHARACTERS = {
    "1": {"name": "Luke Skywalker", "sibling": "3"},
    "2": {"name": "Darth Vader", "sibling": None},
    "3": {"name": "Leia Organa", "sibling": "1"},
}

get_character = Mock(side_effect=lambda character_id: CHARACTERS[character_id])


class CharacterType(ObjectType):
    name = String()
    sibling = Field(lambda: CharacterType)

    async def resolve_sibling(character, info):
        if character["sibling"]:
            return await info.context.character_loader.load(character["sibling"])
        return None


class Query(ObjectType):
    skywalker_family = List(CharacterType)

    async def resolve_skywalker_family(_, info):
        return await info.context.character_loader.load_many(["1", "2", "3"])


mock_batch_load_fn = Mock(
    side_effect=lambda character_ids: [get_character(id) for id in character_ids]
)


class CharacterLoader(DataLoader):
    async def batch_load_fn(self, character_ids):
        return mock_batch_load_fn(character_ids)


Context = namedtuple("Context", "character_loader")


@mark.asyncio
async def test_basic_dataloader():
    schema = Schema(query=Query)

    character_loader = CharacterLoader()
    context = Context(character_loader=character_loader)

    query = """
        {
            skywalkerFamily {
                name
                sibling {
                    name
                }
            }
        }
    """

    result = await schema.execute_async(query, context=context)

    assert not result.errors
    assert result.data == {
        "skywalkerFamily": [
            {"name": "Luke Skywalker", "sibling": {"name": "Leia Organa"}},
            {"name": "Darth Vader", "sibling": None},
            {"name": "Leia Organa", "sibling": {"name": "Luke Skywalker"}},
        ]
    }

    assert mock_batch_load_fn.call_count == 1
    assert get_character.call_count == 3


def id_loader(**options):
    load_calls = []

    async def default_resolve(x):
        return x

    resolve = options.pop("resolve", default_resolve)

    async def fn(keys):
        load_calls.append(keys)
        return await resolve(keys)
        # return keys

    identity_loader = DataLoader(fn, **options)
    return identity_loader, load_calls


@mark.asyncio
async def test_build_a_simple_data_loader():
    async def call_fn(keys):
        return keys

    identity_loader = DataLoader(call_fn)

    promise1 = identity_loader.load(1)

    value1 = await promise1
    assert value1 == 1


@mark.asyncio
async def test_can_build_a_data_loader_from_a_partial():
    value_map = {1: "one"}

    async def call_fn(context, keys):
        return [context.get(key) for key in keys]

    partial_fn = partial(call_fn, value_map)
    identity_loader = DataLoader(partial_fn)

    promise1 = identity_loader.load(1)

    value1 = await promise1
    assert value1 == "one"


@mark.asyncio
async def test_supports_loading_multiple_keys_in_one_call():
    async def call_fn(keys):
        return keys

    identity_loader = DataLoader(call_fn)

    promise_all = identity_loader.load_many([1, 2])

    values = await promise_all
    assert values == [1, 2]

    promise_all = identity_loader.load_many([])

    values = await promise_all
    assert values == []


@mark.asyncio
async def test_batches_multiple_requests():
    identity_loader, load_calls = id_loader()

    promise1 = identity_loader.load(1)
    promise2 = identity_loader.load(2)

    p = gather(promise1, promise2)

    value1, value2 = await p

    assert value1 == 1
    assert value2 == 2

    assert load_calls == [[1, 2]]


@mark.asyncio
async def test_batches_multiple_requests_with_max_batch_sizes():
    identity_loader, load_calls = id_loader(max_batch_size=2)

    promise1 = identity_loader.load(1)
    promise2 = identity_loader.load(2)
    promise3 = identity_loader.load(3)

    p = gather(promise1, promise2, promise3)

    value1, value2, value3 = await p

    assert value1 == 1
    assert value2 == 2
    assert value3 == 3

    assert load_calls == [[1, 2], [3]]


@mark.asyncio
async def test_coalesces_identical_requests():
    identity_loader, load_calls = id_loader()

    promise1 = identity_loader.load(1)
    promise2 = identity_loader.load(1)

    assert promise1 == promise2
    p = gather(promise1, promise2)

    value1, value2 = await p

    assert value1 == 1
    assert value2 == 1

    assert load_calls == [[1]]


@mark.asyncio
async def test_caches_repeated_requests():
    identity_loader, load_calls = id_loader()

    a, b = await gather(identity_loader.load("A"), identity_loader.load("B"))

    assert a == "A"
    assert b == "B"

    assert load_calls == [["A", "B"]]

    a2, c = await gather(identity_loader.load("A"), identity_loader.load("C"))

    assert a2 == "A"
    assert c == "C"

    assert load_calls == [["A", "B"], ["C"]]

    a3, b2, c2 = await gather(
        identity_loader.load("A"), identity_loader.load("B"), identity_loader.load("C")
    )

    assert a3 == "A"
    assert b2 == "B"
    assert c2 == "C"

    assert load_calls == [["A", "B"], ["C"]]


@mark.asyncio
async def test_clears_single_value_in_loader():
    identity_loader, load_calls = id_loader()

    a, b = await gather(identity_loader.load("A"), identity_loader.load("B"))

    assert a == "A"
    assert b == "B"

    assert load_calls == [["A", "B"]]

    identity_loader.clear("A")

    a2, b2 = await gather(identity_loader.load("A"), identity_loader.load("B"))

    assert a2 == "A"
    assert b2 == "B"

    assert load_calls == [["A", "B"], ["A"]]


@mark.asyncio
async def test_clears_all_values_in_loader():
    identity_loader, load_calls = id_loader()

    a, b = await gather(identity_loader.load("A"), identity_loader.load("B"))

    assert a == "A"
    assert b == "B"

    assert load_calls == [["A", "B"]]

    identity_loader.clear_all()

    a2, b2 = await gather(identity_loader.load("A"), identity_loader.load("B"))

    assert a2 == "A"
    assert b2 == "B"

    assert load_calls == [["A", "B"], ["A", "B"]]


@mark.asyncio
async def test_allows_priming_the_cache():
    identity_loader, load_calls = id_loader()

    identity_loader.prime("A", "A")

    a, b = await gather(identity_loader.load("A"), identity_loader.load("B"))

    assert a == "A"
    assert b == "B"

    assert load_calls == [["B"]]


@mark.asyncio
async def test_does_not_prime_keys_that_already_exist():
    identity_loader, load_calls = id_loader()

    identity_loader.prime("A", "X")

    a1 = await identity_loader.load("A")
    b1 = await identity_loader.load("B")

    assert a1 == "X"
    assert b1 == "B"

    identity_loader.prime("A", "Y")
    identity_loader.prime("B", "Y")

    a2 = await identity_loader.load("A")
    b2 = await identity_loader.load("B")

    assert a2 == "X"
    assert b2 == "B"

    assert load_calls == [["B"]]


# # Represents Errors
@mark.asyncio
async def test_resolves_to_error_to_indicate_failure():
    async def resolve(keys):
        mapped_keys = [
            key if key % 2 == 0 else Exception("Odd: {}".format(key)) for key in keys
        ]
        return mapped_keys

    even_loader, load_calls = id_loader(resolve=resolve)

    with raises(Exception) as exc_info:
        await even_loader.load(1)

    assert str(exc_info.value) == "Odd: 1"

    value2 = await even_loader.load(2)
    assert value2 == 2
    assert load_calls == [[1], [2]]


@mark.asyncio
async def test_can_represent_failures_and_successes_simultaneously():
    async def resolve(keys):
        mapped_keys = [
            key if key % 2 == 0 else Exception("Odd: {}".format(key)) for key in keys
        ]
        return mapped_keys

    even_loader, load_calls = id_loader(resolve=resolve)

    promise1 = even_loader.load(1)
    promise2 = even_loader.load(2)

    with raises(Exception) as exc_info:
        await promise1

    assert str(exc_info.value) == "Odd: 1"
    value2 = await promise2
    assert value2 == 2
    assert load_calls == [[1, 2]]


@mark.asyncio
async def test_caches_failed_fetches():
    async def resolve(keys):
        mapped_keys = [Exception("Error: {}".format(key)) for key in keys]
        return mapped_keys

    error_loader, load_calls = id_loader(resolve=resolve)

    with raises(Exception) as exc_info:
        await error_loader.load(1)

    assert str(exc_info.value) == "Error: 1"

    with raises(Exception) as exc_info:
        await error_loader.load(1)

    assert str(exc_info.value) == "Error: 1"

    assert load_calls == [[1]]


@mark.asyncio
async def test_caches_failed_fetches_2():
    identity_loader, load_calls = id_loader()

    identity_loader.prime(1, Exception("Error: 1"))

    with raises(Exception) as _:
        await identity_loader.load(1)

    assert load_calls == []


# It is resilient to job queue ordering
@mark.asyncio
async def test_batches_loads_occuring_within_promises():
    identity_loader, load_calls = id_loader()

    async def load_b_1():
        return await load_b_2()

    async def load_b_2():
        return await identity_loader.load("B")

    values = await gather(identity_loader.load("A"), load_b_1())

    assert values == ["A", "B"]

    assert load_calls == [["A", "B"]]


@mark.asyncio
async def test_catches_error_if_loader_resolver_fails():
    exc = Exception("AOH!")

    def do_resolve(x):
        raise exc

    a_loader, a_load_calls = id_loader(resolve=do_resolve)

    with raises(Exception) as exc_info:
        await a_loader.load("A1")

    assert exc_info.value == exc


@mark.asyncio
async def test_can_call_a_loader_from_a_loader():
    deep_loader, deep_load_calls = id_loader()
    a_loader, a_load_calls = id_loader(
        resolve=lambda keys: deep_loader.load(tuple(keys))
    )
    b_loader, b_load_calls = id_loader(
        resolve=lambda keys: deep_loader.load(tuple(keys))
    )

    a1, b1, a2, b2 = await gather(
        a_loader.load("A1"),
        b_loader.load("B1"),
        a_loader.load("A2"),
        b_loader.load("B2"),
    )

    assert a1 == "A1"
    assert b1 == "B1"
    assert a2 == "A2"
    assert b2 == "B2"

    assert a_load_calls == [["A1", "A2"]]
    assert b_load_calls == [["B1", "B2"]]
    assert deep_load_calls == [[("A1", "A2"), ("B1", "B2")]]


@mark.asyncio
async def test_dataloader_clear_with_missing_key_works():
    async def do_resolve(x):
        return x

    a_loader, a_load_calls = id_loader(resolve=do_resolve)
    assert a_loader.clear("A1") == a_loader
