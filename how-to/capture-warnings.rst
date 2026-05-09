.. _`warnings`:

如何捕获警告
=======================

从 ``3.1`` 版本开始，pytest 现在自动在测试执行期间捕获警告并在会话结束时显示它们：

.. code-block:: python

    # test_show_warnings.py 的内容
    import warnings


    def api_v1():
        warnings.warn(UserWarning("api v1, should use functions from v2"))
        return 1


    def test_one():
        assert api_v1() == 1


运行 pytest 现在产生此输出：

.. code-block:: pytest

    $ pytest test_show_warnings.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 1 item

    test_show_warnings.py .                                              [100%]

    ============================= warnings summary =============================
    test_show_warnings.py::test_one
      /home/sweet/project/test_show_warnings.py:5: UserWarning: api v1, should use functions from v2
        warnings.warn(UserWarning("api v1, should use functions from v2"))

    -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
    ======================= 1 passed, 1 warning in 0.12s =======================

.. _`controlling-warnings`:

控制警告
--------------------

类似于 Python 的 `warning filter`_ 和 :option:`-W option <python:-W>` 标志，pytest 提供了自己的 ``-W`` 标志来控制哪些警告被忽略、显示或转换为错误。有关更多高级用例，请参见 `warning filter`_ 文档。

.. _`warning filter`: https://docs.python.org/3/library/warnings.html#warning-filter

此代码示例显示如何将 ``UserWarning`` 类别的任何警告视为错误：

.. code-block:: pytest

    $ pytest -q test_show_warnings.py -W error::UserWarning
    F                                                                    [100%]
    ================================= FAILURES =================================
    _________________________________ test_one _________________________________

        def test_one():
    >       assert api_v1() == 1
                   ^^^^^^^^

    test_show_warnings.py:10:
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

        def api_v1():
    >       warnings.warn(UserWarning("api v1, should use functions from v2"))
    E       UserWarning: api v1, should use functions from v2

    test_show_warnings.py:5: UserWarning
    ========================= short test summary info ==========================
    FAILED test_show_warnings.py::test_one - UserWarning: api v1, should use ...
    1 failed in 0.12s

可以使用 :confval:`filterwarnings` 配置选项在配置文件中设置相同的选项。例如，下面的配置将忽略所有用户警告和匹配正则表达式的特定弃用警告，但将所有其他警告转换为错误。

.. tab:: toml

    .. code-block:: toml

        [pytest]
        filterwarnings = [
            'error',
            'ignore::UserWarning',
            # 注意下面使用单引号在 TOML 中表示 "原始" 字符串。
            'ignore:function ham\(\) is deprecated:DeprecationWarning',
        ]

.. tab:: ini

    .. code-block:: ini

        [pytest]
        filterwarnings =
            error
            ignore::UserWarning
            ignore:function ham\(\) is deprecated:DeprecationWarning


当警告与列表中的多个选项匹配时，执行最后一个匹配选项的操作。


.. note::

    ``-W`` 标志和 :confval:`filterwarnings` 配置选项使用结构相似的警告过滤器，但每个配置选项以不同的方式解释其过滤器。例如，``filterwarnings`` 中的 *message* 是一个字符串，包含警告消息开头必须匹配的（不区分大小写的）正则表达式，而 ``-W`` 中的 *message* 是警告消息开头必须包含的（不区分大小写的）字面字符串，忽略消息开头或结尾的任何空白。有关更多详细信息，请参阅 `warning filter`_ 文档。


.. _`filterwarnings`:

``@pytest.mark.filterwarnings``
-------------------------------

你可以使用 :ref:`@pytest.mark.filterwarnings <pytest.mark.filterwarnings ref>` 标记向特定测试项添加警告过滤器，允许你对哪些警告应在测试、类甚至模块级别捕获进行更精细的控制：

.. code-block:: python

    import warnings


    def api_v1():
        warnings.warn(UserWarning("api v1, should use functions from v2"))
        return 1


    @pytest.mark.filterwarnings("ignore:api v1")
    def test_one():
        assert api_v1() == 1


