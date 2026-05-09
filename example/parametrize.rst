.. _`parametrize examples`:

参数化测试
=================================================

以下是一些使用 :ref:`parametrize <parametrizing>` 的示例。


.. _`parametrizing test functions`:

参数化测试函数
----------------------------------------------------

这是使用 :ref:`@pytest.mark.parametrize <@pytest.mark.parametrize>` 标记测试函数的简单示例，它使用所有 ``argvalues`` 检查特定的输入/预期输出组合：

.. code-block:: python

    # test_expectation.py 的内容
    import pytest


    @pytest.mark.parametrize("test_input,expected", [("3+5", 8), ("2+4", 6), ("6*9", 42)])
    def test_eval(test_input, expected):
        assert eval(test_input) == expected

通过运行，你会看到三个测试被执行：

.. code-block:: pytest

    $ pytest
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 3 items

    test_expectation.py ..F                                              [100%]

    ================================= FAILURES =================================
    _______________________________ test_eval[6*9-42] ____________________________

    test_input = '6*9', expected = 42

        @pytest.mark.parametrize("test_input,expected", [("3+5", 8), ("2+4", 6), ("6*9", 42)])
        def test_eval(test_input, expected):
    >       assert eval(test_input) == expected
    E       assert 54 == 42
    E        +  where 54 = eval('6*9')

    test_expectation.py:6: AssertionError
    ========================= short test summary info ==========================
    FAILED test_expectation.py::test_eval[6*9-42] - assert 54 == 42
    ======================= 2 passed, 1 failed in 0.12s ==========================

注意，在失败的测试中，pytest 特别报告了 ``test_input`` 和 ``expected`` 的值。

也可以在单个函数参数上堆叠参数化标记，产生所有参数组合：

.. code-block:: python

    # test_foocompare.py 的内容
    import pytest


    @pytest.mark.parametrize("x", [0, 1])
    @pytest.mark.parametrize("y", [2, 3])
    def test_foo(x, y):
        pass


这将运行测试，参数设置为 ``x=0/y=2``、``x=0/y=3``、``x=1/y=2`` 和 ``x=1/y=3``，以装饰器组合的顺序穷举参数组合。


.. code-block:: pytest

    $ pytest -v test_foocompare.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y -- $PYTHON_PREFIX/bin/python
    cachedir: .pytest_cache
    rootdir: /home/sweet/project
    collected 4 items

    test_foocompare.py::test_foo[2-0] PASSED                              [ 25%]
    test_foocompare.py::test_foo[2-1] PASSED                              [ 50%]
    test_foocompare.py::test_foo[3-0] PASSED                              [ 75%]
    test_foocompare.py::test_foo[3-1] PASSED                              [100%]

    ============================ 4 passed in 0.12s =============================

.. _parametrizing_indirect:

使用参数化间接应用 fixtures
--------------------------------------------------------------

假设我们有以下示例：

.. code-block:: python

    # test_indirect.py 的内容
    import pytest


    @pytest.fixture
    def fixt(request):
        return request.param * 3


    @pytest.mark.parametrize("fixt", ["a", "b"], indirect=True)
    def test_indirect(fixt):
        assert len(fixt) == 3


这可以用于比简单循环更少样板代码地编写许多测试，最重要的是可以使用完整的 :ref:`pytest fixture 机制 <fixtures>`。

通过 ``request`` 对象，可以向后传递请求 test context 或 parametrization 参数，并向前传递 fixture function：

.. code-block:: python

    # test_indirect_list.py 的内容
    import pytest


    @pytest.fixture(scope="function")
    def x(request):
        return request.param * 3


    @pytest.fixture(scope="function")
    def y(request):
        return request.param * 2


    @pytest.mark.parametrize("x, y", [("a", "b")], indirect=["x"])
    def test_indirect(x, y):
        assert x == "aaa"
        assert y == "b"

此测试的结果将是成功的：

.. code-block:: pytest

    $ pytest -v test_indirect_list.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y -- $PYTHON_PREFIX/bin/python
    cachedir: .pytest_cache
    rootdir: /home/sweet/project
    collecting ... collected 1 item

    test_indirect_list.py::test_indirect[a-b] PASSED                     [100%]

    ============================ 1 passed in 0.12s =============================

