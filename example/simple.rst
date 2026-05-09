
基本模式和示例
==========================================================

如何更改命令行选项默认值
-------------------------------------------

每次使用 ``pytest`` 时都输入相同的命令行选项可能会很繁琐。例如，如果你总是想查看有关跳过和预期失败测试的详细信息，以及更简洁的 "点" 进度输出，你可以将其写入配置文件：

.. code-block:: toml

    # pytest.toml 的内容
    [pytest]
    addopts = ["-ra", "-q"]

或者，你可以设置 ``PYTEST_ADDOPTS`` 环境变量，在使用环境时添加命令行选项：

.. code-block:: bash

    export PYTEST_ADDOPTS="-v"

以下是命令行在存在 ``addopts`` 或环境变量时的构建方式：

.. code-block:: text

    <配置文件 addopts> $PYTEST_ADDOPTS <额外的命令行参数>

所以如果用户在命令行中执行：

.. code-block:: bash

    pytest -m slow

实际执行的命令行是：

.. code-block:: bash

    pytest -ra -q -v -m slow

请注意，与其他命令行应用程序一样，在选项冲突的情况下，最后一个获胜，所以上面的示例会显示详细输出，因为 :option:`-v` 覆盖了 :option:`-q`。


.. _request example:

根据命令行选项向测试函数传递不同的值
----------------------------------------------------------------------------

.. regendoc:wipe

假设我们想编写一个依赖于命令行选项的测试。
这里有一个基本模式可以实现这一点：

.. code-block:: python

    # test_sample.py 的内容
    def test_answer(cmdopt):
        if cmdopt == "type1":
            print("first")
        elif cmdopt == "type2":
            print("second")
        assert 0  # 为了查看打印了什么


为此，我们需要添加一个命令行选项并通过 :ref:`fixture 函数 <fixture>` 提供 ``cmdopt``：

.. code-block:: python

    # conftest.py 的内容
    import pytest


    def pytest_addoption(parser):
        parser.addoption(
            "--cmdopt", action="store", default="type1", help="我的选项: type1 或 type2"
        )


    @pytest.fixture
    def cmdopt(request):
        return request.config.getoption("--cmdopt")

让我们在不提供新选项的情况下运行它：

.. code-block:: pytest

    $ pytest -q test_sample.py
    F                                                                    [100%]
    ================================= FAILURES =================================
    _______________________________ test_answer ________________________________

    cmdopt = 'type1'

        def test_answer(cmdopt):
            if cmdopt == "type1":
                print("first")
            elif cmdopt == "type2":
                print("second")
    >       assert 0  # 为了查看打印了什么
            ^^^^^^^^
    E       assert 0

    test_sample.py:6: AssertionError
    --------------------------- Captured stdout call ---------------------------
    first
    ========================= short test summary info ==========================
    FAILED test_sample.py::test_answer - assert 0
    1 failed in 0.12s

现在提供命令行选项：

.. code-block:: pytest

    $ pytest -q --cmdopt=type2
    F                                                                    [100%]
    ================================= FAILURES =================================
    _______________________________ test_answer ________________________________

    cmdopt = 'type2'

        def test_answer(cmdopt):
            if cmdopt == "type1":
                print("first")
            elif cmdopt == "type2":
                print("second")
    >       assert 0  # 为了查看打印了什么
            ^^^^^^^^
    E       assert 0

    test_sample.py:6: AssertionError
    --------------------------- Captured stdout call ---------------------------
    second
    ========================= short test summary info ==========================
    FAILED test_sample.py::test_answer - assert 0
    1 failed in 0.12s

你可以看到命令行选项到达了我们的测试。

我们可以通过列出选项来添加简单的输入验证：

.. code-block:: python

    # conftest.py 的内容
    import pytest


    def pytest_addoption(parser):
        parser.addoption(
            "--cmdopt",
            action="store",
            default="type1",
            help="我的选项: type1 或 type2",
            choices=("type1", "type2"),
        )

现在我们会对错误的参数给出反馈：

