
.. _paramexamples:

参数化测试
=================================================

``pytest`` 允许你轻松地参数化测试函数。
有关基本文档，请参见 :ref:`parametrize-basics`。

下面我们提供一些使用内置机制的示例。

根据命令行参数生成参数组合
----------------------------------------------------------------------------

.. regendoc:wipe

假设我们想用不同的计算参数执行测试，并且参数范围由命令行参数决定。让我们首先编写一个简单的（什么都不做的）计算测试：

.. code-block:: python

    # test_compute.py 的内容


    def test_compute(param1):
        assert param1 < 4

现在我们添加一个这样的测试配置：

.. code-block:: python

    # conftest.py 的内容


    def pytest_addoption(parser):
        parser.addoption("--all", action="store_true", help="run all combinations")


    def pytest_generate_tests(metafunc):
        if "param1" in metafunc.fixturenames:
            if metafunc.config.getoption("all"):
                end = 5
            else:
                end = 2
            metafunc.parametrize("param1", range(end))

这意味着如果我们不传递 ``--all``，我们只运行 2 个测试：

.. code-block:: pytest

    $ pytest -q test_compute.py
    ..                                                                   [100%]
    2 passed in 0.12s

我们只运行了两个计算，所以看到两个点。让我们运行完整版本：

.. code-block:: pytest

    $ pytest -q --all
    ....F                                                                [100%]
    ================================= FAILURES =================================
    _____________________________ test_compute[4] ______________________________

    param1 = 4

        def test_compute(param1):
    >       assert param1 < 4
    E       assert 4 < 4

    test_compute.py:4: AssertionError
    ========================= short test summary info ==========================
    FAILED test_compute.py::test_compute[4] - assert 4 < 4
    1 failed, 4 passed in 0.12s

正如预期的那样，当运行 ``param1`` 值的完整范围时，我们会在最后一个值上得到错误。


测试 ID 的多种选项
------------------------------------

pytest 将为参数化测试中的每组值构建一个字符串作为测试 ID。这些 ID 可以与 :option:`-k` 一起使用来选择要运行的特定用例，并且当某个用例失败时它们也会标识该特定用例。使用 :option:`--collect-only` 运行 pytest 将显示生成的 ID。

数字、字符串、布尔值和 None 将在测试 ID 中使用它们通常的字符串表示。对于其他对象，pytest 将基于参数名称生成一个字符串：

.. code-block:: python

    # test_time.py 的内容

    from datetime import datetime, timedelta

    import pytest

    testdata = [
        (datetime(2001, 12, 12), datetime(2001, 12, 11), timedelta(1)),
        (datetime(2001, 12, 11), datetime(2001, 12, 12), timedelta(-1)),
    ]


    @pytest.mark.parametrize("a,b,expected", testdata)
    def test_timedistance_v0(a, b, expected):
        diff = a - b
        assert diff == expected


    @pytest.mark.parametrize("a,b,expected", testdata, ids=["forward", "backward"])
    def test_timedistance_v1(a, b, expected):
        diff = a - b
        assert diff == expected


    def idfn(val):
        if isinstance(val, (datetime,)):
            # 注意这不会显示任何时/分/秒
            return val.strftime("%Y%m%d")


    @pytest.mark.parametrize("a,b,expected", testdata, ids=idfn)
    def test_timedistance_v2(a, b, expected):
        diff = a - b
        assert diff == expected


    @pytest.mark.parametrize(
        "a,b,expected",
        [
            pytest.param(
                datetime(2001, 12, 12), datetime(2001, 12, 11), timedelta(1), id="forward"
            ),
            pytest.param(
                datetime(2001, 12, 11), datetime(2001, 12, 12), timedelta(-1), id="backward"
            ),
        ],
    )
    def test_timedistance_v3(a, b, expected):
        diff = a - b
        assert diff == expected

在 ``test_timedistance_v0`` 中，我们让 pytest 生成测试 ID。

在 ``test_timedistance_v1`` 中，我们将 ``ids`` 指定为用作测试 ID 的字符串列表。这些很简洁，但维护起来可能很麻烦。

在 ``test_timedistance_v2`` 中，我们将 ``ids`` 指定为一个函数，该函数可以生成字符串表示作为测试 ID 的一部分。所以我们的 ``datetime`` 值使用由 ``idfn`` 生成的标签，但由于我们没有为 ``timedelta`` 对象生成标签，它们仍然使用默认的 pytest 表示：

.. code-block:: pytest

    $ pytest test_time.py --collect-only
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 8 items

    <Dir parametrize.rst-213>
      <Module test_time.py>
        <Function test_timedistance_v0[a0-b0-expected0]>
        <Function test_timedistance_v0[a1-b1-expected1]>
        <Function test_timedistance_v1[forward]>
        <Function test_timedistance_v1[backward]>
        <Function test_timedistance_v2[20011212-20011211-expected0]>
        <Function test_timedistance_v2[20011211-20011212-expected1]>
        <Function test_timedistance_v3[forward]>
        <Function test_timedistance_v3[backward]>

    ======================== 8 tests collected in 0.12s ========================

在 ``test_timedistance_v3`` 中，我们使用 ``pytest.param`` 将测试 ID 与实际数据一起指定，而不是单独列出它们。

快速移植 "testscenarios"
------------------------------------

