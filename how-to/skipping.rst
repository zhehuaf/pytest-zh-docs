.. _`skip and xfail`:

.. _skipping:

如何使用 skip 和 xfail 处理无法成功的测试
=================================================================

你可以标记在某些平台上无法运行的测试函数，或者你预期会失败的测试函数，以便 pytest 可以相应地处理它们，并在保持测试套件*绿色*的同时呈现测试会话摘要。

**skip** 意味着你期望你的测试仅在满足某些条件时通过，
否则 pytest 应该完全跳过运行该测试。常见示例包括在非 Windows 平台上跳过仅 Windows 的测试，或跳过依赖于当前不可用外部资源（例如数据库）的测试。

**xfail** 意味着你预期测试由于某种原因会失败。
一个常见的例子是针对尚未实现的功能或尚未修复的错误的测试。
当尽管预期失败（用 ``pytest.mark.xfail`` 标记）但测试通过时，
它是一个 **xpass**，将在测试摘要中报告。

``pytest`` 单独计数并列出 *skip* 和 *xfail* 测试。默认情况下不显示有关跳过/预期失败测试的详细信息，以避免
使输出混乱。你可以使用 :option:`-r` 选项查看与测试进度中显示的"短"字母对应的详细信息：

.. code-block:: bash

    pytest -rxXs  # 显示有关 xfailed、xpassed 和 skipped 测试的额外信息

有关 :option:`-r` 选项的更多详细信息，请运行 ``pytest -h``。

（参见 :ref:`how to change command line options defaults`）

.. _skipif:
.. _skip:
.. _`condition booleans`:

跳过测试函数
-----------------------


跳过测试函数的最简单方法是使用 ``skip`` 装饰器标记它，该装饰器可以传递一个可选的 ``reason``：

.. code-block:: python

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_the_unknown(): ...


或者，也可以通过在测试执行或设置期间调用 ``pytest.skip(reason)`` 函数来强制跳过：

.. code-block:: python

    def test_function():
        if not valid_config():
            pytest.skip("unsupported configuration")

当无法在导入时评估跳过条件时，强制方法非常有用。

也可以使用 ``pytest.skip(reason, allow_module_level=True)`` 在模块级别跳过整个模块：

.. code-block:: python

    import sys

    import pytest

    if not sys.platform.startswith("win"):
        pytest.skip("skipping windows-only tests", allow_module_level=True)


**参考**: :ref:`pytest.mark.skip ref`

``skipif``
~~~~~~~~~~



如果你想有条件地跳过某些内容，那么你可以使用 ``skipif``。
这里是一个示例，标记一个测试函数在 Python 版本低于 3.13 的解释器上运行时被跳过：

.. code-block:: python

    import sys


    @pytest.mark.skipif(sys.version_info < (3, 13), reason="requires python3.13 or higher")
    def test_function(): ...

如果在收集期间条件求值为 ``True``，测试函数将被跳过，
使用 ``-rs`` 时指定的理由会出现在摘要中。

你可以在模块之间共享 ``skipif`` 标记。考虑这个测试模块：

.. code-block:: python

    # test_mymodule.py 的内容
    import mymodule

    minversion = pytest.mark.skipif(
        mymodule.__versioninfo__ < (1, 1), reason="at least mymodule-1.1 required"
    )


    @minversion
    def test_function(): ...

你可以导入标记并在另一个测试模块中重用它：

.. code-block:: python

    # test_myothermodule.py
    from test_mymodule import minversion


    @minversion
    def test_anotherfunction(): ...

对于较大的测试套件，通常最好有一个文件
在其中定义标记，然后在整个测试套件中一致地应用它们。

或者，你可以使用 :ref:`条件字符串 <string conditions>` 而不是布尔值，但它们不能很容易地在模块之间共享，
因此主要为了向后兼容性而支持它们。

**参考**: :ref:`pytest.mark.skipif ref`


