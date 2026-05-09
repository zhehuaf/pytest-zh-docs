
.. _`test generators`:
.. _`parametrizing-tests`:
.. _`parametrized test functions`:
.. _`parametrize`:

.. _`parametrize-basics`:

如何参数化 fixtures 和测试函数
==========================================================================

pytest 在多个级别启用测试参数化：

- :py:func:`pytest.fixture` 允许 :ref:`参数化 fixture 函数 <fixture-parametrize>`。

* `@pytest.mark.parametrize`_ 允许在测试函数或类中定义多组参数和 fixtures。

* `pytest_generate_tests`_ 允许定义自定义参数化方案或扩展。


.. note::

    参见 :ref:`subtests` 了解参数化的替代方案。

.. _parametrizemark:
.. _`@pytest.mark.parametrize`:


``@pytest.mark.parametrize``: 参数化测试函数
---------------------------------------------------------------------

.. regendoc: wipe

内置的 :ref:`pytest.mark.parametrize ref` 装饰器启用测试函数的参数化。以下是一个典型示例，测试函数实现检查某个输入是否产生预期输出：

.. code-block:: python

    # test_expectation.py 的内容
    import pytest


    @pytest.mark.parametrize("test_input,expected", [("3+5", 8), ("2+4", 6), ("6*9", 42)])
    def test_eval(test_input, expected):
        assert eval(test_input) == expected

这里，``@parametrize`` 装饰器定义了三个不同的 ``(test_input,expected)`` 元组，因此 ``test_eval`` 函数将使用它们依次运行三次：

.. code-block:: pytest

    $ pytest
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 3 items

    test_expectation.py ..F                                              [100%]

    ================================= FAILURES =================================
    ____________________________ test_eval[6*9-42] _____________________________

    test_input = '6*9', expected = 42

        @pytest.mark.parametrize("test_input,expected", [("3+5", 8), ("2+4", 6), ("6*9", 42)])
        def test_eval(test_input, expected):
    >       assert eval(test_input) == expected
    E       AssertionError: assert 54 == 42
    E        +  where 54 = eval('6*9')

    test_expectation.py:6: AssertionError
    ========================= short test summary info ==========================
    FAILED test_expectation.py::test_eval[6*9-42] - AssertionError: assert 54...
    ======================= 1 failed, 2 passed in 0.12s ========================

.. note::

    参数值按原样传递给测试（不进行任何复制）。

    例如，如果你传递列表或字典作为参数值，并且测试用例代码修改了它，修改将反映到后续的测试用例调用中。

.. note::

    pytest 默认会转义参数化中使用的 unicode 字符串中的任何非 ascii 字符，因为它有几个缺点。
    但是，如果你想在参数化中使用 unicode 字符串并在终端中按原样（非转义）查看它们，请在你的配置文件中
    使用此选项：

    .. tab:: toml

        .. code-block:: toml

            [pytest]
            disable_test_id_escaping_and_forfeit_all_rights_to_community_support = true

    .. tab:: ini

        .. code-block:: ini

            [pytest]
            disable_test_id_escaping_and_forfeit_all_rights_to_community_support = true

    注意，这可能会根据你使用的终端和操作系统导致不需要的副作用，甚至错误，因为 ``test_id`` 用于标识测试，并在多个位置显示，其中一些可能不支持 unicode。

    但请记住，这可能会导致不必要的副作用，
    甚至错误，具体取决于使用的操作系统和当前安装的插件，
    因此请自担风险使用。


在此示例设计中，只有一对输入/输出值无法通过
简单的测试函数。与测试函数参数一样，
你可以在回溯中看到 ``input`` 和 ``output`` 值。

请注意，你也可以在类或模块上使用 parametrize 标记
（参见 :ref:`mark`），这将使用参数集调用多个函数，
例如：


.. code-block:: python

    import pytest


    @pytest.mark.parametrize("n,expected", [(1, 2), (3, 4)])
    class TestClass:
        def test_simple_case(self, n, expected):
            assert n + 1 == expected

        def test_weird_simple_case(self, n, expected):
            assert (n * 1) + 1 == expected


要为模块中的所有测试进行参数化，你可以赋值给 :globalvar:`pytestmark` 全局变量：


.. code-block:: python

    import pytest

    pytestmark = pytest.mark.parametrize("n,expected", [(1, 2), (3, 4)])


    class TestClass:
        def test_simple_case(self, n, expected):
            assert n + 1 == expected

        def test_weird_simple_case(self, n, expected):
            assert (n * 1) + 1 == expected


也可以在 parametrize 中标记单个测试实例，
例如使用内置的 ``mark.xfail``：

