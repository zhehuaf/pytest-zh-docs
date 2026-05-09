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
* 任何已捕获的先前测试输出将被处理