跳过类的所有测试函数或模块
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

你可以在任何其他标记上使用 ``skipif`` 标记（在类上）：

.. code-block:: python

    @pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
    class TestPosixCalls:
        def test_function(self):
            "will not be setup or run under 'win32' platform"

如果条件为 ``True``，此标记将为该类的每个测试方法产生跳过结果。

如果你想跳过模块的所有测试函数，你可以使用
:globalvar:`pytestmark` 全局变量：

.. code-block:: python

    # test_module.py
    pytestmark = pytest.mark.skipif(...)

如果将多个 ``skipif`` 装饰器应用于测试函数，则
如果任何跳过条件为真，它将被跳过。

.. _`whole class- or module level`: mark.html#scoped-marking


跳过文件或目录
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

有时你可能需要跳过整个文件或目录，例如，如果
测试依赖于 Python 版本特定的特性或包含你不希望 pytest 运行的代码。在这种情况下，你必须从收集中排除文件和目录。有关更多信息，请参阅 :ref:`customizing-test-collection`。


在缺少导入依赖时跳过
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

你可以通过使用 :ref:`pytest.importorskip ref` 在模块级别、测试内或测试设置函数中跳过缺少导入的测试。

.. code-block:: python

    docutils = pytest.importorskip("docutils")

如果这里无法导入 ``docutils``，这将导致测试的跳过结果。你也可以根据库的版本号跳过：

.. code-block:: python

    docutils = pytest.importorskip("docutils", minversion="0.3")

版本将从指定模块的 ``__version__`` 属性中读取。

总结
~~~~~~~

以下是关于如何在不同情况下跳过模块中的测试的快速指南：

1. 无条件跳过模块中的所有测试：

  .. code-block:: python

        pytestmark = pytest.mark.skip("all tests still WIP")

2. 基于某些条件跳过模块中的所有测试：

  .. code-block:: python

        pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="tests for linux only")

3. 如果缺少某些导入则跳过模块中的所有测试：

  .. code-block:: python

        pexpect = pytest.importorskip("pexpect")


.. _xfail:

XFail：将测试函数标记为预期失败
----------------------------------------------

你可以使用 ``xfail`` 标记来表明你
预期测试会失败：

.. code-block:: python

    @pytest.mark.xfail
    def test_function(): ...

此测试将运行，但失败时不会报告回溯。相反，终端
报告会将其列在 "expected to fail" (``XFAIL``) 或 "unexpectedly
passing" (``XPASS``) 部分。

或者，你也可以在测试或其设置函数内强制将测试标记为 ``XFAIL``：

.. code-block:: python

    def test_function():
        if not valid_config():
            pytest.xfail("failing configuration (but should work)")

.. code-block:: python

    def test_function2():
        import slow_module

        if slow_module.slow_function():
            pytest.xfail("slow_module taking too long")

这两个示例说明了你不希望在模块级别检查条件的情况，这是标记求值时的条件。

这将使 ``test_function`` ``XFAIL``。请注意，与标记不同，:func:`pytest.xfail` 调用之后不会执行其他代码。这是因为它内部通过引发已知异常来实现。

**参考**: :ref:`pytest.mark.xfail ref`


``condition`` 参数
~~~~~~~~~~~~~~~~~~~~~~~

如果测试仅在特定条件下预期失败，你可以将该条件作为第一个参数传递：

.. code-block:: python

    @pytest.mark.xfail(sys.platform == "win32", reason="bug in a 3rd party library")
    def test_function(): ...

请注意，你也必须传递理由（参见 :ref:`pytest.mark.xfail ref` 处的参数描述）。

``reason`` 参数
~~~~~~~~~~~~~~~~~~~~

你可以使用 ``reason`` 参数指定预期失败的原因：

.. code-block:: python

    @pytest.mark.xfail(reason="known parser issue")
    def test_function(): ...


``raises`` 参数
~~~~~~~~~~~~~~~~~~~~