你可以用单独的修饰器指定多个过滤器：

.. code-block:: python

    # 忽略 "api v1" 警告，但对所有其他警告失败
    @pytest.mark.filterwarnings("ignore:api v1")
    @pytest.mark.filterwarnings("error")
    def test_one():
        assert api_v1() == 1


你也可以通过提供多个参数将多个过滤器传递给单个标记：

.. code-block:: python

    # 后面的参数优先，符合 warnings.filterwarnings 的行为。
    @pytest.mark.filterwarnings("error", "ignore:api v1")
    def test_one():
        assert api_v1() == 1


.. important::

    关于修饰器顺序和过滤器优先级：
    重要的是要记住，修饰器是按相反顺序评估的，
    所以你必须按与 :py:func:`warnings.filterwarnings` 和 :option:`-W option <python:-W>` 的传统用法相反的顺序列出警告过滤器。
    这意味着实践中来自前面 :ref:`@pytest.mark.filterwarnings <pytest.mark.filterwarnings ref>` 修饰器的过滤器优先于后面修饰器的过滤器，如上面的示例所示。


使用标记应用的过滤器优先于在命令行上传递或通过 :confval:`filterwarnings` 配置选项配置的过滤器。

你可以通过使用 :ref:`filterwarnings <pytest.mark.filterwarnings ref>` 标记作为类修饰器将过滤器应用于类的所有测试，或通过设置 :globalvar:`pytestmark` 变量将过滤器应用于模块中的所有测试：

.. code-block:: python

    # 将此模块的所有警告转换为错误
    pytestmark = pytest.mark.filterwarnings("error")


.. note::

    如果你想应用多个过滤器
    （通过将 :ref:`filterwarnings <pytest.mark.filterwarnings ref>` 标记列表分配给 :globalvar:`pytestmark`），
    你必须使用传统的 :py:func:`warnings.filterwarnings` 排序方法（后面的过滤器优先），
    这与上面提到的修饰器方法相反。


*感谢 Florian Schulze 在* `pytest-warnings`_ *插件中提供的参考实现。*

.. _`pytest-warnings`: https://github.com/fschulze/pytest-warnings

禁用警告摘要
--------------------------

虽然不推荐，但你可以使用 :option:`--disable-warnings` 命令行选项完全抑制测试运行输出中的警告摘要。

完全禁用警告捕获
----------------------------------

此插件默认启用，但可以在配置文件中完全禁用：

.. tab:: toml

    .. code-block:: toml

        [pytest]
        addopts = ["-p", "no:warnings"]

.. tab:: ini

    .. code-block:: ini

        [pytest]
        addopts = -p no:warnings


或在命令行上传递 ``-p no:warnings``。如果你的测试套件使用外部系统处理警告，这可能很有用。


.. _`deprecation-warnings`:

DeprecationWarning 和 PendingDeprecationWarning
------------------------------------------------

默认情况下，pytest 将显示来自用户代码和第三方库的 ``DeprecationWarning`` 和 ``PendingDeprecationWarning`` 警告，如 :pep:`565` 所推荐。
这有助于用户保持代码现代化，并避免在弃用警告被实际删除时出现中断。

但是，在用户在其测试中捕获任何类型的警告的特定情况下，使用 :func:`pytest.warns`、:func:`pytest.deprecated_call` 或 :fixture:`recwarn` fixture，
不会显示任何警告。

有时隐藏发生在无法控制的代码中（如第三方库）的一些特定弃用警告是有用的，在这种情况下，你可以使用警告过滤器选项（配置或标记）来忽略这些警告。

例如：

.. tab:: toml

    .. code-block:: toml

        [pytest]
        filterwarnings = [
            'ignore:.*U.*mode is deprecated:DeprecationWarning',
        ]

.. tab:: ini

    .. code-block:: ini

        [pytest]
        filterwarnings =
            ignore:.*U.*mode is deprecated:DeprecationWarning


