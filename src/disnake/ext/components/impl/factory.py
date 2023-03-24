"""Standard implementation of the overarching component factory type."""

from __future__ import annotations

import types
import typing

import attr
from disnake.ext.components import fields
from disnake.ext.components.api import component as component_api
from disnake.ext.components.api import factory as factory_api
from disnake.ext.components.api import parser as parser_api
from disnake.ext.components.impl import custom_id as custom_id_impl
from disnake.ext.components.impl.parser import base as parser_base
from disnake.ext.components.internal import aio

if typing.TYPE_CHECKING:
    import disnake
    import typing_extensions

__all__: typing.Sequence[str] = ("ComponentFactory",)


_T = typing.TypeVar("_T")

ParserMapping = typing.Mapping[str, parser_api.Parser[typing.Any]]
MutableParserMapping = typing.MutableMapping[str, parser_api.Parser[typing.Any]]


@attr.define(slots=True)
class ComponentFactoryBuilder(typing.Generic[factory_api.ComponentT]):
    """A builder for component factories that support stepwise creation.

    Individually register parameters and return their parser. This is used in
    :class:`component_base.ComponentMeta` to register the parsers on each field
    as they are created.

    Call :meth:`build` to finalise the :class:`ComponentFactory`.
    """

    parsers: MutableParserMapping = attr.field(factory=dict, init=False)
    component: type[factory_api.ComponentT]

    def add_field(self, field: attr.Attribute[_T]) -> parser_api.Parser[_T]:
        """Register a new field, add its parser and return it.

        In case the field already has a parser, return it as-is. Otherwise,
        build a new parser and return it.

        Parameters
        ----------
        field:
            The field to add to the :class:`ComponentFactory`.

        Returns
        -------
        :class:`parser_api.Parser`[typing.Any]
            The parser for the provided field.
        """
        parser = fields.get_parser(field)

        if not parser:
            field_type = field.type or str  # TODO: also pass to default
            parser = parser_base.get_parser(field_type).default()

        self.parsers[field.name] = parser
        return parser

    def build(self) -> ComponentFactory[factory_api.ComponentT]:
        """Finalise the :class:`ComponentFactory` and return it.

        This makes the mapping in :attr:`self.parsers` read-only.

        Returns
        -------
        :class:`ComponentFactory`[:class:`RichComponent`]
            The newly created component factory.
        """
        return ComponentFactory(types.MappingProxyType(self.parsers), self.component)


@attr.define(slots=True)
class ComponentFactory(
    factory_api.ComponentFactory[factory_api.ComponentT],
    typing.Generic[factory_api.ComponentT],
):
    """Implementation of the overarching component factory type.

    A component factory holds information about all the custom id fields of a
    component, and contains that component's parsers. In most situations, a
    component factory can simply be created using :meth:`from_component`.
    """

    parsers: ParserMapping
    component: type[factory_api.ComponentT]

    @classmethod
    def from_component(  # noqa: D102
        cls,
        component: type[component_api.RichComponent],
    ) -> typing_extensions.Self:
        # <<docstring inherited from factory_api.ComponentFactory>>

        parser: typing.Optional[parser_api.Parser[typing.Any]]

        parsers: dict[str, parser_api.Parser[typing.Any]] = {}
        for field in fields.get_fields(component, kind=fields.FieldType.CUSTOM_ID):
            parser = fields.get_parser(field)

            if not parser:
                parser = parser_base.get_parser(field.type or str).default()

            parsers[field.name] = parser

        return cls(parsers, component)

    async def loads_param(
        self,
        interaction: disnake.Interaction,
        param: str,
        value: str,
    ) -> object:
        """Parse a single custom id parameter to the desired type with its parser.

        Parameters
        ----------
        interaction:
            The interaction that caused the component to activate.
        param:
            The name of the custom id field that is to be parsed.
        value:
            The value of the custom id field that is to be parsed.

        Returns
        -------
        :class:`object`:
            The parsed custom id field value.
        """
        parser = self.parsers[param]
        result = parser.loads(interaction, value)
        return await aio.eval_maybe_coro(result)

    async def dumps_param(
        self,
        param: str,
        value: object,
    ) -> str:
        """Parse a single custom id parameter to its string form for custom id storage.

        Parameters
        ----------
        interaction:
            The interaction that caused the component to activate.
        param:
            The name of the custom id field that is to be parsed.
        value:
            The value of the custom id field that is to be parsed.

        Returns
        -------
        :class:`str`:
            The dumped custom id parameter, ready for storage inside a custom id.
        """
        parser = self.parsers[param]
        result = parser.dumps(value)
        return await aio.eval_maybe_coro(result)

    async def loads(  # noqa: D102
        self,
        interaction: disnake.Interaction,
        params: typing.Mapping[str, str],
    ) -> factory_api.ComponentT:
        # <<docstring inherited from factory_api.ComponentFactory>>

        kwargs = {
            param: await self.loads_param(interaction, param, value)
            for param, value in params.items()
            if value
        }

        return self.component(**kwargs)

    async def dumps(self, component: factory_api.ComponentT) -> str:  # noqa: D102
        # <<docstring inherited from factory_api.ComponentFactory>>

        component_type = type(component)

        kwargs = {
            field.name: await self.dumps_param(
                field.name, getattr(component, field.name)
            )
            for field in fields.get_fields(
                component_type, kind=fields.FieldType.CUSTOM_ID
            )
        }

        return typing.cast(
            custom_id_impl.CustomID, component_type.custom_id
        ).format_map(kwargs)