如果你想更具体地说明测试失败的原因，可以在 ``raises`` 参数中指定单个异常或异常元组。

.. code-block:: python

    @pytest.mark.xfail(raises=RuntimeError)
    def test_function(): ...

然后，如果测试失败且异常未在 ``raises`` 中提及，则报告为常规失败。

``run`` 参数
~~~~~~~~~~~~~~~~~

如果测试应标记为 xfail 并报告为此类，但不应
执行，请将 ``run`` 参数设置为 ``False``：

.. code-block:: python

    @pytest.mark.xfail(run=False)
    def test_function(): ...

这对于那些使解释器崩溃的 xfailing 测试特别有用，应该稍后调查。

.. _`xfail strict tutorial`:

``strict`` 参数
~~~~~~~~~~~~~~~~~~~~

默认情况下，``XFAIL`` 和 ``XPASS`` 都不会使测试套件失败。
你可以通过将 ``strict`` 仅关键字参数设置为 ``True`` 来更改此设置：

.. code-block:: python

    @pytest.mark.xfail(strict=True)
    def test_function(): ...


这将使此测试的 ``XPASS`` ("unexpectedly passing") 结果导致测试套件失败。

你可以使用 ``strict_xfail`` ini 选项更改 ``strict`` 参数的默认值：

.. tab:: toml

    .. code-block:: toml

        [pytest]
        xfail_strict = true

.. tab:: ini

    .. code-block:: ini

        [pytest]
        strict_xfail = true


忽略 xfail
~~~~~~~~~~~~~~

通过在命令行上指定：

.. code-block:: bash

    pytest --runxfail

你可以强制运行和报告 ``xfail`` 标记的测试，
就像它根本没有被标记一样。这也会导致 :func:`pytest.xfail` 不产生任何效果。

示例
~~~~~~~~

这里是一个包含多种用法的简单测试文件：

.. literalinclude:: /example/xfail_demo.py

使用 report-on-xfail 选项运行它会产生以下输出：

.. FIXME: Use $ instead of ! again to re-enable regendoc once it's fixed:
   https://github.com/pytest-dev/pytest/issues/8807

.. code-block:: pytest

    ! pytest -rx xfail_demo.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-6.x.y, py-1.x.y, pluggy-1.x.y
    cachedir: $PYTHON_PREFIX/.pytest_cache
    rootdir: $REGENDOC_TMPDIR/example
    collected 7 items

    xfail_demo.py xxxxxxx                                                [100%]

    ========================= short test summary info ==========================
    XFAIL xfail_demo.py::test_hello
    XFAIL xfail_demo.py::test_hello2
      reason: [NOTRUN]
    XFAIL xfail_demo.py::test_hello3
      condition: hasattr(os, 'sep')
    XFAIL xfail_demo.py::test_hello4
      bug 110
    XFAIL xfail_demo.py::test_hello5
      condition: pytest.__version__[0] != "17"
    XFAIL xfail_demo.py::test_hello6
      reason: reason
    XFAIL xfail_demo.py::test_hello7
    ============================ 7 xfailed in 0.12s ============================

.. _`skip/xfail with parametrize`:

使用 parametrize 进行 Skip/xfail
--------------------------------

在使用 parametrize 时，可以将 skip 和 xfail 等标记应用于单个测试实例：

.. code-block:: python

    import sys

    import pytest


    @pytest.mark.parametrize(
        ("n", "expected"),
        [
            (1, 2),
            pytest.param(1, 0, marks=pytest.mark.xfail),
            pytest.param(1, 3, marks=pytest.mark.xfail(reason="some bug")),
            (2, 3),
            (3, 4),
            (4, 5),
            pytest.param(
                10, 11, marks=pytest.mark.skipif(sys.version_info >= (3, 0), reason="py2k")
            ),
        ],
    )
    def test_increment(n, expected):
        assert n + 1 == expected