.. regendoc:wipe

通过 per-class 配置参数化测试方法
--------------------------------------------------------------

.. _`unittest parametrizer`: https://github.com/testing-cabal/unittest-ext/blob/master/params.py

这里是一个示例 ``pytest_generate_tests`` 函数，实现了类似 Michael Foord 的 `unittest parametrizer`_ 的参数化方案，但代码量少得多：

.. code-block:: python

    # ./test_parametrize.py 的内容
    import pytest


    def pytest_generate_tests(metafunc):
        # 每个测试函数调用一次
        funcarglist = metafunc.cls.params[metafunc.function.__name__]
        argnames = sorted(funcarglist[0])
        metafunc.parametrize(
            argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist]
        )


    class TestClass:
        # 一个指定测试方法多组参数集的映射
        params = {
            "test_equals": [dict(a=1, b=2), dict(a=3, b=3)],
            "test_zerodivision": [dict(a=1, b=0)],
        }

        def test_equals(self, a, b):
            assert a == b

        def test_zerodivision(self, a, b):
            with pytest.raises(ZeroDivisionError):
                a / b


我们的测试生成器查找一个类级定义，该定义指定要为每个测试函数使用哪些参数集。让我们运行它：

.. code-block:: pytest

    $ pytest -q
    F..                                                                  [100%]
    ================================= FAILURES =================================
    ________________________ TestClass.test_equals[1-2] ________________________

    self = <test_parametrize.TestClass object at 0xdeadbeef0002>, a = 1, b = 2

        def test_equals(self, a, b):
    >       assert a == b
    E       assert 1 == 2

    test_parametrize.py:21: AssertionError
    ========================= short test summary info ==========================
    FAILED test_parametrize.py::TestClass::test_equals[1-2] - assert 1 == 2
    1 failed, 2 passed in 0.12s

使用多个 fixtures 进行参数化
--------------------------------------

这里是一个简化的真实示例，使用参数化测试来测试不同 Python 解释器之间的对象序列化。我们定义一个 ``test_basic_objects`` 函数，它将为它的三个参数运行不同的参数集：

* ``python1``：第一个 Python 解释器，运行以 pickle-dump 对象到文件
* ``python2``：第二个解释器，运行以 pickle-load 对象从文件
* ``obj``：要被 dump/load 的对象

.. literalinclude:: multipython.py

如果我们没有安装所有 Python 解释器，运行它会得到一些跳过，否则运行所有组合（3 个解释器乘以 3 个解释器乘以 3 个要序列化/反序列化的对象）：

.. code-block:: pytest

   . $ pytest -rs -q multipython.py
   ssssssssssss......sss......                                          [100%]
   ========================= short test summary info ==========================
   SKIPPED [15] multipython.py:67: 'python3.11' not found
   12 passed, 15 skipped in 0.12s

可选实现/导入的参数化
---------------------------------------------------

如果你想比较给定 API 的几个实现的输出，你可以编写接收已导入实现的测试函数，并在实现无法导入/可用时被跳过。假设我们有一个"基础"实现，其他的（可能优化的）需要产生类似的结果：

.. code-block:: python

    # conftest.py 的内容

    import pytest


    @pytest.fixture(scope="session")
    def basemod(request):
        return pytest.importorskip("base")


    @pytest.fixture(scope="session", params=["opt1", "opt2"])
    def optmod(request):
        return pytest.importorskip(request.param)


然后是一个简单函数的基础实现：

.. code-block:: python

    # base.py 的内容
    def func1():
        return 1


和一个优化的版本：

.. code-block:: python

    # opt1.py 的内容
    def func1():
        return 1.0001


最后是一个小的测试模块：

.. code-block:: python

    # test_module.py 的内容


    def test_func1(basemod, optmod):
        assert round(basemod.func1(), 3) == round(optmod.func1(), 3)


如果启用跳过报告运行此测试：