.. code-block:: python

    # test_expectation.py 的内容
    import pytest


    @pytest.mark.parametrize(
        "test_input,expected",
        [("3+5", 8), ("2+4", 6), pytest.param("6*9", 42, marks=pytest.mark.xfail)],
    )
    def test_eval(test_input, expected):
        assert eval(test_input) == expected

让我们运行这个：

.. code-block:: pytest

    $ pytest
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 3 items

    test_expectation.py ..x                                              [100%]

    ======================= 2 passed, 1 xfailed in 0.12s =======================

之前导致失败的那组参数现在
显示为"xfailed"（预期失败）测试。

如果提供给 ``parametrize`` 的值导致空列表 - 例如，
如果它们是由某个函数动态生成的 - pytest 的行为
由 :confval:`empty_parameter_set_mark` 选项定义。

要获取多个参数化参数的所有组合，你可以堆叠
``parametrize`` 装饰器：

.. code-block:: python

    import pytest


    @pytest.mark.parametrize("x", [0, 1])
    @pytest.mark.parametrize("y", [2, 3])
    def test_foo(x, y):
        pass

这将使用参数设置为 ``x=0/y=2``、``x=1/y=2``、
``x=0/y=3`` 和 ``x=1/y=3`` 运行测试，按装饰器的顺序穷尽参数。


.. _`pytest_generate_tests`:

基本 ``pytest_generate_tests`` 示例
---------------------------------------------

有时你可能想要实现自己的参数化方案
或为确定 fixture 的参数或范围实现一些动态性。
为此，你可以使用 ``pytest_generate_tests`` 钩子，
在收集测试函数时调用。通过传入的
``metafunc`` 对象，你可以检查请求的测试上下文，最重要的是，
你可以调用 ``metafunc.parametrize()`` 来引起
参数化。

例如，假设我们想要运行一个接受字符串输入的测试，
我们想通过一个新的 ``pytest`` 命令行选项来设置它。首先让我们编写
一个简单的测试，接受 ``stringinput`` fixture 函数参数：

.. code-block:: python

    # test_strings.py 的内容


    def test_valid_string(stringinput):
        assert stringinput.isalpha()

现在我们添加一个 ``conftest.py`` 文件，包含
命令行选项的添加和我们的测试函数的参数化：

.. code-block:: python

    # conftest.py 的内容


    def pytest_addoption(parser):
        parser.addoption(
            "--stringinput",
            action="append",
            default=[],
            help="要传递给测试函数的 stringinputs 列表",
        )


    def pytest_generate_tests(metafunc):
        if "stringinput" in metafunc.fixturenames:
            metafunc.parametrize("stringinput", metafunc.config.getoption("stringinput"))

.. note::

    与其他钩子不同，:hook:`pytest_generate_tests` 钩子也可以直接在测试模块中实现
    或在测试类内部实现；pytest 也会在那里发现它。其他钩子必须位于 :ref:`conftest.py <localplugin>` 或插件中。
    参见 :ref:`writinghooks`。

如果我们现在传递两个 stringinput 值，我们的测试将运行两次：

.. code-block:: pytest

    $ pytest -q --stringinput="hello" --stringinput="world" test_strings.py
    ..                                                                   [100%]
    2 passed in 0.12s

让我们也用一个会导致测试失败的 stringinput 来运行：

.. code-block:: pytest

    $ pytest -q --stringinput="!" test_strings.py
    F                                                                    [100%]
    ================================= FAILURES =================================
    ___________________________ test_valid_string[!] ___________________________

    stringinput = '!'

        def test_valid_string(stringinput):
    >       assert stringinput.isalpha()
    E       AssertionError: assert False
    E        +  where False = <built-in method isalpha of str object at 0xdeadbeef0001>()
    E        +    where <built-in method isalpha of str object at 0xdeadbeef0001> = '!'.isalpha

    test_strings.py:4: AssertionError
    ========================= short test summary info ==========================
    FAILED test_strings.py::test_valid_string[!] - AssertionError: assert False
    1 failed in 0.12s

正如预期的那样，我们的测试函数失败了。

如果你不指定 stringinput，它将被跳过，因为
``metafunc.parametrize()`` 将被调用并传入空参数
列表：

.. code-block:: pytest

    $ pytest -q -rs test_strings.py
    s                                                                    [100%]
    ========================= short test summary info ==========================
    SKIPPED [1] test_strings.py: got empty parameter set for (stringinput)
    1 skipped in 0.12s

请注意，当使用不同的参数集多次调用 ``metafunc.parametrize`` 时，所有参数集之间的参数名称不能重复，否则会引发错误。

更多示例
-------------

更多示例，你可能想查看 :ref:`更多参数化示例 <paramexamples>`。
