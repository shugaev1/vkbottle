from asyncio import AbstractEventLoop, get_event_loop
from typing import TYPE_CHECKING, NoReturn, Optional, Union

from vkbottle.api import API
from vkbottle.dispatch import BuiltinStateDispenser, Router
from vkbottle.exception_factory import ErrorHandler
from vkbottle.framework.abc import ABCFramework
from vkbottle.framework.labeler import BotLabeler
from vkbottle.modules import logger
from vkbottle.polling import BotPolling
from vkbottle.tools import LoopWrapper

if TYPE_CHECKING:
    from vkbottle.api import ABCAPI, Token
    from vkbottle.dispatch import ABCRouter, ABCStateDispenser
    from vkbottle.exception_factory import ABCErrorHandler
    from vkbottle.framework.labeler import ABCLabeler
    from vkbottle.polling import ABCPolling


class Bot(ABCFramework):
    def __init__(
        self,
        token: Optional["Token"] = None,
        api: Optional["ABCAPI"] = None,
        polling: Optional["ABCPolling"] = None,
        loop: Optional[AbstractEventLoop] = None,
        loop_wrapper: Optional[LoopWrapper] = None,
        router: Optional["ABCRouter"] = None,
        labeler: Optional["ABCLabeler"] = None,
        state_dispenser: Optional["ABCStateDispenser"] = None,
        error_handler: Optional["ABCErrorHandler"] = None,
        task_each_event: bool = True,
    ):
        self.api: Union["ABCAPI", API] = API(token) if token is not None else api  # type: ignore
        self.error_handler = error_handler or ErrorHandler()
        self.loop_wrapper = loop_wrapper or LoopWrapper()
        self.labeler = labeler or BotLabeler()
        self.state_dispenser = state_dispenser or BuiltinStateDispenser()
        self._polling = polling or BotPolling(self.api)
        self._router = router or Router()
        self._loop = loop
        self.task_each_event = task_each_event

    @property
    def polling(self) -> "ABCPolling":
        return self._polling.construct(self.api, self.error_handler)

    @property
    def router(self) -> "ABCRouter":
        return self._router.construct(
            views=self.labeler.views(),
            state_dispenser=self.state_dispenser,
            error_handler=self.error_handler,
        )

    @router.setter
    def router(self, new_router: "ABCRouter"):
        self._router = new_router

    @property
    def on(self) -> "ABCLabeler":
        return self.labeler

    async def run_polling(self, custom_polling: Optional["ABCPolling"] = None) -> NoReturn:
        polling = custom_polling or self.polling
        logger.info(f"Starting polling for {polling.api!r}")

        async for event in polling.listen():  # type: ignore
            logger.debug(f"New event was received: {event}")
            for update in event["updates"]:
                if not self.task_each_event:
                    await self.router.route(update, polling.api)
                else:
                    self.loop.create_task(self.router.route(update, polling.api))

    def run_forever(self) -> NoReturn:
        logger.info("Loop will be ran forever")
        self.loop_wrapper.add_task(self.run_polling())
        self.loop_wrapper.run_forever(self.loop)

    @property
    def loop(self) -> AbstractEventLoop:
        if self._loop is None:
            self._loop = get_event_loop()
        return self._loop

    @loop.setter
    def loop(self, new_loop: AbstractEventLoop):
        self._loop = new_loop
