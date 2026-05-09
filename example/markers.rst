
.. _`mark examples`:

使用自定义标记器
=================================================

以下是一些使用 :ref:`mark` 机制的示例。

.. _`mark run`:

标记测试函数并选择它们进行运行
----------------------------------------------------

你可以像这样用自定义元数据"标记"测试函数：

.. code-block:: python

    # test_server.py 的内容

    import pytest


    @pytest.mark.webtest
    def test_send_http():
        pass  # 为你的应用执行一些 webtest 测试


    @pytest.mark.device(serial="123")
    def test_something_quick():
        pass


    @pytest.mark.device(serial="abc")
    def test_another():
        pass


    class TestClass:
        def test_method(self):
            pass



然后你可以限制测试运行仅运行标记为 ``webtest`` 的测试：

.. code-block:: pytest

    $ pytest -v -m webtest
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y -- $PYTHON_PREFIX/bin/python
    cachedir: .pytest_cache
    rootdir: /home/sweet/project
    collecting ... collected 4 items / 3 deselected / 1 selected

    test_server.py::test_send_http PASSED                                [100%]

    ===================== 1 passed, 3 deselected in 0.12s ======================

或者相反，运行除了 webtest 之外的所有测试：

.. code-block:: pytest

    $ pytest -v -m "not webtest"
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y -- $PYTHON_PREFIX/bin/python
    cachedir: .pytest_cache
    rootdir: /home/sweet/project
    collecting ... collected 4 items / 1 deselected / 3 selected

    test_server.py::test_something_quick PASSED                          [ 33%]
    test_server.py::test_another PASSED                                  [ 66%]
    test_server.py::TestClass::test_method PASSED                        [100%]

    ===================== 3 passed, 1 deselected in 0.12s ======================

.. _`marker_keyword_expression_example`:

此外，你可以将测试运行限制为仅运行匹配一个或多个标记器关键字的测试，
例如仅运行标记为 ``device`` 且特定 ``serial="123"`` 的测试：

.. code-block:: pytest

    $ pytest -v -m "device(serial='123')"
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y -- $PYTHON_PREFIX/bin/python
    cachedir: .pytest_cache
    rootdir: /home/sweet/project
    collecting ... collected 4 items / 3 deselected / 1 selected

    test_server.py::test_something_quick PASSED                          [100%]

    ===================== 1 passed, 3 deselected in 0.12s ======================

.. note:: 标记器表达式中仅支持关键字参数匹配。

.. note:: 标记器表达式中仅支持 :class:`int`、（未转义的）:class:`str`、:class:`bool` 和 :data:`None` 值。

基于它们的节点 ID 选择测试
--------------------------------------

你可以提供一个或多个 :ref:`node IDs <node-id>` 作为位置参数
来仅选择指定的测试。这使得基于模块、类、方法或函数名称选择测试变得容易：

.. code-block:: pytest

    $ pytest -v test_server.py::TestClass::test_method
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y -- $PYTHON_PREFIX/bin/python
    cachedir: .pytest_cache
    rootdir: /home/sweet/project
    collecting ... collected 1 item

    test_server.py::TestClass::test_method PASSED                        [100%]

    ============================ 1 passed in 0.12s =============================

你也可以在类上选择：

.. code-block:: pytest

    $ pytest -v test_server.py::TestClass
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y -- $PYTHON_PREFIX/bin/python
    cachedir: .pytest_cache
    rootdir: /home/sweet/project
    collecting ... collected 1 item

    test_server.py::TestClass::test_method PASSED                        [100%]

    ============================ 1 passed in 0.12s =============================

或选择多个节点：

.. code-block:: pytest

    $ pytest -v test_server.py::TestClass test_server.py::test_send_http
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y -- $PYTHON_PREFIX/bin/python
    cachedir: .pytest_cache
    rootdir: /home/sweet/project
    collecting ... collected 2 items

    test_server.py::TestClass::test_method PASSED                        [ 50%]
    test_server.py::test_send_http PASSED                                [100%]

    ============================ 2 passed in 0.12s =============================

.. _node-id:

.. note::

    节点 ID 的形式为 ``module.py::class::method`` 或
    ``module.py::function``。节点 ID 控制哪些测试被
    收集，因此 ``module.py::class`` 将选择类上的所有测试方法。
    对于参数化 fixture 或测试的每个参数也会创建节点，
    因此选择参数化测试必须包含参数值，例如
    ``module.py::function[param]``。

    失败测试的节点 ID 在使用 ``-rf`` 选项运行 pytest 时
    显示在测试摘要信息中。你也可以
    从 ``pytest --collect-only`` 的输出构造节点 ID。

