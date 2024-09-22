"""Parser implementations for standard library and disnake enums and flags."""

import enum
import typing

import disnake
from disnake.ext.components.impl.parser import base as parser_base
from disnake.ext.components.internal import aio

__all__: typing.Sequence[str] = ("EnumParser", "FlagParser")

_AnyEnum = typing.Union[enum.Enum, disnake.Enum, disnake.flags.BaseFlags]
_EnumT = typing.TypeVar("_EnumT", bound=_AnyEnum)


def _get_enum_type(enum_class: typing.Type[_AnyEnum]) -> typing.Optional[type]:
    if issubclass(enum_class, disnake.flags.BaseFlags):
        return int

    maybe_type: type = getattr(enum_class, "_member_type_", object)
    if maybe_type is not object:
        return maybe_type

    # Get first member's type
    member_iter = iter(enum_class)
    maybe_type = typing.cast(  # python typing sucks.
        typing.Type[typing.Any], type(next(member_iter).value)
    )

    # If all members match this type, return it.
    if all(type(member.value) == maybe_type for member in member_iter):
        return maybe_type

    # No single type; store by name instead.
    return None


@parser_base.register_parser_for(
    enum.Enum, disnake.Enum, enum.Flag, disnake.flags.BaseFlags
)
class EnumParser(parser_base.SourcedParser[_EnumT]):
    """Parser type for enums and flags.

    Enums and flags are stored by value instead of by name. This makes parsing
    a bit slower, but values are generally shorter than names.

    This parser type works for standard library and disnake enums and flags.
    Note that this only works for enums and flags where all values are of the
    same type.

    Parameters
    ----------
    enum_class:
        The enum or flag class to use for parsing.

    """

    enum_class: typing.Type[_EnumT]
    value_parser: parser_base.AnyParser

    def __init__(
        self,
        enum_class: typing.Type[_EnumT],
        *,
        store_by_value: typing.Optional[bool] = None,
    ) -> None:
        value_type = _get_enum_type(enum_class)

        if issubclass(enum_class, disnake.flags.BaseFlags) and store_by_value is False:
            msg = (
                "Cannot store disnake flags by name, as their members do not have"
                " names."
            )
            raise ValueError(msg)

        # If the enum is not of a single type and store_by_value wasn't
        # explicitly set or was explicitly set to false, parse by name.
        if value_type is None and not store_by_value:
            self.store_by_value = False
            self.value_type = str

        # If the value type could be determined, set it on the parser and
        # respect the input for store_by_value-- default to True for integers.
        elif value_type is not None:
            self.store_by_value = (
                issubclass(value_type, int)
                if store_by_value is None
                else store_by_value
            )  # fmt: skip
            self.value_type = value_type

        # If the value type could not be determined but the user explicitly set
        # store_by_value to True, raise an exception.
        else:
            msg = (
                "Cannot store enum members by value for enums with members of"
                " varying types. Please either set `store_by_value` to False"
                " or make sure all enum members are of the same type."
            )
            raise ValueError(msg)

        self.enum_class = enum_class
        self.value_parser = parser_base.get_parser(self.value_type)

    async def loads(self, argument: str, *, source: object) -> _EnumT:  # noqa: D102
        # <<docstring inherited from parser_api.Parser>>

        parsed = await parser_base.try_loads(self.value_parser, argument, source=source)

        if self.store_by_value:
            return self.enum_class(parsed)  # pyright: ignore[reportCallIssue]
        else:
            return self.enum_class[parsed]  # pyright: ignore[reportInvalidTypeArguments]

    async def dumps(self, argument: _EnumT) -> str:  # noqa: D102
        # <<docstring inherited from parser_api.Parser>>
        if self.store_by_value:
            result = self.value_parser.dumps(argument.value)
        else:
            # Baseflags members are always integers. This should never error
            # due to the check in __init__.
            assert not isinstance(argument, disnake.flags.BaseFlags)
            result = self.value_parser.dumps(argument.name)

        return await aio.eval_maybe_coro(result)


FlagParser = EnumParser
