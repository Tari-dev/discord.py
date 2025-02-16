"""
The MIT License (MIT)
Copyright (c) 2015-present Rapptz
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import discord

from .errors import MissingRequiredArgument

__all__ = (
    'CustomDefault',
    'Author',
    'ReferencedMessage',
    'CurrentChannel',
    'CurrentGuild',
    'Call',
)

class CustomDefaultMeta(type):
    def __new__(cls, *args, **kwargs):
        name, bases, attrs = args
        attrs['display'] = kwargs.pop('display', name)
        return super().__new__(cls, name, bases, attrs, **kwargs)

    def __repr__(cls):
        return str(cls)

    def __str__(cls):
        return cls.display

class CustomDefault(metaclass=CustomDefaultMeta):
    """The base class of custom defaults that require the :class:`.Context`.
    Classes that derive from this should override the :attr:`~.CustomDefault.converters` attribute to specify
    converters to use and the :meth:`~.CustomDefault.default` method to do its conversion logic.
    This method must be a coroutine.
    """
    converters = (str,)

    async def default(self, ctx, param):
        """|coro|
        The method to override to do conversion logic.
        If an error is found while converting, it is recommended to
        raise a :exc:`.CommandError` derived exception as it will
        properly propagate to the error handlers.
        Parameters
        -----------
        ctx: :class:`.Context`
            The invocation context that the argument is being used in.
        """
        raise NotImplementedError('Derived classes need to implement this.')


class Author(CustomDefault):
    """Default parameter which returns the author for this context."""
    converters = (discord.Member, discord.User)

    async def default(self, ctx, param):
        return ctx.author

class ReferencedMessage(CustomDefault):
    """Default parameter which returns the referenced message for this context."""
    converters = (discord.Message,)

    async def default(self, ctx, param):
        if (message:= ctx.message.reference):
            return message.resolved
        raise MissingRequiredArgument(param)


class CurrentChannel(CustomDefault):
    """Default parameter which returns the channel for this context."""
    converters = (discord.TextChannel,)

    async def default(self, ctx, param):
        return ctx.channel

class CurrentGuild(CustomDefault):
    """Default parameter which returns the guild for this context."""

    async def default(self, ctx, param):
        if ctx.guild:
            return ctx.guild
        raise MissingRequiredArgument(param)

class Call(CustomDefault):
    """Easy wrapper for lambdas/inline defaults."""

    def __init__(self, callback):
        self._callback = callback

    async def default(self, ctx, param):
        return self._callback(ctx, param)