使用 ``-k expr`` 基于名称选择测试
-------------------------------------------------------

.. versionadded:: 2.0/2.3.4

你可以使用 :option:`-k` 命令行选项来指定一个表达式，
该表达式在测试名称上实现子字符串匹配，而不是 :option:`-m` 在标记器上提供的精确匹配。这使得基于名称选择测试变得容易：

.. versionchanged:: 5.4

表达式匹配现在不区分大小写。

.. code-block:: pytest

    $ pytest -v -k http  # 使用上面定义的示例模块运行
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y -- $PYTHON_PREFIX/bin/python
    cachedir: .pytest_cache
    rootdir: /home/sweet/project
    collecting ... collected 4 items / 3 deselected / 1 selected

    test_server.py::test_send_http PASSED                                [100%]

    ===================== 1 passed, 3 deselected in 0.12s ======================

你也可以运行除匹配关键字的测试之外的所有测试：

.. code-block:: pytest

    $ pytest -k "not send_http" -v
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y -- $PYTHON_PREFIX/bin/python
    cachedir: .pytest_cache
    rootdir: /home/sweet/project
    collecting ... collected 4 items / 1 deselected / 3 selected

    test_server.py::test_something_quick PASSED                          [ 33%]
    test_server.py::test_another PASSED                                  [ 66%]
    test_server.py::TestClass::test_method PASSED                        [100%]

    ===================== 3 passed, 1 deselected in 0.12s ======================

或者选择 "http" 和 "quick" 测试：

.. code-block:: pytest

    $ pytest -k "http or quick" -v
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y -- $PYTHON_PREFIX/bin/python
    cachedir: .pytest_cache
    rootdir: /home/sweet/project
    collecting ... collected 4 items / 2 deselected / 2 selected

    test_server.py::test_send_http PASSED                                [ 50%]
    test_server.py::test_something_quick PASSED                          [100%]

    ===================== 2 passed, 2 deselected in 0.12s ======================

你可以使用 ``and``、``or``、``not`` 和括号。

除了测试的名称之外，:option:`-k` 还匹配测试的父级名称（通常是文件和类的名称）、测试函数上设置的属性、应用于它或其父级的标记器，以及显式添加到它或其父级的任何 :attr:`extra keywords <_pytest.nodes.Node.extra_keyword_matches>`。

注册标记器
-------------------------------------



.. ini-syntax for custom markers:

为你的测试套件注册标记器很简单：

.. code-block:: toml

    # pytest.toml 的内容
    [pytest]
    markers = ["webtest: mark a test as a webtest.", "slow: mark test as slow."]

可以注册多个自定义标记器，每个标记器定义在自己的行中，如上例所示。

你可以查询测试套件存在哪些标记器——列表包括我们刚刚定义的 ``webtest`` 和 ``slow`` 标记器：

.. code-block:: pytest

    $ pytest --markers
    @pytest.mark.webtest: mark a test as a webtest.

    @pytest.mark.slow: mark test as slow.

    @pytest.mark.filterwarnings(warning): add a warning filter to the given test. see https://docs.pytest.org/en/stable/how-to/capture-warnings.html#pytest-mark-filterwarnings

    @pytest.mark.skip(reason=None): skip the given test function with an optional reason. Example: skip(reason="no way of currently testing this") skips the test.

    @pytest.mark.skipif(condition, ..., *, reason=...): skip the given test function if any of the conditions evaluate to True. Example: skipif(sys.platform == 'win32') skips the test if we are on the win32 platform. See https://docs.pytest.org/en/stable/reference/reference.html#pytest-mark-skipif

    @pytest.mark.xfail(condition, ..., *, reason=..., run=True, raises=None, strict=strict_xfail): mark the test function as an expected failure if any of the conditions evaluate to True. Optionally specify a reason for better reporting and run=False if you don't even want to execute the test function. If only specific exception(s) are expected, you can list them in raises, and if the test fails in other ways, it will be reported as a true failure. See https://docs.pytest.org/en/stable/reference/reference.html#pytest-mark-xfail

    @pytest.mark.parametrize(argnames, argvalues): call a test function multiple times passing in different arguments in turn. argvalues generally needs to be a list of values if argnames specifies only one name or a list of tuples of values if argnames specifies multiple names. Example: @parametrize('arg1', [1,2]) would lead to two calls of the decorated test function, one with arg1=1 and another with arg1=2.see https://docs.pytest.org/en/stable/how-to/parametrize.html for more info and examples.

    @pytest.mark.usefixtures(fixturename1, fixturename2, ...): mark tests as needing all of the specified fixtures. see https://docs.pytest.org/en/stable/explanation/fixtures.html#usefixtures

    @pytest.mark.tryfirst: mark a hook implementation function such that the plugin machinery will try to call it first/as early as possible. DEPRECATED, use @pytest.hookimpl(tryfirst=True) instead.

    @pytest.mark.trylast: mark a hook implementation function such that the plugin machinery will try to call it last/as late as possible. DEPRECATED, use @pytest.hookimpl(trylast=True) instead.


