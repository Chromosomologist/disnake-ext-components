"""Parser implementations for disnake channel types."""

from __future__ import annotations

import typing

import disnake
from disnake.ext.components.impl.parser import base, snowflake

__all__: typing.Sequence[str] = (
    "DMChannelParser",
    "ForumChannelParser",
    "GroupChannelParser",
    "GuildChannelParser",
    "PrivateChannelParser",
    "NewsChannelParser",
    "StageChannelParser",
    "TextChannelParser",
    "VoiceChannelParser",
    "CategoryParser",
    "GetDMChannelParser",
    "GetForumChannelParser",
    "GetGroupChannelParser",
    "GetGuildChannelParser",
    "GetPrivateChannelParser",
    "GetNewsChannelParser",
    "GetStageChannelParser",
    "GetTextChannelParser",
    "GetVoiceChannelParser",
    "GetCategoryParser",
    "PartialMessageableParser",
)


_AnyChannel = typing.Union[
    disnake.abc.GuildChannel, disnake.abc.PrivateChannel, disnake.Thread
]
_ChannelT = typing.TypeVar("_ChannelT", bound=_AnyChannel)


# GET_ONLY


class GetChannelParserBase(base.Parser[_ChannelT]):  # noqa: D101
    # <<docstring inherited from parser_api.Parser>>

    parser_type: typing.Type[_ChannelT]

    def __init__(self) -> None:
        super().__init__()
        self.dumps = snowflake.snowflake_dumps

    def loads(  # noqa: D102
        self, inter: disnake.Interaction, argument: str
    ) -> _ChannelT:
        # <<docstring inherited from parser_api.Parser>>

        channel = inter.bot.get_channel(int(argument))

        if channel is None:
            msg = f"Could not find a channel with id {argument!r}."
            raise LookupError(msg)

        if not isinstance(channel, self.parser_type):
            msg = (
                f"Found a channel of type {type(channel).__name__!r} for id"
                f"{argument!r}, expected (any of) type(s) {self.parser_type.__name__}."
            )
            raise TypeError(msg)
        return channel


# GET AND FETCH


class ChannelParserBase(base.Parser[_ChannelT]):  # noqa: D101
    # <<docstring inherited from parser_api.Parser>>

    parser_type: typing.Type[_ChannelT]

    def __init__(self) -> None:
        super().__init__()
        self.dumps = snowflake.snowflake_dumps

    async def loads(  # noqa: D102
        self, inter: disnake.Interaction, argument: str
    ) -> _ChannelT:
        # <<docstring inherited from parser_api.Parser>>

        channel_id = int(argument)
        channel = (
            inter.bot.get_channel(channel_id)
            or await inter.bot.fetch_channel(channel_id)
        )  # fmt: skip

        if not isinstance(channel, self.parser_type):
            msg = (
                f"Found a channel of type {type(channel).__name__!r} for id"
                f" {argument!r}, expected (any of) type(s) {self.parser_type.__name__}."
            )
            raise TypeError(msg)
        return channel


# ABSTRACT


class GetGuildChannelParser(  # noqa: D101
    GetChannelParserBase[disnake.abc.GuildChannel],
    is_default_for=(disnake.abc.GuildChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.abc.GuildChannel


class GetPrivateChannelParser(  # noqa: D101
    GetChannelParserBase[disnake.abc.PrivateChannel],
    is_default_for=(disnake.abc.PrivateChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.abc.PrivateChannel


# PRIVATE


class GetDMChannelParser(  # noqa: D101
    GetChannelParserBase[disnake.DMChannel],
    is_default_for=(disnake.DMChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.DMChannel


class GetGroupChannelParser(  # noqa: D101
    GetChannelParserBase[disnake.GroupChannel],
    is_default_for=(disnake.GroupChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.GroupChannel


# GUILD


class GetForumChannelParser(  # noqa: D101
    GetChannelParserBase[disnake.ForumChannel],
    is_default_for=(disnake.ForumChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.ForumChannel


class GetNewsChannelParser(  # noqa: D101
    GetChannelParserBase[disnake.NewsChannel],
    is_default_for=(disnake.NewsChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.NewsChannel


class GetVoiceChannelParser(  # noqa: D101
    GetChannelParserBase[disnake.VoiceChannel],
    is_default_for=(disnake.VoiceChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.VoiceChannel


class GetStageChannelParser(  # noqa: D101
    GetChannelParserBase[disnake.StageChannel],
    is_default_for=(disnake.StageChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.StageChannel


class GetTextChannelParser(  # noqa: D101
    GetChannelParserBase[disnake.TextChannel],
    is_default_for=(disnake.TextChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.TextChannel


class GetThreadParser(  # noqa: D101
    GetChannelParserBase[disnake.Thread],
    is_default_for=(disnake.Thread,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.Thread


class GetCategoryParser(  # noqa: D101
    GetChannelParserBase[disnake.CategoryChannel],
    is_default_for=(disnake.CategoryChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.CategoryChannel


# ASYNC ABSTRACT


class GuildChannelParser(  # noqa: D101
    ChannelParserBase[disnake.abc.GuildChannel],
    is_default_for=(disnake.abc.GuildChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.abc.GuildChannel


class PrivateChannelParser(  # noqa: D101
    ChannelParserBase[disnake.abc.PrivateChannel],
    is_default_for=(disnake.abc.PrivateChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.abc.PrivateChannel


# ASYNC PRIVATE


class DMChannelParser(  # noqa: D101
    ChannelParserBase[disnake.DMChannel],
    is_default_for=(disnake.DMChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.DMChannel


class GroupChannelParser(  # noqa: D101
    ChannelParserBase[disnake.GroupChannel],
    is_default_for=(disnake.GroupChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.GroupChannel


# ASYNC GUILD


class ForumChannelParser(  # noqa: D101
    ChannelParserBase[disnake.ForumChannel],
    is_default_for=(disnake.ForumChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.ForumChannel


class NewsChannelParser(  # noqa: D101
    ChannelParserBase[disnake.NewsChannel],
    is_default_for=(disnake.NewsChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.NewsChannel


class VoiceChannelParser(  # noqa: D101
    ChannelParserBase[disnake.VoiceChannel],
    is_default_for=(disnake.VoiceChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.VoiceChannel


class StageChannelParser(  # noqa: D101
    ChannelParserBase[disnake.StageChannel],
    is_default_for=(disnake.StageChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.StageChannel


class TextChannelParser(  # noqa: D101
    ChannelParserBase[disnake.TextChannel],
    is_default_for=(disnake.TextChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.TextChannel


class ThreadParser(  # noqa: D101
    ChannelParserBase[disnake.Thread],
    is_default_for=(disnake.Thread,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.Thread


class CategoryParser(  # noqa: D101
    ChannelParserBase[disnake.CategoryChannel],
    is_default_for=(disnake.CategoryChannel,),
):
    # <<docstring inherited from parser_api.Parser>>
    parser_type = disnake.CategoryChannel


class PartialMessageableParser(  # noqa: D101
    base.Parser[disnake.PartialMessageable],
    is_default_for=(disnake.PartialMessageable,),
):
    # <<docstring inherited from parser_api.Parser>>

    def __init__(
        self, channel_type: typing.Optional[disnake.ChannelType] = None
    ) -> None:
        self.channel_type = channel_type
        self.dumps = snowflake.snowflake_dumps

    def loads(  # noqa: D102
        self, inter: disnake.Interaction, argument: str
    ) -> disnake.PartialMessageable:
        # <<docstring inherited from parser_api.Parser>>

        return inter.bot.get_partial_messageable(int(argument), type=self.channel_type)
