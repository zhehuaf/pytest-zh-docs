
.. _usage:

如何调用 pytest
==========================================

..  seealso:: :ref:`完整的 pytest 命令行标志参考 <command-line-flags>`

通常，pytest 使用命令 ``pytest`` 调用（参见下面的 :ref:`其他调用 pytest 的方式 <invoke-other>`）。这将执行当前目录及其子目录中所有文件名符合 ``test_*.py`` 或 ``*_test.py`` 形式的所有测试。更一般地说，pytest 遵循 :ref:`标准测试发现规则 <test discovery>`。


.. _select-tests:

指定要运行哪些测试
------------------------------

Pytest 支持多种从命令行或文件运行和选择测试的方式（参见下面的 :ref:`从文件读取参数 <args-from-file>`）。

**在模块中运行测试**

.. code-block:: bash

    pytest test_mod.py

**在目录中运行测试**

.. code-block:: bash

    pytest testing/

**按关键字表达式运行测试**

.. code-block:: bash

    pytest -k 'MyClass and not method'

这将运行包含与给定*字符串表达式*（不区分大小写）匹配的名称的测试，该表达式可以包括使用文件名、类名和函数名作为变量的 Python 运算符。上面的示例将运行 ``TestMyClass.test_something``，但不运行 ``TestMyClass.test_method_simple``。在 Windows 上运行时，在表达式中使用 ``""`` 代替 ``''``。

.. _nodeids:

**按收集参数运行测试**

传递相对于工作目录的模块文件名，后跟说明符，如类名和函数名，用 ``::`` 字符分隔，以及参数化中括在 ``[]`` 中的参数。

要在模块中运行特定测试：

.. code-block:: bash

    pytest tests/test_mod.py::test_func

要运行类中的所有测试：

.. code-block:: bash

    pytest tests/test_mod.py::TestClass

指定特定测试方法：

.. code-block:: bash

    pytest tests/test_mod.py::TestClass::test_method

指定测试的特定参数化：

.. code-block:: bash

    pytest tests/test_mod.py::test_func[x1,y2]

**按标记表达式运行测试**

要运行所有用 ``@pytest.mark.slow`` 装饰器装饰的测试：

.. code-block:: bash

    pytest -m slow


要运行所有用带注解的 ``@pytest.mark.slow(phase=1)`` 装饰器装饰的测试，且 ``phase`` 关键字参数设置为 ``1``：

.. code-block:: bash

    pytest -m "slow(phase=1)"

更多信息请参见 :ref:`标记 <mark>`。

**从包运行测试**

.. code-block:: bash

    pytest --pyargs pkg.testing

这将导入 ``pkg.testing`` 并使用其文件系统位置来查找和运行测试。

.. _args-from-file:

**从文件读取参数**

.. versionadded:: 8.2

以上所有内容都可以使用 ``@`` 前缀从文件读取：

.. code-block:: bash

    pytest @tests_to_run.txt

其中 ``tests_to_run.txt`` 每行包含一个条目，例如：

.. code-block:: text

    tests/test_file.py
    tests/test_mod.py::test_func[x1,y2]
    tests/test_mod.py::TestClass
    -m slow

此文件也可以使用 ``pytest --collect-only -q`` 生成，并根据需要进行修改。

获取关于版本、选项名称、环境变量的帮助
--------------------------------------------------------------

.. code-block:: bash

    pytest --version   # 显示 pytest 从何处导入
    pytest --fixtures  # 显示可用的内置函数参数
    pytest -h | --help # 显示命令行和配置文件选项的帮助


.. _durations:

分析测试执行持续时间
-------------------------------------

.. versionchanged:: 6.0

要获取超过 1.0 秒的最慢的 10 个测试持续时间列表：

.. code-block:: bash

    pytest --durations=10 --durations-min=1.0

默认情况下，pytest 不会显示太小的测试持续时间（<0.005 秒），除非在命令行上传递 ``-vv``。


管理插件加载
-------------------------------

提前加载插件
~~~~~~~~~~~~~~~~~~~~~~~

你可以使用 :option:`-p` 选项在命令行中显式提前加载插件（内部和外部）::

    pytest -p mypluginmodule

该选项接收一个 ``name`` 参数，可以是：

* 完整的模块点分名称，例如 ``myproject.plugins``。此点分名称必须可导入。
* 插件的入口点名称。这是插件注册时传递给 ``importlib`` 的名称。例如，要提前加载 :pypi:`pytest-cov` 插件，你可以使用::

    pytest -p pytest_cov


禁用插件
~~~~~~~~~~~~~~~~~~

要在调用时禁用加载特定插件，请使用 :option:`-p` 选项，并加上前缀 ``no:``。

示例：要禁用加载负责从文本文件执行 doctest 测试的插件 ``doctest``，请像这样调用 pytest：

.. code-block:: bash

    pytest -p no:doctest


.. _invoke-other:

调用 pytest 的其他方式
-----------------------------------------------------

.. _invoke-python:

通过 ``python -m pytest`` 调用 pytest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

你可以通过命令行从 Python 解释器调用测试：

.. code-block:: text

    python -m pytest [...]

这几乎等同于直接调用命令行脚本 ``pytest [...]``，除了通过 ``python`` 调用还会将当前目录添加到 ``sys.path``。


.. _`pytest.main-usage`:

从 Python 代码调用 pytest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

你可以直接从 Python 代码调用 ``pytest``：

.. code-block:: python

    retcode = pytest.main()

这相当于你从命令行调用 "pytest"。
它不会引发 :class:`SystemExit`，而是返回 :ref:`退出代码 <exit-codes>`。
如果你不给它传递任何参数，``main`` 会从进程的命令行参数中读取参数 (:data:`sys.argv`)，这可能是不希望的。
你可以显式传递选项和参数：

.. code-block:: python

    retcode = pytest.main(["-x", "mytestdir"])

你可以向 ``pytest.main`` 指定额外的插件：

.. code-block:: python

    # myinvoke.py 的内容
    import sys

    import pytest


    class MyPlugin:
        def pytest_sessionfinish(self):
            print("*** 测试运行报告完成")


    if __name__ == "__main__":
        sys.exit(pytest.main(["-qq"], plugins=[MyPlugin()]))

运行它将显示 ``MyPlugin`` 已被添加，并且其 hook 被调用：

.. code-block:: pytest

    $ python myinvoke.py
    *** 测试运行报告完成


.. note::

    调用 ``pytest.main()`` 将导致导入你的测试和它们导入的任何模块。由于 Python 导入系统的缓存机制，从同一进程对 ``pytest.main()`` 进行后续调用将不会反映这些文件在调用之间的更改。因此，不推荐从同一进程对 ``pytest.main()`` 进行多次调用（例如，为了重新运行测试）。