这将忽略消息开头匹配正则表达式 ``".*U.*mode is deprecated"`` 的所有 ``DeprecationWarning`` 类型警告。

更多示例请参见 :ref:`@pytest.mark.filterwarnings <filterwarnings>` 和
:ref:`控制警告 <controlling-warnings>`。

.. note::

    如果在解释器级别配置警告，使用
    :envvar:`python:PYTHONWARNINGS` 环境变量或
    ``-W`` 命令行选项，pytest 默认不会配置任何过滤器。

    此外，pytest 不遵循 :pep:`565` 重置所有警告过滤器的建议，因为
    这可能会破坏通过调用 :func:`warnings.simplefilter` 自行配置警告过滤器的测试套件
    （参见 :issue:`2430` 获取示例）。


.. _`ensuring a function triggers a deprecation warning`:

.. _ensuring_function_triggers:

确保代码触发弃用警告
--------------------------------------------

你也可以使用 :func:`pytest.deprecated_call` 来检查某个函数调用是否触发 ``DeprecationWarning``、``PendingDeprecationWarning`` 或 ``FutureWarning``：

.. code-block:: python

    import pytest


    def test_myfunction_deprecated():
        with pytest.deprecated_call():
            myfunction(17)

如果调用 ``myfunction`` 时没有发出弃用警告，此测试将失败。





.. _`asserting warnings`:

.. _assertwarnings:

.. _`asserting warnings with the warns function`:

.. _warns:

使用 warns 函数断言警告
------------------------------------------

你可以使用 :func:`pytest.warns` 检查代码是否引发特定警告，它的工作方式类似于 :ref:`raises <assertraises>`（不同之处在于 :ref:`raises <assertraises>` 不捕获所有异常，只捕获 ``expected_exception``）：

.. code-block:: python

    import warnings

    import pytest


    def test_warning():
        with pytest.warns(UserWarning):
            warnings.warn("my warning", UserWarning)

