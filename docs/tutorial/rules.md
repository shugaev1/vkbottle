# Правила

Для того чтобы хендлер ловил только нужные сообщения/другие ивенты нужны правила (rules, рулзы - устоявшаяся транслитерация в комьюнити вкботла), в вкботле существует множество рулзов прямо из коробки, но в большинстве своем они подходят только для одного ивента - ивента сообщений

Чтобы получить доступ к правилам из коробки вы можете поступить по-разному:

1. Импортировать их из `vkbottle.dispatch.rules` и использовать, инициализируя прямо в декораторе или в любой другой части кода:
    ```python
    from vkbottle.dispatch.rules.base import CommandRule
    from typing import Tuple

    @bot.on.message(CommandRule("say", ["!", "/"], 1))
    async def say_handler(message: Message, args: Tuple[str]):
        await message.answer(f"<<{args[0]}>>")
    ```

2. Использовать автораспаковщики рулзов из коробки, список с названиями можно найти [здесь](https://github.com/vkbottle/vkbottle/blob/master/vkbottle/framework/bot/labeler/default.py#L34), в этом случае некоторые второстепенные параметры контролировать будет нельзя
    ```python
    @bot.on.message(command=("say", 1))
    async def say_handler(message: Message, args: Tuple[str]):
        await message.answer(f"<<{args[0]}>>")
    ```

Правил может быть любое количество, как первого, так и второго метода распаковки

## Создание собственных правил

> Правило - это класс соответствующий интерфейсу `ABCRule`, который должен реализовать лишь один асинхронный метод `check`, принимающий ивент и возвращающий `False` если проверка пройдена не была и `True` либо словарь с аргументами, которые будут распакованы в хендлер как непозиционные аргументы

### Создание правил напрямую

Чтобы создать правила импортируем `ABCRule` и имплементируем асинхронный метод `check`, еще стоит импортировать `Union` из `typing` для типизации вашего кода:

```python
from typing import Union
from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule

class MyRule(ABCRule[Message]):
    async def check(self, event: Message) -> Union[dict, bool]:
        ...
```

Теперь стоит имплементировать логику правила `MyRule`, пусть оно будет просто проверять что длина сообщения меньше ста символов:

```python
return len(message.text) < 100
```

Вот что получилось:

> Union в данном правиле не понадобился поэтому его допустимо опустить по стандартам mypy, в любом случае на сигнатуру это не повлияет

```python
from typing import Union
from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule

class MyRule(ABCRule[Message]):
    async def check(self, event: Message) -> bool:
        return len(event.text) < 100
```

Теперь правило можно использовать как первым способом:

```python
@bot.on.message(MyRule())
```

Вторым способом рулзом `MyRule` в текущем состоянии воспользоваться не получится, из-за отсутствия каких-либо параметров правила, предлагается его кастомизировать с помощью метода `__init__`:

```python
# Новый вид правила
class MyRule(ABCRule[Message]):
    def __init__(self, lt: int = 100):
        self.lt = lt

    async def check(self, event: Message) -> bool:
        return len(event.text) < self.lt
```

Теперь, если предварительно (до объявления хендлеров) зарегистрировать правило в локальный лейблер

```python
bot.labeler.custom_rules["my_rule"] = MyRule
```

Его можно будет использовать и вторым способом:

```python
@bot.on.message(my_rule=50)
```

### Создание правил через правила-врапперы

> Есть так называемые правила-врапперы, правила - которые исполняют какой-то код который получают как параметры

К правилам-врапперам из коробки можно отнести: `func`, шорткат `FuncRule`; `coro` или `coroutine`, шорткат `CoroutineRule`

`FuncRule` принимает в качестве аргумента функцию (которая может быть лямбдой). Созданное напрямую правило `MyRule` можно заменить вот так:

```python
@bot.on.message(func=lambda message: len(message.text) < 100)
```

`FuncRule` принимает корутину.

> Еще существуют правила, которые совмещают несколько правил. В vkbottle [существует](https://github.com/vkbottle/vkbottle/blob/master/vkbottle/tools/dev_tools/utils.py#L26) автоматическая распаковка и трансформация некоторых инстансов в такие правила (стоит заметить что рекурсивно это не работает), а именно:
> * `Rule1() & Rule2()` конвертируется в `AndRule`
> * `Rule1() | Rule2()` конвертируется в `OrRule`
> * `~Rule2()` конвертируется в `NotRule`
>
> Вместо `OrRule` можно использовать несколько хендлеров:
> ```python
> @bot.on.message(some_rule=1)
> @bot.on.message(some_rule=100)
> ```
> Еще стоит заметить, что многие правила принимают в качестве аргумента итерабельный элемент для того чтобы самим имплементировать фильтр, как например `VBMLRule`, стоящий за `text`


## Экзамплы по этой части туториала

* [labeler-setup](https://github.com/vkbottle/vkbottle/tree/master/examples/high-level/labeler_setup.py)
* [rules-shortcuts](https://github.com/vkbottle/vkbottle/tree/master/examples/high-level/rules_shortcuts.py)
