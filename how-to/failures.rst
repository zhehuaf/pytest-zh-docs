.. _how-to-handle-failures:

如何处理测试失败
=============================

.. _maxfail:

在第一次（或第 N 次）失败后停止
---------------------------------------------------

要在第一次（N）失败后停止测试过程：

.. code-block:: bash

    pytest -x           # 第一次失败后停止
    pytest --maxfail=2  # 两次失败后停止


.. _pdb-option:

在 pytest 中使用 :doc:`python:library/pdb`
-------------------------------------------

在失败时进入 :doc:`pdb <python:library/pdb>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python 带有一个内置的 Python 调试器 :doc:`pdb <python:library/pdb>`。``pytest``
允许通过命令行选项进入 :doc:`pdb <python:library/pdb>` 提示符：

.. code-block:: bash

    pytest --pdb

这将在每次失败（或 KeyboardInterrupt）时调用 Python 调试器。
通常你可能只想对第一个失败的测试这样做以了解
某些失败情况：

.. code-block:: bash

    pytest -x --pdb   # 第一次失败时进入 PDB，然后结束测试会话
    pytest --pdb --maxfail=3  # 前三次失败时进入 PDB

请注意，在任何失败时，异常信息都存储在
``sys.last_value``、``sys.last_type`` 和 ``sys.last_traceback`` 中。在
交互式使用中，这允许使用任何调试工具进入事后调试。
也可以手动访问异常信息，
例如::

    >>> import sys
    >>> sys.last_traceback.tb_lineno
    42
    >>> sys.last_value
    AssertionError('assert result == "ok"',)


.. _trace-option:

在测试开始时进入 :doc:`pdb <python:library/pdb>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``pytest`` 允许通过命令行选项在每个测试开始时立即进入 :doc:`pdb <python:library/pdb>` 提示符：

.. code-block:: bash

    pytest --trace

这将在每个测试开始时调用 Python 调试器。

.. _breakpoints:

设置断点
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded: 2.4.0

要在代码中设置断点，请在代码中使用原生 Python ``import pdb;pdb.set_trace()`` 调用，pytest 会自动禁用该测试的输出捕获：

* 其他测试中的输出捕获不受影响。
* 任何已捕获的先前测试输出将被照常处理。
* 当结束调试器会话时（通过 ``continue`` 命令），输出捕获恢复。


.. _`breakpoint-builtin`:

使用内置的 breakpoint 函数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python 3.7 引入了内置的 ``breakpoint()`` 函数。
Pytest 支持使用 ``breakpoint()``，具有以下行为：

 - 当调用 ``breakpoint()`` 且 ``PYTHONBREAKPOINT`` 设置为默认值时，pytest 将使用自定义的内部 PDB 跟踪 UI 而不是系统默认的 ``Pdb``。
 - 测试完成后，系统将默认恢复为系统的 ``Pdb`` 跟踪 UI。
 - 当向 pytest 传递 :option:`--pdb` 时，自定义的内部 Pdb 跟踪 UI 用于 ``breakpoint()`` 以及失败的测试/未处理的异常。
 - :option:`--pdbcls` 可用于指定自定义调试器类。


.. _faulthandler:

Fault Handler
-------------

.. versionadded:: 5.0

:mod:`faulthandler` 标准模块可用于在段错误或超时后转储 Python 回溯。

除非在命令行上给出 ``-p no:faulthandler``，否则该模块会在 pytest 运行时自动启用。

此外，可以使用 :confval:`faulthandler_timeout=X<faulthandler_timeout>` 配置选项，如果测试完成时间超过 ``X`` 秒，则转储所有线程的回溯。

.. note::

    此功能已从外部 `pytest-faulthandler <https://github.com/pytest-dev/pytest-faulthandler>`__ 插件集成，有两个小差异：

    * 要禁用它，使用 ``-p no:faulthandler`` 而不是 ``--no-faulthandler``：前者可用于任何插件，因此节省了一个选项。

    * ``--faulthandler-timeout`` 命令行选项已变为 :confval:`faulthandler_timeout` 配置选项。仍然可以使用 ``-o faulthandler_timeout=X`` 从命令行进行配置。


.. _unraisable:

警告关于不可引发的异常和未处理的线程异常
-------------------------------------------------------------------

.. versionadded:: 6.2

未处理的异常是在无法传播给调用者的情况下引发的异常。最常见的情况是在 :meth:`__del__ <object.__del__>` 实现中引发的异常。

未处理的线程异常是在 :class:`~threading.Thread` 中引发但未被处理的异常，导致线程不干净地终止。

这两种类型的异常通常被认为是 bug，但由于它们不会导致程序本身崩溃，可能会被忽视。Pytest 检测这些情况并发出一则警告，该警告在测试运行摘要中可见。

除非在命令行上给出 ``-p no:unraisableexception``（用于不可引发的异常）和 ``-p no:threadexception``（用于线程异常）选项，否则这些插件会在 pytest 运行时自动启用。

可以使用 :ref:`pytest.mark.filterwarnings ref` 标记选择性地静默这些警告。警告类别是 :class:`pytest.PytestUnraisableExceptionWarning` 和 :class:`pytest.PytestUnhandledThreadExceptionWarning`。

