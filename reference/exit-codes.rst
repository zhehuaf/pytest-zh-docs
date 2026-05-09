.. _exit-codes:

退出代码
========================================================

运行 ``pytest`` 可以产生六种不同的退出代码：

:退出代码 0: 所有测试都已收集并成功通过
:退出代码 1: 测试已收集并运行，但有些测试失败
:退出代码 2: 测试执行被用户中断
:退出代码 3: 执行测试时发生内部错误
:退出代码 4: pytest 命令行使用错误
:退出代码 5: 没有收集到测试

它们由 :class:`pytest.ExitCode` 枚举表示。退出代码作为公共 API 的一部分，可以直接导入和访问：

.. code-block:: python

    from pytest import ExitCode

.. note::

    如果你想在某些场景下自定义退出代码，特别是当没有收集到测试时，考虑使用
    `pytest-custom_exit_code <https://github.com/yashtodi94/pytest-custom_exit_code>`__
    插件。

