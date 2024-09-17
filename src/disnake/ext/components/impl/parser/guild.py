"""Parser implementations for disnake.Guild type."""

from __future__ import annotations

import typing

import disnake
from disnake.ext.components.impl.parser import base as parser_base
from disnake.ext.components.impl.parser import helpers, snowflake

__all__: typing.Sequence[str] = ("GuildParser", "GetGuildParser")


@parser_base.register_parser_for(disnake.Guild)
class GetGuildParser(parser_base.SourcedParser[disnake.Guild]):  # noqa: D101
    # <<docstring inherited from parser_api.Parser>>

    def __init__(self) -> None:
        super().__init__()
        self.dumps = snowflake.snowflake_dumps

    def loads(  # noqa: D102
        self,
        argument: str,
        *,
        source: typing.Union[helpers.BotAware, helpers.GuildAware],
    ) -> disnake.Guild:
        # <<docstring inherited from parser_api.Parser>>

        if isinstance(source, helpers.BotAware):
            guild = source.bot.get_guild(int(argument))

            if (
                guild is None
                and isinstance(source, helpers.GuildAware)
                and source.guild
            ):
                return source.guild

        elif source.guild:
            return source.guild

        msg = f"Could not find a guild with id {argument!r}."
        raise LookupError(msg)


@parser_base.register_parser_for(disnake.Guild)
class GuildParser(parser_base.SourcedParser[disnake.Guild]):  # noqa: D101
    # <<docstring inherited from parser_api.Parser>>

    def __init__(self) -> None:
        super().__init__()
        self.dumps = snowflake.snowflake_dumps

    async def loads(  # noqa: D102
        self,
        argument: str,
        *,
        source: typing.Union[helpers.BotAware, helpers.GuildAware],
    ) -> disnake.Guild:
        # <<docstring inherited from parser_api.Parser>>

        id_ = int(argument)
        if isinstance(source, helpers.BotAware):
            guild = source.bot.get_guild(id_)
            if guild:
                return guild

            try:
                return await source.bot.fetch_guild(id_)
            except disnake.HTTPException:
                if isinstance(source, helpers.GuildAware) and source.guild:
                    return source.guild

        elif source.guild:
            return source.guild

        msg = f"Could not find a guild with id {argument!r}."
        raise LookupError(msg)