如果未引发所讨论的警告，测试将失败。使用关键字参数 ``match`` 来断言警告与文本或正则表达式匹配。
要匹配可能包含正则表达式元字符如 ``(`` 或 ``.`` 的字面字符串，可以使用 ``re.escape`` 转义模式。

一些示例：

.. code-block:: pycon


    >>> with warns(UserWarning, match="must be 0 or None"):
    ...     warnings.warn("value must be 0 or None", UserWarning)
    ...

    >>> with warns(UserWarning, match=r"must be \d+$"):
    ...     warnings.warn("value must be 42", UserWarning)
    ...

    >>> with warns(UserWarning, match=r"must be \d+$"):
    ...     warnings.warn("this is not here", UserWarning)
    ...
    Traceback (most recent call last):
      ...
    Failed: Regex pattern did not match any of the 1 warnings emitted.
     Regex: ...
     Emitted warnings: ...UserWarning...

    >>> with warns(UserWarning, match=re.escape("issue with foo() func")):
    ...     warnings.warn("issue with foo() func")
    ...

该函数还返回所有引发警告的列表（作为 ``warnings.WarningMessage`` 对象），你可以查询以获取额外信息：

.. code-block:: python

    with pytest.warns(RuntimeWarning) as record:
        warnings.warn("another warning", RuntimeWarning)

    # 检查只引发了一个警告
    assert len(record) == 1
    # 检查消息是否匹配
    assert record[0].message.args[0] == "another warning"

或者，你可以使用 :fixture:`recwarn` fixture 详细检查引发的警告（参见 :ref:`下方 <recwarn>`）。


:fixture:`recwarn` fixture 自动确保在测试结束时重置警告过滤器，因此不会泄漏全局状态。

.. _`recording warnings`:

.. _recwarn:

记录警告
------------------

你可以使用 :func:`pytest.warns` 上下文管理器或 :fixture:`recwarn` fixture 记录引发的警告。

要使用 :func:`pytest.warns` 记录而不对警告断言任何内容，
不要将参数作为预期警告类型传递，它将默认为通用 Warning：

.. code-block:: python

    with pytest.warns() as record:
        warnings.warn("user", UserWarning)
        warnings.warn("runtime", RuntimeWarning)

    assert len(record) == 2
    assert str(record[0].message) == "user"
    assert str(record[1].message) == "runtime"

:fixture:`recwarn` fixture 将为整个函数记录警告：

.. code-block:: python

    import warnings


    def test_hello(recwarn):
        warnings.warn("hello", UserWarning)
        assert len(recwarn) == 1
        w = recwarn.pop(UserWarning)
        assert issubclass(w.category, UserWarning)
        assert str(w.message) == "hello"
        assert w.filename
        assert w.lineno

:fixture:`recwarn` fixture 和 :func:`pytest.warns` 上下文管理器都返回相同的记录警告接口：一个 :class:`~_pytest.recwarn.WarningsRecorder` 实例。要查看记录的警告，你可以
迭代此实例，在其上调用 ``len`` 以获取记录的警告数量，或索引它以获取特定的记录警告。


.. _`warns use cases`:

测试中警告的附加用例
-----------------------------------------

以下是测试中经常出现的涉及警告的一些用例，以及如何处理它们的建议：

- 确保至少发出一个指定的警告：

.. code-block:: python

    def test_warning():
        with pytest.warns((RuntimeWarning, UserWarning)):
            ...

- 确保**只**发出某些警告：

.. code-block:: python

    def test_warning(recwarn):
        ...
        assert len(recwarn) == 1
        user_warning = recwarn.pop(UserWarning)
        assert issubclass(user_warning.category, UserWarning)

-  确保**没有**发出警告：

.. code-block:: python

    def test_warning():
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            ...

- 要抑制警告：

.. code-block:: python

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ...


.. _custom_failure_messages:

自定义失败消息
-----------------------

记录警告提供了一个机会，用于在何时没有发出警告或其他条件满足时产生自定义测试失败消息。

.. code-block:: python

    def test():
        with pytest.warns(Warning) as record:
            f()
            if not record:
                pytest.fail("Expected a warning!")

如果调用 ``f`` 时没有发出警告，则 ``not record`` 将求值为 ``True``。然后你可以调用 :func:`pytest.fail` 并使用自定义错误消息。

.. _internal-warnings:

内部 pytest 警告
------------------------

pytest 在某些情况下可能会生成自己的警告，例如使用不当或弃用功能。

例如，如果 pytest 遇到一个匹配 :confval:`python_classes` 但也定义了 ``__init__`` 构造函数的类，它会发出警告，因为这会阻止该类被实例化：

.. code-block:: python

    # test_pytest_warnings.py 的内容
    class Test:
        def __init__(self):
            pass

        def test_foo(self):
            assert 1 == 1

.. code-block:: pytest

    $ pytest test_pytest_warnings.py -q

    ============================= warnings summary =============================
    test_pytest_warnings.py:1
      /home/sweet/project/test_pytest_warnings.py:1: PytestCollectionWarning: cannot collect test class 'Test' because it has a __init__ constructor (from: test_pytest_warnings.py)
        class Test:

    -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
    1 warning in 0.12s

可以使用用于过滤其他类型警告的相同内置机制来过滤这些警告。

请阅读我们的 :ref:`backwards-compatibility` 以了解我们如何处理弃用并最终删除功能。

完整警告列表列在 :ref:`参考文档 <warnings ref>` 中。


.. _`resource-warnings`:

资源警告
-----------------

如果启用了 :mod:`tracemalloc` 模块，当 pytest 捕获 :class:`ResourceWarning` 时，可以获得有关其来源的附加信息。

在运行测试时启用 :mod:`tracemalloc` 的一种方便方法是将 :envvar:`PYTHONTRACEMALLOC` 设置为足够大的帧数（比如 ``20``，但该数字取决于应用程序）。

有关更多信息，请参阅 Python 文档中的 `Python Development Mode <https://docs.python.org/3/library/devmode.html>`__ 部分。
