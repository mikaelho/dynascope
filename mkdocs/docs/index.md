---
hide:
  - navigation
---


![Dynascope logo](images/dynascope.png)

# Dynamic scope for Python

## What is dynamic scope?

Python is a dynamic language, but it does not have dynamic scope. If Python had it, here's what
using a dynamic `variable` could look like:

```python
variable = 1

def function():
    assert variable == 1
    variable = 2
    assert variable == 2

function()
assert variable == 1
```

With dynamic scope, the value of a variable is determined by **going up the call stack** and using
the first value found:

- At the start of the `function`, value is found by going up the stack to the caller, where
  `variable` is defined with value of `1`.
- After we have set `variable` to `2` in the function, the value is found in the local scope and no
  call stack traversal is needed.
- Then, after returning from the `function`, value `1` is again found in the local scope - we have
  effectively forgotten about any values set earlier, "down" in the call stack.

But, as said, Python does not support dynamic scope, and the Internet seems to consider it actively
harmful. It even goes against the Zen of Python, being more implicit than explicit.

> Rumor has it that early Python used dynamic scoping but then dropped it.

## What is dynamic scope good for?

The Internet would say "nothing". Certainly everything that can be done with dynamic scope could
also be accomplished by explicitly passing arguments down the call chain.

Here are some use cases that are most often mentioned by the Internet (even if grudgingly):

1. _**Dynamic configuration**_ settings that depend on the call path, for example for logging.
2. **_Resource management_**, or ensuring that a certain code path does not take too much time or
   other resources, e.g. via cancellation tokens.
3. **_Hierarchical structure building_**, e.g. creation documents or user interfaces, with an
   implicit context of the current node and style.

In all of these, we get the benefit of cleaner, aspect-oriented code, and the downside of
implicitness.

## Ignore all the good advice with `dynascope`

To explore what the use cases mentioned above look like in practice, just `pip install dynascope`
and pretend dynamic scope is real:

```python
from dynascope import scope

scope.variable = 1

def function():
  assert scope.variable == 1
  scope.variable = 2
  assert scope.variable == 2

function()
assert scope.variable == 1
```

`dynascope` also supports `with` blocks:

```python
from dynascope import scope

scope.variable = 1

with scope(variable=2):
    assert scope.variable == 2

assert scope.variable == 1
```

`with` scopes look explicit, so maybe they are more acceptable to the Internet, who knows.

`dynascope` also provides utilities that help writing code that depends on dynamic scope features:

- _**Context manager builder**_ supports creating domain-specific context managers.
- _**Transparent functions**_ let us set dynamic variable values in helper functions, without 
  immediately losing the values on returning from the function.
- _**Static pods**_ allow dynamically scoped objects to carry normal Python variables.

These will be demonstrated as we try `dynascope` on some relevant use cases.

Now, let's try implementing some dynamic scope use cases with `dynascope`.

## Dynamic configuration

#### Introduction

Choosing the logging use case, let's imagine that we have a complex codebase that has many
interlinked components, lots of looping and so on. Also, we have the code well covered with debug
logging, turned off for regular operations as the debug messages would be just so much noise.

Now, we want to see the debug from a particular function, but only if it is called from a specific
parent function, as debug information when called other ways are not relevant to you.

(For the sake of the example, assume that just firing up the debugger is not an option; the function
is a very busy one, and stepping through it would be a chore.)

#### What it looks like in action

In this example, we are interested in the debug messages from the `service_function`, but only if
the function is called via an API endpoint, not if it is called directly:

```python
import logging

from samples.dynamic_logging import dynalog
from samples.dynamic_logging import scope

logger = logging.getLogger(__name__)
dynalog(logger)  # Patch logger for dynamic filtering

logger.setLevel(logging.INFO)  # Normally not interested in debug messages

def api_endpoint():
    scope.log_level = logging.DEBUG  # Set log level for this call branch only
    service_function()

def service_function():
    logger.debug("This message is only interesting for APIs")

service_function()  # Debug message is not logged
api_endpoint()  # Debug message is logged
```

Simple, yet hard to achieve with the regular logging machinery, as far as I know.

Bonus: with dynamic scope, selective logging can be quickly added to an existing codebase, as no
changes need to be made to the actual log calls.

#### How to set it up

Here is a wrapper on a regular logger that patches the logging level checker:

```python
from dynascope import scope

def dynalog(logger):
    "Patch the regular logger to support overriding the log level for the current call branch."
    original_isEnabledFor = logger.isEnabledFor

    def dynamic_isEnabledFor(level):
        if (log_level := getattr(scope, "log_level", None)) is not None:
            return log_level <= level
        else:
            return original_isEnabledFor(level)

    setattr(logger, "isEnabledFor", dynamic_isEnabledFor)
    return logger
```

## Resource management

#### Introduction

#### What it looks like in action

#### How to set it up

## Hierarchical structures

#### Introduction

#### What they look like in action

#### How to set it up

