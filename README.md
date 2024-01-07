![dynascope logo](docs/assets/dynascope.png)

# What is dynamic scope... in Python?

In dynamic scoping the program tries to locate the value of a variable in the call stack, moving back through the chain
of function calls until it finds or fails to find a value for the variable. This also means that as the function returns
to the caller, any values set to the dynamic variable in that function are forgotten, along with the function locals.

To compare dynamic scoping to lexical/static scoping, dynamic scoping looks at _when_ the variable assignment was
_executed_, whereas lexical/static scoping looks at _where_ the variable assignment was _defined_.

Early Python used dynamic scoping! (Maybe. *) Today's Python uses only lexical/static scoping, as demonstrated below.

![Scope demonstration]()

If you want to delve deeper into scopes in Python, there are several excellent articles on the topic, for example this
one. For a gentler introduction to the idea of dynamic scoping, check this video:
[Dynamic Scope (Theory of Python)](https://www.youtube.com/watch?v=9Ezop9_SZLo).

Generally, you do not need dynamic scoping for anything, but it might be handy when you have the right use case.

**Pros**

* Global-type scope with no need to "carry" specific variables through your function call chain.
* But with more control, as other code locations outside the current call stack cannot impact the value in surprising 
  ways.

**Cons**

* Surprises due to not understanding the call stack.
* Inability of static type checkers to accurately infer the current value. 

# What is dynascope?

## Introduction

## Quick reference

## Details

# Sample use cases

# Notes

# Related work

* [contextvars](https://docs.python.org/3/library/contextvars.html), in the standard library since Python 3.7, let you
  define variables that are close to dynamic. Some challenges with contextvars:
    * Do not support multi-level objects
    * Do not work as context managers
    * Clunky API
* As the implementation of the basic idea is relatively simple, there are several PyPI packages (and StackOverflow 
  answers) working with the idea of dynamic scoping:
  * [Dysco](https://github.com/intoli/dysco) - Emphasis on configurability, missing documentation on usage and 
    motivation.
  * [dynamicscope](https://github.com/mentalisttraceur/python-dynamicscope) - Interesting if scary approach where the
    dynamic scope reaches for values, and even deletes variables, in the callers' local scopes.
      * "... strongly recommended to only use this module for education, fun party tricks, and write-only throw-away
        code..."
  * [VarScope](https://eertmans.be/varscope/) - `with` blocks only, no support for nested values (like in a dict).
  * [block-scopes](https://github.com/cadojo/block-scopes#readme) - `with` blocks only.
  * [360blockscope](https://pypi.org/project/360blockscope/) - `with` blocks. "Just to be clear, I made this as a joke."
  * [dynamic-threadlocal](dynamic_threadlocal) - No documentation, not updated since 2011.
  * [dynscope](https://pypi.org/project/dynscope/) - `with` blocks only, not updated since 2010.
  * [innerscope](https://github.com/eriknw/innerscope) - Something almost unrelated, but interesting.