以下是运行使用 :pypi:`testscenarios` 配置的测试的快速移植，这是 Robert Collins 为标准 unittest 框架编写的附加组件。我们只需要做一些工作来为 pytest 的 :py:func:`Metafunc.parametrize <pytest.Metafunc.parametrize>` 构造正确的参数：

.. code-block:: python

    # test_scenarios.py 的内容


    def pytest_generate_tests(metafunc):
        idlist = []
        argvalues = []
        for scenario in metafunc.cls.scenarios:
            idlist.append(scenario[0])
            items = scenario[1].items()
            argnames = [x[0] for x in items]
            argvalues.append([x[1] for x in items])
        metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


    scenario1 = ("basic", {"attribute": "value"})
    scenario2 = ("advanced", {"attribute": "value2"})


    class TestSampleWithScenarios:
        scenarios = [scenario1, scenario2]

        def test_demo1(self, attribute):
            assert isinstance(attribute, str)

        def test_demo2(self, attribute):
            assert isinstance(attribute, str)

这是一个完全自包含的示例，你可以运行：

.. code-block:: pytest

    $ pytest test_scenarios.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 4 items

    test_scenarios.py ....                                               [100%]

    ============================ 4 passed in 0.12s =============================

如果你只收集测试，你将很好地看到测试函数的变体 'advanced' 和 'basic'：

.. code-block:: pytest

    $ pytest --collect-only test_scenarios.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 4 items

    <Dir parametrize.rst-213>
      <Module test_scenarios.py>
        <Class TestSampleWithScenarios>
          <Function test_demo1[basic]>
          <Function test_demo2[basic]>
          <Function test_demo1[advanced]>
          <Function test_demo2[advanced]>

    ======================== 4 tests collected in 0.12s ========================

注意我们告诉 ``metafunc.parametrize()`` 你的场景值应该被视为类作用域的。在 pytest-2.3 中，这导致了基于资源的排序。

延迟参数化资源的设置
---------------------------------------------------

.. regendoc:wipe

测试函数的参数化发生在收集时。最好只在实际测试运行时设置昂贵的资源，如数据库连接或子进程。这里有一个简单的示例，说明如何实现这一点。此测试需要 ``db`` 对象 fixture：

.. code-block:: python

    # test_backends.py 的内容

    import pytest


    def test_db_initialized(db):
        # 一个虚拟测试
        if db.__class__.__name__ == "DB2":
            pytest.fail("deliberately failing for demo purposes")

我们现在可以添加一个测试配置，生成对 ``test_db_initialized`` 函数的两次调用，并实现一个工厂，为实际的测试调用创建数据库对象：

.. code-block:: python

    # conftest.py 的内容
    import pytest


    def pytest_generate_tests(metafunc):
        if "db" in metafunc.fixturenames:
            metafunc.parametrize("db", ["d1", "d2"], indirect=True)


    class DB1:
        "one database object"


    class DB2:
        "alternative database object"


    @pytest.fixture
    def db(request):
        if request.param == "d1":
            return DB1()
        elif request.param == "d2":
            return DB2()
        else:
            raise ValueError("invalid internal test config")

让我们首先看看它在收集时的样子：

.. code-block:: pytest

    $ pytest test_backends.py --collect-only
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 2 items

    <Dir parametrize.rst-213>
      <Module test_backends.py>
        <Function test_db_initialized[d1]>
        <Function test_db_initialized[d2]>

    ======================== 2 tests collected in 0.12s ========================

然后当我们运行测试时：

.. code-block:: pytest

    $ pytest -q test_backends.py
    .F                                                                   [100%]
    ================================= FAILURES =================================
    _________________________ test_db_initialized[d2] __________________________

    db = <conftest.DB2 object at 0xdeadbeef0001>

        def test_db_initialized(db):
            # 一个虚拟测试
            if db.__class__.__name__ == "DB2":
    >           pytest.fail("deliberately failing for demo purposes")
    E           Failed: deliberately failing for demo purposes

    test_backends.py:8: Failed
    ========================= short test summary info ==========================
    FAILED test_backends.py::test_db_initialized[d2] - Failed: deliberately f...
    1 failed, 1 passed in 0.12s

第一次调用 ``db == "DB1"`` 通过，而第二次调用 ``db == "DB2"`` 失败。我们的 ``db`` fixture 函数在设置阶段实例化了每个 DB 值，而 ``pytest_generate_tests`` 在收集阶段生成了对 ``test_db_initialized`` 的两次相应调用。

间接参数化
---------------------------------------------------

在对测试进行参数化时，使用 ``indirect=True`` 参数允许使用接收值的 fixture 在将值传递给测试之前进行参数化：

.. code-block:: python

    import pytest


    @pytest.fixture
    def fixt(request):
        return request.param * 3


    @pytest.mark.parametrize("fixt", ["a", "b"], indirect=True)
    def test_indirect(fixt):
        assert len(fixt) == 3

这可以用于例如在 fixture 中在测试运行时进行更昂贵的设置，而不是在收集时运行这些设置步骤。

.. regendoc:wipe

在特定参数上应用 indirect
---------------------------------------------------

通常，参数化使用多个参数名称。可以将 ``indirect`` 参数应用于特定参数。可以通过传递参数名称的列表或元组给 ``indirect`` 来实现。在下面的示例中，有一个使用两个 fixtures ``x`` 和 ``y`` 的 ``test_indirect`` 函数。这里我们将包含 fixture ``x`` 名称的列表传递给 indirect。indirect 参数将仅应用于此参数，值 ``a`` 将被传递给相应的 fixture 函数：

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