有关如何从插件添加和使用标记器的示例，请参见 :ref:`adding a custom marker from a plugin`。

.. note::

    建议显式注册标记器，以便：

    * 测试套件中有一个地方定义你的标记器

    * 通过 ``pytest --markers`` 查询现有标记器会给出良好的输出

    * 如果你使用 :confval:`strict_markers` 配置选项，函数标记器中的拼写错误将被视为错误。

.. _`scoped-marking`:

标记整个类或模块
----------------------------------------------------

你可以将 ``pytest.mark`` 装饰器用于类，以将标记器应用于其所有测试方法：

.. code-block:: python

    # test_mark_classlevel.py 的内容
    import pytest


    @pytest.mark.webtest
    class TestClass:
        def test_startup(self):
            pass

        def test_startup_and_more(self):
            pass

这等同于直接将装饰器应用于两个测试函数。

要在模块级别应用标记器，使用 :globalvar:`pytestmark` 全局变量::

    import pytest
    pytestmark = pytest.mark.webtest

或多个标记器::

    pytestmark = [pytest.mark.webtest, pytest.mark.slowtest]


由于历史原因，在类装饰器引入之前，可以在测试类上设置 :globalvar:`pytestmark` 属性，如下所示：

.. code-block:: python

    import pytest


    class TestClass:
        pytestmark = pytest.mark.webtest

.. _`marking individual tests when using parametrize`:

使用参数化时标记单个测试
-----------------------------------------------

使用参数化时，应用标记器将使其应用于每个单独的测试。但是也可以将标记器应用于单个测试实例：

.. code-block:: python

    import pytest


    @pytest.mark.foo
    @pytest.mark.parametrize(
        ("n", "expected"), [(1, 2), pytest.param(1, 3, marks=pytest.mark.bar), (2, 3)]
    )
    def test_increment(n, expected):
        assert n + 1 == expected

在这个示例中，标记 "foo" 将应用于三个测试中的每一个，而标记 "bar" 仅应用于第二个测试。Skip 和 xfail 标记也可以以这种方式应用，参见 :ref:`skip/xfail with parametrize`。

.. _`adding a custom marker from a plugin`:

自定义标记器和命令行选项以控制测试运行
----------------------------------------------------------

.. regendoc:wipe

插件可以提供自定义标记器并基于它实现特定行为。这是一个自包含的示例，它添加了一个命令行选项和一个参数化测试函数标记器，以运行通过命名环境指定的测试：

.. code-block:: python

    # conftest.py 的内容

    import pytest


    def pytest_addoption(parser):
        parser.addoption(
            "-E",
            action="store",
            metavar="NAME",
            help="only run tests matching the environment NAME.",
        )


    def pytest_configure(config):
        # register an additional marker
        config.addinivalue_line(
            "markers", "env(name): mark test to run only on named environment"
        )


    def pytest_runtest_setup(item):
        envnames = [mark.args[0] for mark in item.iter_markers(name="env")]
        if envnames:
            if item.config.getoption("-E") not in envnames:
                pytest.skip(f"test requires env in {envnames!r}")

使用此本地插件的测试文件：

.. code-block:: python

    # test_someenv.py 的内容

    import pytest


    @pytest.mark.env("stage1")
    def test_basic_db_operation():
        pass

以及指定与测试需要不同的环境的示例调用：

.. code-block:: pytest

    $ pytest -E stage2
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 1 item

    test_someenv.py s                                                    [100%]

    ============================ 1 skipped in 0.12s ============================

以及指定所需确切环境的示例：

.. code-block:: pytest

    $ pytest -E stage1
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 1 item

    test_someenv.py .                                                    [100%]

    ============================ 1 passed in 0.12s =============================

:option:`--markers` 选项始终为你提供可用标记器列表：

