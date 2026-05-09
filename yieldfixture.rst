:orphan:

.. _yieldfixture:

"yield_fixture" 函数
---------------------------------------------------------------



.. important::
    从 pytest-3.0 起，使用普通 ``fixture`` 装饰器的 fixtures 可以使用 ``yield``
    语句来提供 fixture 值并执行清理代码，就像以前版本中的 ``yield_fixture`` 一样。

    将函数标记为 ``yield_fixture`` 仍然被支持，但已弃用，不应在新代码中使用。