.. code-block:: pytest

    $ pytest -q --cmdopt=type3
    ERROR: usage: pytest [options] [file_or_dir] [file_or_dir] [...]
    pytest: error: argument --cmdopt: invalid choice: 'type3' (choose from type1, type2)
      inifile: None
      rootdir: /home/sweet/project


如果你需要提供更详细的错误消息，你可以使用 ``type`` 参数并引发 :exc:`pytest.UsageError`：

.. code-block:: python

    # conftest.py 的内容
    import pytest


    def type_checker(value):
        msg = "cmdopt 必须指定一个数字类型，格式为 typeNNN"
        if not value.startswith("type"):
            raise pytest.UsageError(msg)
        try:
            int(value[4:])
        except ValueError:
            raise pytest.UsageError(msg)

        return value


    def pytest_addoption(parser):
        parser.addoption(
            "--cmdopt",
            action="store",
            default="type1",
            help="我的选项: type1 或 type2",
            type=type_checker,
        )

这就完成了基本模式。然而，通常更希望的是在测试之外处理命令行选项，并传入不同或更复杂的对象。

动态添加命令行选项
--------------------------------------------------------------

.. regendoc:wipe

通过 :confval:`addopts` 你可以静态地为你的项目添加命令行选项。你也可以在命令行参数被处理之前动态修改它们：

.. code-block:: python

    # 可安装的外部插件
    import sys


    def pytest_load_initial_conftests(args):
        if "xdist" in sys.modules:  # pytest-xdist 插件
            import multiprocessing

            num = max(multiprocessing.cpu_count() / 2, 1)
            args[:] = ["-n", str(num)] + args

如果你安装了 :pypi:`xdist plugin <pytest-xdist>`，现在你将始终使用接近 CPU 数量的子进程数来执行测试运行。在空目录中使用上述 conftest.py 运行：

.. code-block:: pytest

    $ pytest
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 0 items

    ========================== no tests ran in 0.12s ===========================

.. _`excontrolskip`:

根据命令行选项控制跳过测试
--------------------------------------------------------------

.. regendoc:wipe

这是一个 ``conftest.py`` 文件，添加了 ``--runslow`` 命令行选项来控制跳过 ``pytest.mark.slow`` 标记的测试：