.. code-block:: pytest

    $ pytest --markers
    @pytest.mark.env(name): mark test to run only on named environment

    @pytest.mark.filterwarnings(warning): add a warning filter to the given test. see https://docs.pytest.org/en/stable/how-to/capture-warnings.html#pytest-mark-filterwarnings

    @pytest.mark.skip(reason=None): skip the given test function with an optional reason. Example: skip(reason="no way of currently testing this") skips the test.

    @pytest.mark.skipif(condition, ..., *, reason=...): skip the given test function if any of the conditions evaluate to True. Example: skipif(sys.platform == 'win32') skips the test if we are on the win32 platform. See https://docs.pytest.org/en/stable/reference/reference.html#pytest-mark-skipif

    @pytest.mark.xfail(condition, ..., *, reason=..., run=True, raises=None, strict=strict_xfail): mark the test function as an expected failure if any of the conditions evaluate to True. Optionally specify a reason for better reporting and run=False if you don't even want to execute the test function. If only specific exception(s) are expected, you can list them in raises, and if the test fails in other ways, it will be reported as a true failure. See https://docs.pytest.org/en/stable/reference/reference.html#pytest-mark-xfail

    @pytest.mark.parametrize(argnames, argvalues): call a test function multiple times passing in different arguments in turn. argvalues generally needs to be a list of values if argnames specifies only one name or a list of tuples of values if argnames specifies multiple names. Example: @parametrize('arg1', [1,2]) would lead to two calls of the decorated test function, one with arg1=1 and another with arg1=2.see https://docs.pytest.org/en/stable/how-to/parametrize.html for more info and examples.

    @pytest.mark.usefixtures(fixturename1, fixturename2, ...): mark tests as needing all of the specified fixtures. see https://docs.pytest.org/en/stable/explanation/fixtures.html#usefixtures

    @pytest.mark.tryfirst: mark a hook implementation function such that the plugin machinery will try to call it first/as early as possible. DEPRECATED, use @pytest.hookimpl(tryfirst=True) instead.

    @pytest.mark.trylast: mark a hook implementation function such that the plugin machinery will try to call it last/as late as possible. DEPRECATED, use @pytest.hookimpl(trylast=True) instead.


.. _`passing callables to custom markers`:

将可调用对象传递给自定义标记器
--------------------------------------------

.. regendoc:wipe

以下是将用于下一个示例的配置文件：

.. code-block:: python

    # conftest.py 的内容
    import sys


    def pytest_runtest_setup(item):
        for marker in item.iter_markers(name="my_marker"):
            print(marker)
            sys.stdout.flush()

自定义标记器可以通过将其作为可调用对象调用或使用 ``pytest.mark.MARKER_NAME.with_args`` 来定义其参数集，即 ``args`` 和 ``kwargs`` 属性。这两种方法在大多数情况下实现相同的效果。

但是，如果有一个可调用对象作为单个位置参数且没有关键字参数，使用 ``pytest.mark.MARKER_NAME(c)`` 将不会将 ``c`` 作为位置参数传递，而是会用自定义标记器装饰 ``c``（参见 :ref:`MarkDecorator <mark>`）。幸运的是，``pytest.mark.MARKER_NAME.with_args`` 可以解决这个问题：

.. code-block:: python

    # test_custom_marker.py 的内容
    import pytest


    def hello_world(*args, **kwargs):
        return "Hello World"


    @pytest.mark.my_marker.with_args(hello_world)
    def test_with_args():
        pass

输出如下：

.. code-block:: pytest

    $ pytest -q -s
    Mark(name='my_marker', args=(<function hello_world at 0xdeadbeef0001>,), kwargs={})
    .
    1 passed in 0.12s

我们可以看到自定义标记器的参数集已扩展为包含函数 ``hello_world``。这是将自定义标记器创建为可调用对象（在幕后调用 ``__call__``）与使用 ``with_args`` 之间的关键区别。


读取从多个地方设置的标记器
----------------------------------------------------

.. versionadded: 2.2.2

.. regendoc:wipe

如果你在测试套件中大量使用标记器，你可能会遇到将标记器多次应用于测试函数的情况。从插件代码中，你可以读取所有这些设置。示例：

.. code-block:: python

    # test_mark_three_times.py 的内容
    import pytest

    pytestmark = pytest.mark.glob("module", x=1)


    @pytest.mark.glob("class", x=2)
    class TestClass:
        @pytest.mark.glob("function", x=3)
        def test_something(self):
            pass

这里我们将标记器 "glob" 应用于同一测试函数三次。从 conftest 文件中，我们可以这样读取它：

.. code-block:: python

    # conftest.py 的内容
    import sys


    def pytest_runtest_setup(item):
        for mark in item.iter_markers(name="glob"):
            print(f"glob args={mark.args} kwargs={mark.kwargs}")
            sys.stdout.flush()

让我们在不捕获输出的情况下运行此测试，看看我们得到什么：

.. code-block:: pytest

    $ pytest -q -s
    glob args=('function',) kwargs={'x': 3}
    glob args=('class',) kwargs={'x': 2}
    glob args=('module',) kwargs={'x': 1}
    .
    1 passed in 0.12s

