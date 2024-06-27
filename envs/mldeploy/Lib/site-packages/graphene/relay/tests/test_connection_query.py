from pytest import mark

from graphql_relay.utils import base64

from ...types import ObjectType, Schema, String
from ..connection import Connection, ConnectionField, PageInfo
from ..node import Node

letter_chars = ["A", "B", "C", "D", "E"]


class Letter(ObjectType):
    class Meta:
        interfaces = (Node,)

    letter = String()


class LetterConnection(Connection):
    class Meta:
        node = Letter


class Query(ObjectType):
    letters = ConnectionField(LetterConnection)
    connection_letters = ConnectionField(LetterConnection)
    async_letters = ConnectionField(LetterConnection)

    node = Node.Field()

    def resolve_letters(self, info, **args):
        return list(letters.values())

    async def resolve_async_letters(self, info, **args):
        return list(letters.values())

    def resolve_connection_letters(self, info, **args):
        return LetterConnection(
            page_info=PageInfo(has_next_page=True, has_previous_page=False),
            edges=[
                LetterConnection.Edge(node=Letter(id=0, letter="A"), cursor="a-cursor")
            ],
        )


schema = Schema(Query)

letters = {letter: Letter(id=i, letter=letter) for i, letter in enumerate(letter_chars)}


def edges(selected_letters):
    return [
        {
            "node": {"id": base64("Letter:%s" % letter.id), "letter": letter.letter},
            "cursor": base64("arrayconnection:%s" % letter.id),
        }
        for letter in [letters[i] for i in selected_letters]
    ]


def cursor_for(ltr):
    letter = letters[ltr]
    return base64("arrayconnection:%s" % letter.id)


async def execute(args=""):
    if args:
        args = "(" + args + ")"
    return await schema.execute_async(
        """
    {
        letters%s {
            edges {
                node {
                    id
                    letter
                }
                cursor
            }
            pageInfo {
                hasPreviousPage
                hasNextPage
                startCursor
                endCursor
            }
        }
    }
    """
        % args
    )


async def check(args, letters, has_previous_page=False, has_next_page=False):
    result = await execute(args)
    expected_edges = edges(letters)
    expected_page_info = {
        "hasPreviousPage": has_previous_page,
        "hasNextPage": has_next_page,
        "endCursor": expected_edges[-1]["cursor"] if expected_edges else None,
        "startCursor": expected_edges[0]["cursor"] if expected_edges else None,
    }

    assert not result.errors
    assert result.data == {
        "letters": {"edges": expected_edges, "pageInfo": expected_page_info}
    }


@mark.asyncio
async def test_returns_all_elements_without_filters():
    await check("", "ABCDE")


@mark.asyncio
async def test_respects_a_smaller_first():
    await check("first: 2", "AB", has_next_page=True)


@mark.asyncio
async def test_respects_an_overly_large_first():
    await check("first: 10", "ABCDE")


@mark.asyncio
async def test_respects_a_smaller_last():
    await check("last: 2", "DE", has_previous_page=True)


@mark.asyncio
async def test_respects_an_overly_large_last():
    await check("last: 10", "ABCDE")


@mark.asyncio
async def test_respects_first_and_after():
    await check(f'first: 2, after: "{cursor_for("B")}"', "CD", has_next_page=True)


@mark.asyncio
async def test_respects_first_and_after_with_long_first():
    await check(f'first: 10, after: "{cursor_for("B")}"', "CDE")


@mark.asyncio
async def test_respects_last_and_before():
    await check(f'last: 2, before: "{cursor_for("D")}"', "BC", has_previous_page=True)


@mark.asyncio
async def test_respects_last_and_before_with_long_last():
    await check(f'last: 10, before: "{cursor_for("D")}"', "ABC")


@mark.asyncio
async def test_respects_first_and_after_and_before_too_few():
    await check(
        f'first: 2, after: "{cursor_for("A")}", before: "{cursor_for("E")}"',
        "BC",
        has_next_page=True,
    )


@mark.asyncio
async def test_respects_first_and_after_and_before_too_many():
    await check(
        f'first: 4, after: "{cursor_for("A")}", before: "{cursor_for("E")}"', "BCD"
    )


@mark.asyncio
async def test_respects_first_and_after_and_before_exactly_right():
    await check(
        f'first: 3, after: "{cursor_for("A")}", before: "{cursor_for("E")}"', "BCD"
    )


@mark.asyncio
async def test_respects_last_and_after_and_before_too_few():
    await check(
        f'last: 2, after: "{cursor_for("A")}", before: "{cursor_for("E")}"',
        "CD",
        has_previous_page=True,
    )


@mark.asyncio
async def test_respects_last_and_after_and_before_too_many():
    await check(
        f'last: 4, after: "{cursor_for("A")}", before: "{cursor_for("E")}"', "BCD"
    )


@mark.asyncio
async def test_respects_last_and_after_and_before_exactly_right():
    await check(
        f'last: 3, after: "{cursor_for("A")}", before: "{cursor_for("E")}"', "BCD"
    )


@mark.asyncio
async def test_returns_no_elements_if_first_is_0():
    await check("first: 0", "", has_next_page=True)


@mark.asyncio
async def test_returns_all_elements_if_cursors_are_invalid():
    await check('before: "invalid" after: "invalid"', "ABCDE")


@mark.asyncio
async def test_returns_all_elements_if_cursors_are_on_the_outside():
    await check(
        f'before: "{base64("arrayconnection:%s" % 6)}" after: "{base64("arrayconnection:%s" % -1)}"',
        "ABCDE",
    )


@mark.asyncio
async def test_returns_no_elements_if_cursors_cross():
    await check(
        f'before: "{base64("arrayconnection:%s" % 2)}" after: "{base64("arrayconnection:%s" % 4)}"',
        "",
    )


@mark.asyncio
async def test_connection_type_nodes():
    result = await schema.execute_async(
        """
    {
        connectionLetters {
            edges {
                node {
                    id
                    letter
                }
                cursor
            }
            pageInfo {
                hasPreviousPage
                hasNextPage
            }
        }
    }
    """
    )

    assert not result.errors
    assert result.data == {
        "connectionLetters": {
            "edges": [
                {"node": {"id": "TGV0dGVyOjA=", "letter": "A"}, "cursor": "a-cursor"}
            ],
            "pageInfo": {"hasPreviousPage": False, "hasNextPage": True},
        }
    }


@mark.asyncio
async def test_connection_async():
    result = await schema.execute_async(
        """
    {
        asyncLetters(first:1) {
            edges {
                node {
                    id
                    letter
                }
            }
            pageInfo {
                hasPreviousPage
                hasNextPage
            }
        }
    }
    """
    )

    assert not result.errors
    assert result.data == {
        "asyncLetters": {
            "edges": [{"node": {"id": "TGV0dGVyOjA=", "letter": "A"}}],
            "pageInfo": {"hasPreviousPage": False, "hasNextPage": True},
        }
    }
