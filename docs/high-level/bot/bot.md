# Bot

Инстанс бота это аддон состоящий из стандартного апи и составляющих фреймворка, так же он умеет запускать лонгпол

Атрибуты:

`bot.api` - [API документация](../../low-level/api/api.md)
`bot.router` - [Router документация](../../high-level/routing/index.md)
`bot.labeler`/`bot.on` - [Labeler документация](labeler.md)
`bot.polling` - [Polling документация](../../low-level/polling/polling.md)
`bot.loop_wrapper` - [Loop Wrapper документация](../../tools/loop-wrapper.md)
`bot.loop` - возвращает _event loop_ который был установлен или самостоятельно получает его
`bot.error` - возвращает `error handler` бота из `bot.router`. Добавлено для краткой записи

Функции:

## bot.run_polling()

Асинхронный запуск longpoll

## bot.run_forever()

Синхронный запуск longpoll. Добавляет `run_polling` в таски `bot.loop_wrapper` и запускает луп в `run_forever`