使用 pytest 标记平台特定测试
--------------------------------------------------------------

.. regendoc:wipe

假设你有一个测试套件，它标记特定平台的测试，
即 ``pytest.mark.darwin``、``pytest.mark.win32`` 等，并且你
也有在所有平台上运行且没有特定标记器的测试。如果你现在想有一种方法只为你特定的平台运行测试，你可以使用以下插件：

.. code-block:: python

    # conftest.py 的内容
    #
    import sys

    import pytest

    ALL = set("darwin linux win32".split())


    def pytest_runtest_setup(item):
        supported_platforms = ALL.intersection(mark.name for mark in item.iter_markers())
        plat = sys.platform
        if supported_platforms and plat not in supported_platforms:
            pytest.skip(f"cannot run on platform {plat}")

然后，如果测试被指定为不同的平台，则测试将被跳过。
让我们做一个小的测试文件来展示这是什么样子的：

.. code-block:: python

    # test_plat.py 的内容

    import pytest


    @pytest.mark.darwin
    def test_if_apple_is_evil():
        pass


    @pytest.mark.linux
    def test_if_linux_works():
        pass


    @pytest.mark.win32
    def test_if_win32_crashes():
        pass


    def test_runs_everywhere():
        pass

然后你将看到两个测试被跳过，两个测试被按预期执行：

.. code-block:: pytest

    $ pytest -rs # 此选项报告跳过原因
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 4 items

    test_plat.py s.s.                                                    [100%]

    ========================= short test summary info ==========================
    SKIPPED [2] conftest.py:13: cannot run on platform linux
    ======================= 2 passed, 2 skipped in 0.12s =======================

注意，如果你通过标记器命令行选项指定平台，如下所示：

.. code-block:: pytest

    $ pytest -m linux
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 4 items / 3 deselected / 1 selected

    test_plat.py .                                                       [100%]

    ===================== 1 passed, 3 deselected in 0.12s ======================

那么未标记的测试将不会运行。因此，这是一种将运行限制到特定测试的方式。

基于测试名称自动添加标记器
--------------------------------------------------------

.. regendoc:wipe

如果你的测试套件中测试函数名称指示某种测试类型，你可以实现一个钩子来自动定义标记器，以便你可以使用 :option:`-m` 选项。让我们看看这个测试模块：

.. code-block:: python

    # test_module.py 的内容


    def test_interface_simple():
        assert 0


    def test_interface_complex():
        assert 0


    def test_event_simple():
        assert 0


    def test_something_else():
        assert 0

我们想动态定义两个标记器，可以在 ``conftest.py`` 插件中完成：

.. code-block:: python

    # conftest.py 的内容

    import pytest


    def pytest_collection_modifyitems(items):
        for item in items:
            if "interface" in item.nodeid:
                item.add_marker(pytest.mark.interface)
            elif "event" in item.nodeid:
                item.add_marker(pytest.mark.event)

我们现在可以使用 ``-m option`` 来选择一组：

.. code-block:: pytest

    $ pytest -m interface --tb=short
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 4 items / 2 deselected / 2 selected

    test_module.py FF                                                    [100%]

    ================================= FAILURES =================================
    __________________________ test_interface_simple ___________________________
    test_module.py:4: in test_interface_simple
        assert 0
    E   assert 0
    __________________________ test_interface_complex __________________________
    test_module.py:8: in test_interface_complex
        assert 0
    E   assert 0
    ========================= short test summary info ==========================
    FAILED test_module.py::test_interface_simple - assert 0
    FAILED test_module.py::test_interface_complex - assert 0
    ===================== 2 failed, 2 deselected in 0.12s ======================

或者选择 "event" 和 "interface" 测试：

.. code-block:: pytest

    $ pytest -m "interface or event" --tb=short
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 4 items / 1 deselected / 3 selected

    test_module.py FFF                                                   [100%]

    ================================= FAILURES =================================
    __________________________ test_interface_simple ___________________________
    test_module.py:4: in test_interface_simple
        assert 0
    E   assert 0
    __________________________ test_interface_complex __________________________
    test_module.py:8: in test_interface_complex
        assert 0
    E   assert 0
    ____________________________ test_event_simple _____________________________
    test_module.py:12: in test_event_simple
        assert 0
    E   assert 0
    ========================= short test summary info ==========================
    FAILED test_module.py::test_interface_simple - assert 0
    FAILED test_module.py::test_interface_complex - assert 0
    FAILED test_module.py::test_event_simple - assert 0
    ===================== 3 failed, 1 deselected in 0.12s ======================