.. code-block:: pytest

    $ pytest -rs test_module.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 2 items

    test_module.py .s                                                    [100%]

    ========================= short test summary info ==========================
    SKIPPED [1] test_module.py:3: could not import 'opt2': No module named 'opt2'
    ======================= 1 passed, 1 skipped in 0.12s =======================

你会看到我们没有 ``opt2`` 模块，因此 ``test_func1`` 的第二次测试运行被跳过了。几点说明：

- ``conftest.py`` 文件中的 fixture 函数是 "session-scoped" 的，因为我们不需要导入超过一次

- 如果你有多个测试函数和跳过的导入，你会看到报告中 ``[1]`` 计数增加

- 你也可以将 :ref:`@pytest.mark.parametrize <@pytest.mark.parametrize>` 样式的参数化放在测试函数上来参数化输入/输出值。


为单个参数化测试设置标记或测试 ID
--------------------------------------------------------------------

使用 ``pytest.param`` 为单个参数化测试应用标记或设置测试 ID。
例如：

.. code-block:: python

    # test_pytest_param_example.py 的内容
    import pytest


    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("3+5", 8),
            pytest.param("1+7", 8, marks=pytest.mark.basic),
            pytest.param("2+4", 6, marks=pytest.mark.basic, id="basic_2+4"),
            pytest.param(
                "6*9", 42, marks=[pytest.mark.basic, pytest.mark.xfail], id="basic_6*9"
            ),
        ],
    )
    def test_eval(test_input, expected):
        assert eval(test_input) == expected

在这个示例中，我们有 4 个参数化测试。除了第一个测试外，我们用自定义标记器 ``basic`` 标记其余三个参数化测试，对于第四个测试，我们还使用内置标记 ``xfail`` 来指示此测试预期失败。为了明确起见，我们为某些测试设置了测试 ID。

然后使用仅带有 ``basic`` 标记器的详细模式运行 ``pytest``：

.. code-block:: pytest

    $ pytest -v -m basic
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y -- $PYTHON_PREFIX/bin/python
    cachedir: .pytest_cache
    rootdir: /home/sweet/project
    collecting ... collected 24 items / 21 deselected / 3 selected

    test_pytest_param_example.py::test_eval[1+7-8] PASSED                [ 33%]
    test_pytest_param_example.py::test_eval[basic_2+4] PASSED            [ 66%]
    test_pytest_param_example.py::test_eval[basic_6*9] XFAIL             [100%]

    =============== 2 passed, 21 deselected, 1 xfailed in 0.12s ================

结果是：

- 收集了四个测试
- 一个测试被取消选择，因为它没有 ``basic`` 标记。
- 选择了三个带有 ``basic`` 标记的测试。
- 测试 ``test_eval[1+7-8]`` 通过了，但名称是自动生成的，令人困惑。
- 测试 ``test_eval[basic_2+4]`` 通过了。
- 测试 ``test_eval[basic_6*9]`` 预期失败，确实失败了。

.. _`parametrizing_conditional_raising`:

参数化条件性引发
--------------------------------------------------------------------

使用 :func:`pytest.raises` 和 :ref:`pytest.mark.parametrize ref` 装饰器来编写参数化测试，其中一些测试引发异常，另一些则不引发。

``contextlib.nullcontext`` 可用于测试预期不引发异常但应产生某些值的测试用例。值作为 ``enter_result`` 参数给出，它将作为 ``with`` 语句的目标可用（在下面的示例中为 ``e``）。

例如：

.. code-block:: python

    from contextlib import nullcontext

    import pytest


    @pytest.mark.parametrize(
        "example_input,expectation",
        [
            (3, nullcontext(2)),
            (2, nullcontext(3)),
            (1, nullcontext(6)),
            (0, pytest.raises(ZeroDivisionError)),
        ],
    )
    def test_division(example_input, expectation):
        """Test how much I know division."""
        with expectation as e:
            assert (6 / example_input) == e

在上面的示例中，前三个测试用例应该没有任何异常地运行，而第四个应该引发 ``ZeroDivisionError`` 异常，这是 pytest 预期的。