.. code-block:: python

    # conftest.py 的内容

    import pytest


    def pytest_addoption(parser):
        parser.addoption(
            "--runslow", action="store_true", default=False, help="run slow tests"
        )


    def pytest_configure(config):
        config.addinivalue_line("markers", "slow: mark test as slow to run")


    def pytest_collection_modifyitems(config, items):
        if config.getoption("--runslow"):
            # --runslow 在 CLI 中给出：不要跳过慢速测试
            return
        skip_slow = pytest.mark.skip(reason="need --runslow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)

我们现在可以编写这样的测试模块：

.. code-block:: python

    # test_module.py 的内容
    import pytest


    def test_func_fast():
        pass


    @pytest.mark.slow
    def test_func_slow():
        pass

运行时将看到被跳过的 "slow" 测试：

.. code-block:: pytest

    $ pytest -rs    # "-rs" 表示报告小 's' 的详细信息
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 2 items

    test_module.py .s                                                    [100%]

    ========================= short test summary info ==========================
    SKIPPED [1] test_module.py:8: need --runslow option to run
    ======================= 1 passed, 1 skipped in 0.12s =======================

或运行包括 ``slow`` 标记的测试：

.. code-block:: pytest

    $ pytest --runslow
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 2 items

    test_module.py ..                                                    [100%]

    ============================ 2 passed in 0.12s =============================

.. _`__tracebackhide__`:

编写良好集成的断言辅助函数
-----------------------------------------

.. regendoc:wipe

如果你有一个从测试中调用的测试辅助函数，你可以使用 ``pytest.fail`` 标记器以特定消息使测试失败。如果你在辅助函数的某处设置 ``__tracebackhide__`` 选项，测试支持函数将不会出现在回溯中。示例：

.. code-block:: python

    # test_checkconfig.py 的内容
    import pytest


    def checkconfig(x):
        __tracebackhide__ = True
        if not hasattr(x, "config"):
            pytest.fail(f"not configured: {x}")


    def test_something():
        checkconfig(42)

``__tracebackhide__`` 设置影响 ``pytest`` 显示回溯的方式：除非指定了 :option:`--full-trace` 命令行选项，否则 ``checkconfig`` 函数将不会显示。让我们运行这个小函数：

.. code-block:: pytest

    $ pytest -q test_checkconfig.py
    F                                                                    [100%]
    ================================= FAILURES =================================
    ______________________________ test_something ______________________________

        def test_something():
    >       checkconfig(42)
    E       Failed: not configured: 42

    test_checkconfig.py:11: Failed
    ========================= short test summary info ==========================
    FAILED test_checkconfig.py::test_something - Failed: not configured: 42
    1 failed in 0.12s

如果你只想隐藏某些异常，你可以将 ``__tracebackhide__`` 设置为一个可调用对象，该对象接收 ``ExceptionInfo`` 对象。例如，你可以使用这个来确保意外的异常类型不会被隐藏：

.. code-block:: python

    import operator

    import pytest


    class ConfigException(Exception):
        pass


    def checkconfig(x):
        __tracebackhide__ = operator.methodcaller("errisinstance", ConfigException)
        if not hasattr(x, "config"):
            raise ConfigException(f"not configured: {x}")


    def test_something():
        checkconfig(42)

这将避免在无关异常（即断言辅助函数中的错误）上隐藏异常回溯。


检测是否在 pytest 运行中
--------------------------------------------------------------

.. regendoc:wipe

通常让应用程序代码在被测试时表现不同是一个坏主意。但如果你绝对需要找出你的应用程序代码是否在测试中运行，你可以这样做：

.. code-block:: python

    import os


    if os.environ.get("PYTEST_VERSION") is not None:
        # 如果代码被 pytest 调用，你想做的事情
        ...
    else:
        # 如果代码未被 pytest 调用，你想做的事情
        ...


向测试报告头部添加信息
--------------------------------------------------------------

.. regendoc:wipe

在 ``pytest`` 运行中呈现额外信息很容易：

.. code-block:: python

    # conftest.py 的内容


    def pytest_report_header(config):
        return "project deps: mylib-1.1"

这将把字符串添加到测试头部：

.. code-block:: pytest

    $ pytest
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    project deps: mylib-1.1
    rootdir: /home/sweet/project
    collected 0 items

    ========================== no tests ran in 0.12s ===========================

.. regendoc:wipe

也可以返回一个字符串列表，这些字符串将被视为多行信息。你可以考虑使用 ``config.getoption('verbose')`` 来在适当时显示更多信息：

.. code-block:: python

    # conftest.py 的内容


    def pytest_report_header(config):
        if config.get_verbosity() > 0:
            return ["info1: did you know that ...", "did you?"]

这将仅在使用 "--v" 运行时添加信息：

.. code-block:: pytest

    $ pytest -v
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y -- $PYTHON_PREFIX/bin/python
    cachedir: .pytest_cache
    info1: did you know that ...
    did you?
    rootdir: /home/sweet/project
    collecting ... collected 0 items

    ========================== no tests ran in 0.12s ===========================

而在普通运行时没有：

.. code-block:: pytest

    $ pytest
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 0 items

    ========================== no tests ran in 0.12s ===========================

分析测试持续时间
--------------------------

.. regendoc:wipe

.. versionadded: 2.2

如果你有一个运行缓慢的大型测试套件，你可能想找出哪些测试是最慢的。让我们创建一个人工测试套件：

.. code-block:: python

    # test_some_are_slow.py 的内容
    import time


    def test_funcfast():
        time.sleep(0.1)


    def test_funcslow1():
        time.sleep(0.2)


    def test_funcslow2():
        time.sleep(0.3)

现在我们可以分析哪些测试函数执行最慢：

.. code-block:: pytest

    $ pytest --durations=3
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 3 items

    test_some_are_slow.py ...                                            [100%]

    =========================== slowest 3 durations ============================
    0.30s call     test_some_are_slow.py::test_funcslow2
    0.20s call     test_some_are_slow.py::test_funcslow1
    0.10s call     test_some_are_slow.py::test_funcfast
    ============================ 3 passed in 0.12s =============================

增量测试 - 测试步骤
---------------------------------------------------

.. regendoc:wipe

有时你可能会遇到由一系列测试步骤组成的测试情况。如果一步失败，继续执行后续步骤没有意义，因为它们无论如何都预期会失败，而且它们的回溯不会增加任何见解。这是一个简单的 ``conftest.py`` 文件，引入了一个 ``incremental`` 标记器，用于类上：

.. code-block:: python

    # conftest.py 的内容

    import pytest

    # 存储每个测试类名称和参数化索引的失败历史（如果使用了参数化）
    _test_failed_incremental: dict[str, dict[tuple[int, ...], str]] = {}


    def pytest_runtest_makereport(item, call):
        if "incremental" in item.keywords:
            # incremental 标记器被使用
            if call.excinfo is not None:
                # 测试失败
                # 检索测试的类名
                cls_name = str(item.cls)
                # 检索测试的索引（如果参数化与 incremental 结合使用）
                parametrize_index = (
                    tuple(item.callspec.indices.values())
                    if hasattr(item, "callspec")
                    else ()
                )
                # 检索测试函数的名称
                test_name = item.originalname or item.name
                # 存储失败测试的原始名称
                _test_failed_incremental.setdefault(cls_name, {}).setdefault(
                    parametrize_index, test_name
                )


    def pytest_runtest_setup(item):
        if "incremental" in item.keywords:
            # 检索测试的类名
            cls_name = str(item.cls)
            # 检查此类是否之前有测试失败
            if cls_name in _test_failed_incremental:
                # 检索测试的索引（如果参数化与 incremental 结合使用）
                parametrize_index = (
                    tuple(item.callspec.indices.values())
                    if hasattr(item, "callspec")
                    else ()
                )
                # 检索此类名称和索引第一个失败的测试函数名称
                test_name = _test_failed_incremental[cls_name].get(parametrize_index, None)
                # 如果找到名称，则此类名称和测试名称组合的测试已失败
                if test_name is not None:
                    pytest.xfail(f"previous test failed ({test_name})")


这两个钩子实现一起工作，以终止类中标记为增量的测试。这里是一个测试模块示例：

.. code-block:: python

    # test_step.py 的内容

    import pytest


    @pytest.mark.incremental
    class TestUserHandling:
        def test_login(self):
            pass

        def test_modification(self):
            assert 0

        def test_deletion(self):
            pass


    def test_normal():
        pass

如果我们运行它：

.. code-block:: pytest

    $ pytest -rx
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 4 items

    test_step.py .Fx.                                                    [100%]

    ================================= FAILURES =================================
    ____________________ TestUserHandling.test_modification ____________________

    self = <test_step.TestUserHandling object at 0xdeadbeef0001>

        def test_modification(self):
    >       assert 0
    E       assert 0

    test_step.py:11: AssertionError
    ========================= short test summary info ==========================
    XFAIL test_step.py::TestUserHandling::test_deletion - previous test failed (test_modification)
    ================== 1 failed, 2 passed, 1 xfailed in 0.12s ==================

我们会看到 ``test_deletion`` 没有被执行，因为 ``test_modification``
失败了。它被报告为 "预期失败"。


包/目录级别的 fixtures（setups）
-------------------------------------------------------

如果你有嵌套的测试目录，你可以通过将 fixture 函数放在该目录的 ``conftest.py`` 文件中来拥有每个目录的 fixture 作用域。你可以使用所有类型的 fixtures，包括 :ref:`autouse fixtures <autouse fixtures>`，它们等效于 xUnit 的 setup/teardown 概念。但是，建议在你的测试或测试类中有明确的 fixture 引用，而不是依赖隐式执行的 setup/teardown 函数，特别是当它们远离实际测试时。

这里是一个使 ``db`` fixture 在目录中可用的示例：

.. code-block:: python

    # a/conftest.py 的内容
    import pytest


    class DB:
        pass


    @pytest.fixture(scope="package")
    def db():
        return DB()

然后是该目录中的测试模块：

.. code-block:: python

    # a/test_db.py 的内容
    def test_a1(db):
        assert 0, db  # 显示值

另一个测试模块：

.. code-block:: python

    # a/test_db2.py 的内容
    def test_a2(db):
        assert 0, db  # 显示值

然后是姐妹目录中的一个模块，它将看不到 ``db`` fixture：

.. code-block:: python

    # b/test_error.py 的内容
    def test_root(db):  # 这里没有 db，会报错
        pass

我们可以运行它：

.. code-block:: pytest

    $ pytest
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 7 items

    a/test_db.py F                                                       [ 14%]
    a/test_db2.py F                                                      [ 28%]
    b/test_error.py E                                                    [ 42%]
    test_step.py .Fx.                                                    [100%]

    ================================== ERRORS ==================================
    _______________________ ERROR at setup of test_root ________________________
    file /home/sweet/project/b/test_error.py, line 1
      def test_root(db):  # 这里没有 db，会报错
    E       fixture 'db' not found
    >       available fixtures: cache, capfd, capfdbinary, caplog, capsys, capsysbinary, capteesys, doctest_namespace, monkeypatch, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, subtests, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory
    >       使用 'pytest --fixtures [testpath]' 查看它们。

    /home/sweet/project/b/test_error.py:1
    ================================= FAILURES =================================
    _________________________________ test_a1 __________________________________

    db = <conftest.DB object at 0xdeadbeef0002>

        def test_a1(db):
    >       assert 0, db  # 显示值
            ^^^^^^^^^^^^
    E       AssertionError: <conftest.DB object at 0xdeadbeef0002>
    E       assert 0

    a/test_db.py:2: AssertionError
    _________________________________ test_a2 __________________________________

    db = <conftest.DB object at 0xdeadbeef0002>

        def test_a2(db):
    >       assert 0, db  # 显示值
            ^^^^^^^^^^^^
    E       AssertionError: <conftest.DB object at 0xdeadbeef0002>
    E       assert 0

    a/test_db2.py:2: AssertionError
    ____________________ TestUserHandling.test_modification ____________________

    self = <test_step.TestUserHandling object at 0xdeadbeef0003>

        def test_modification(self):
    >       assert 0
    E       assert 0

    test_step.py:11: AssertionError
    ========================= short test summary info ==========================
    FAILED a/test_db.py::test_a1 - AssertionError: <conftest.DB object at 0x7...
    FAILED a/test_db2.py::test_a2 - AssertionError: <conftest.DB object at 0x...
    FAILED test_step.py::TestUserHandling::test_modification - assert 0
    ERROR b/test_error.py::test_root
    ============= 3 failed, 2 passed, 1 xfailed, 1 error in 0.12s ==============

``a`` 目录中的两个测试模块看到相同的 ``db`` fixture 实例，而姐妹目录 ``b`` 中的一个测试看不到它。我们当然也可以在该姐妹目录的 ``conftest.py`` 文件中定义一个 ``db`` fixture。请注意，每个 fixture 只有在有实际需要的测试时才会被实例化（除非你使用 "autouse" fixtures，它们总是在执行第一个测试之前执行）。


后处理测试报告 / 失败
---------------------------------------

如果你想后处理测试报告并需要访问执行环境，你可以实现一个在测试 "报告" 对象即将被创建时被调用的钩子。这里我们将所有失败的测试调用写入文件，并访问一个 fixture（如果它被测试使用），以防你想在后处理期间查询/查看它。在我们的例子中，我们只是将一些信息写入 ``failures`` 文件：

.. code-block:: python

    # conftest.py 的内容

    import os.path

    import pytest


    @pytest.hookimpl(wrapper=True, tryfirst=True)
    def pytest_runtest_makereport(item, call):
        # 执行所有其他钩子以获取报告对象
        rep = yield

        # 我们只关注实际失败的测试调用，而不是 setup/teardown
        if rep.when == "call" and rep.failed:
            mode = "a" if os.path.exists("failures") else "w"
            with open("failures", mode, encoding="utf-8") as f:
                # 让我们也访问一个 fixture 只是为了好玩
                if "tmp_path" in item.fixturenames:
                    extra = " ({})".format(item.funcargs["tmp_path"])
                else:
                    extra = ""

                f.write(rep.nodeid + extra + "\n")

        return rep


如果你有失败的测试：

.. code-block:: python

    # test_module.py 的内容
    def test_fail1(tmp_path):
        assert 0


    def test_fail2():
        assert 0

并运行它们：

.. code-block:: pytest

    $ pytest test_module.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 2 items

    test_module.py FF                                                    [100%]

    ================================= FAILURES =================================
    ________________________________ test_fail1 ________________________________

    tmp_path = PosixPath('PYTEST_TMPDIR/test_fail10')

        def test_fail1(tmp_path):
    >       assert 0
    E       assert 0

    test_module.py:2: AssertionError
    ________________________________ test_fail2 ________________________________

        def test_fail2():
    >       assert 0
    E       assert 0

    test_module.py:6: AssertionError
    ========================= short test summary info ==========================
    FAILED test_module.py::test_fail1 - assert 0
    FAILED test_module.py::test_fail2 - assert 0
    ============================ 2 failed in 0.12s =============================

你将有一个 "failures" 文件，其中包含失败的测试 id：

.. code-block:: bash

    $ cat failures
    test_module.py::test_fail1 (PYTEST_TMPDIR/test_fail10)
    test_module.py::test_fail2

在 fixtures 中使测试结果信息可用
-----------------------------------------------------------

.. regendoc:wipe

如果你想使测试结果报告在 fixture finalizers 中可用，这里有一个通过本地插件实现的小示例：

.. code-block:: python

    # conftest.py 的内容
    import pytest
    from pytest import StashKey, CollectReport

    phase_report_key = StashKey[dict[str, CollectReport]]()


    @pytest.hookimpl(wrapper=True, tryfirst=True)
    def pytest_runtest_makereport(item, call):
        # 执行所有其他钩子以获取报告对象
        rep = yield

        # 存储调用的每个阶段的测试结果，可以是 "setup"、"call"、"teardown"
        item.stash.setdefault(phase_report_key, {})[rep.when] = rep

        return rep


    @pytest.fixture
    def something(request):
        yield
        # request.node 是一个 "item"，因为我们使用默认的 "function" 作用域
        report = request.node.stash[phase_report_key]
        if report["setup"].failed:
            print("设置测试失败", request.node.nodeid)
        elif report["setup"].skipped:
            print("设置测试跳过", request.node.nodeid)
        elif ("call" not in report) or report["call"].failed:
            print("执行测试失败或跳过", request.node.nodeid)


如果你有失败的测试：

.. code-block:: python

    # test_module.py 的内容

    import pytest


    @pytest.fixture
    def other():
        assert 0


    def test_setup_fails(something, other):
        pass


    def test_call_fails(something):
        assert 0


    def test_fail2():
        assert 0

并运行它：

.. code-block:: pytest

    $ pytest -s test_module.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 3 items

    test_module.py E设置测试失败 test_module.py::test_setup_fails
    F执行测试失败或跳过 test_module.py::test_call_fails
    F

    ================================== ERRORS ==================================
    ____________________ ERROR at setup of test_setup_fails ____________________

        @pytest.fixture
        def other():
    >       assert 0
    E       assert 0

    test_module.py:7: AssertionError
    ================================= FAILURES =================================
    _____________________________ test_call_fails ______________________________

    something = None

        def test_call_fails(something):
    >       assert 0
    E       assert 0

    test_module.py:15: AssertionError
    ________________________________ test_fail2 ________________________________

        def test_fail2():
    >       assert 0
    E       assert 0

    test_module.py:19: AssertionError
    ========================= short test summary info ==========================
    FAILED test_module.py::test_call_fails - assert 0
    FAILED test_module.py::test_fail2 - assert 0
    ERROR test_module.py::test_setup_fails - assert 0
    ======================== 2 failed, 1 error in 0.12s ========================

你会看到 fixture finalizers 可以使用精确的报告信息。

.. _pytest current test env:

``PYTEST_CURRENT_TEST`` 环境变量
--------------------------------------------



有时测试会话可能会卡住，并且可能没有简单的方法来找出哪个测试卡住了，例如，如果 pytest 在安静模式下运行（:option:`-q`）或你无法访问控制台输出。如果问题只是偶尔发生，这是一个特别的问题，即著名的 "不稳定" 测试。

``pytest`` 在运行测试时设置 :envvar:`PYTEST_CURRENT_TEST` 环境变量，如果需要，进程监控工具或 :pypi:`psutil` 等库可以检查该变量以发现哪个测试卡住了：

.. code-block:: python

    import psutil

    for pid in psutil.pids():
        environ = psutil.Process(pid).environ()
        if "PYTEST_CURRENT_TEST" in environ:
            print(f'pytest 进程 {pid} 正在运行: {environ["PYTEST_CURRENT_TEST"]}')

在测试会话期间，pytest 会将 ``PYTEST_CURRENT_TEST`` 设置为当前测试 :ref:`nodeid <nodeids>` 和当前阶段，可以是 ``setup``、``call`` 或 ``teardown``。

例如，当从 ``foo_module.py`` 运行名为 ``test_foo`` 的单个测试函数时，``PYTEST_CURRENT_TEST`` 将被设置为：

#. ``foo_module.py::test_foo (setup)``
#. ``foo_module.py::test_foo (call)``
#. ``foo_module.py::test_foo (teardown)``

按此顺序。

.. note::

    ``PYTEST_CURRENT_TEST`` 的内容旨在供人类阅读，实际格式可以在版本之间（即使是错误修复）更改，因此不应依赖它进行脚本编写或自动化。

.. _freezing-pytest:

冻结 pytest
---------------

如果你使用 `PyInstaller <https://pyinstaller.readthedocs.io>`_ 等工具冻结应用程序，以便将其分发给最终用户，最好也将你的测试运行器打包并使用冻结的应用程序运行你的测试。这样，可以尽早检测到诸如依赖项未包含在可执行文件中的打包错误，同时还可以允许你向用户发送测试文件，以便他们可以在自己的机器上运行它们，这对于获取难以重现的错误的更多信息可能很有用。

幸运的是，最近的 ``PyInstaller`` 版本已经为 pytest 提供了自定义钩子，但如果你使用其他工具来冻结可执行文件，例如 ``cx_freeze`` 或 ``py2exe``，你可以使用 ``pytest.freeze_includes()`` 来获取所有内部 pytest 模块的完整列表。但是，如何配置工具以找到内部模块因工具而异。

你可以通过程序启动期间的巧妙参数处理，使冻结程序作为 pytest 运行器工作，而不是将 pytest 运行器冻结为单独的可执行文件。这允许你有一个单一的可执行文件，这通常更方便。请注意，pytest 用于插件发现的机制（:ref:`入口点 <pip-installable plugins>`）不适用于冻结的可执行文件，因此 pytest 无法自动找到任何第三方插件。要包含 ``pytest-timeout`` 等第三方插件，必须显式导入它们并传递给 pytest.main。

.. code-block:: python

    # app_main.py 的内容
    import sys

    import pytest_timeout  # 第三方插件

    if len(sys.argv) > 1 and sys.argv[1] == "--pytest":
        import pytest

        sys.exit(pytest.main(sys.argv[2:], plugins=[pytest_timeout]))
    else:
        # 正常的应用程序执行：此时 argv 可以像通常一样由你选择的参数解析库解析
        ...


这使你可以使用标准 ``pytest`` 命令行选项执行测试：

.. code-block:: bash

    ./app_main --pytest --verbose --tb=long --junit=xml=results.xml test-suite/
