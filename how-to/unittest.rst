.. _`unittest.TestCase`:
.. _`unittest`:

如何使用基于 ``unittest`` 的测试与 pytest
===============================================

``pytest`` 开箱即用地支持运行 Python ``unittest`` 基础的测试。
它旨在利用现有的基于 ``unittest`` 的测试套件，
使用 pytest 作为测试运行器，并允许增量地调整
测试套件以充分利用 pytest 的功能。

要使用 ``pytest`` 运行现有的 ``unittest`` 风格测试套件，请输入：

.. code-block:: bash

    pytest tests


pytest 将自动在 ``test_*.py`` 或 ``*_test.py`` 文件中收集 ``unittest.TestCase`` 子类及其 ``test`` 方法。

几乎所有 ``unittest`` 功能都受支持：

* :func:`unittest.skip`/:func:`unittest.skipIf` 风格的装饰器
* :meth:`unittest.TestCase.setUp`/:meth:`unittest.TestCase.tearDown`
* :meth:`unittest.TestCase.setUpClass`/:meth:`unittest.TestCase.tearDownClass`
* :func:`unittest.setUpModule`/:func:`unittest.tearDownModule`
* :meth:`unittest.TestCase.subTest`（自版本 ``9.0`` 起）

.. _`load_tests protocol`: https://docs.python.org/3/library/unittest.html#load-tests-protocol

到目前为止，pytest 不支持以下功能：

* `load_tests protocol`_;  

开箱即用的好处
-----------------------

通过使用 pytest 运行测试套件，你可以利用多项功能，
在大多数情况下无需修改现有代码：

* 获取 :ref:`更详细的回溯 <tbreportdemo>`；
* :ref:`标准输出和标准错误 <captures>` 捕获；
* 使用 :option:`-k` 和 :option:`-m` 标志的 :ref:`测试选择选项 <select-tests>`；
* :ref:`maxfail`；
* :ref:`--pdb <pdb-option>` 命令行选项用于在测试失败时调试
  （参见 :ref:`下方注释 <pdb-unittest-note>`）；
* 使用 :pypi:`pytest-xdist` 插件将测试分发到多个 CPU；
* 使用 :ref:`普通 assert 语句 <assert>` 代替 ``self.assert*`` 函数
  （:pypi:`unittest2pytest` 在这方面非常有帮助）；


在 ``unittest.TestCase`` 子类中的 pytest 功能
---------------------------------------------------

以下 pytest 功能在 ``unittest.TestCase`` 子类中有效：

* :ref:`标记 <mark>`: :ref:`skip <skip>`、:ref:`skipif <skipif>`、:ref:`xfail <xfail>`；
* :ref:`自动使用 fixtures <mixing-fixtures>`；

以下 pytest 功能**不起作用**，可能永远不会起作用，因为设计哲学不同：

* :ref:`Fixtures <fixture>`（除了 ``autouse`` fixtures，参见 :ref:`下方 <mixing-fixtures>`）；
* :ref:`参数化 <parametrize>`；
* :ref:`自定义 hooks <writing-plugins>`；


第三方插件可能会或可能不会很好地工作，具体取决于插件和测试套件。

.. _mixing-fixtures:

使用标记将 pytest fixtures 混合到 ``unittest.TestCase`` 子类中
------------------------------------------------------------------------

使用 ``pytest`` 运行 unittest 允许你使用其
:ref:`fixture 机制 <fixture>` 与 ``unittest.TestCase`` 风格的测试。假设你至少已经浏览过 pytest fixture 功能，
让我们快速开始一个示例，集成一个 pytest ``db_class`` fixture，
设置一个类缓存的数据库对象，然后从 unittest 风格的测试中引用它：

.. code-block:: python

    # conftest.py 的内容

    # 我们在下面定义一个 fixture 函数，它将通过
    # 从测试中引用其名称来"使用"

    import pytest


    @pytest.fixture(scope="class")
    def db_class(request):
        class DummyDB:
            pass

        # 在调用测试上下文中设置类属性
        request.cls.db = DummyDB()

这定义了一个 fixture 函数 ``db_class`` —— 如果使用的话 ——
每个测试类调用一次，并将类级别的 ``db`` 属性设置为 ``DummyDB`` 实例。
fixture 函数通过接收一个特殊的 ``request`` 对象来实现这一点，该对象提供对 :ref:`请求测试上下文 <request-context>` 的访问，
例如 ``cls`` 属性，表示使用 fixture 的类。
这种架构将 fixture 编写与实际测试代码解耦，并允许通过最小引用（fixture 名称）来重用 fixture。
所以让我们使用我们的 fixture 定义编写一个实际的 ``unittest.TestCase`` 类：

.. code-block:: python

    # test_unittest_db.py 的内容

    import unittest

    import pytest


    @pytest.mark.usefixtures("db_class")
    class MyTest(unittest.TestCase):
        def test_method1(self):
            assert hasattr(self, "db")
            assert 0, self.db  # 为演示目的而失败

        def test_method2(self):
            assert 0, self.db  # 为演示目的而失败

``@pytest.mark.usefixtures("db_class")`` 类装饰器确保 pytest fixture 函数 ``db_class`` 每个类调用一次。
由于故意失败的断言语句，我们可以在回溯中查看 ``self.db`` 值：

.. code-block:: pytest

    $ pytest test_unittest_db.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 2 items

    test_unittest_db.py FF                                               [100%]

    ================================= FAILURES =================================
    ___________________________ MyTest.test_method1 ____________________________

    self = <test_unittest_db.MyTest testMethod=test_method1>

        def test_method1(self):
            assert hasattr(self, "db")
    >       assert 0, self.db  # 为演示目的而失败
            ^^^^^^^^^^^^^^^^^
    E       AssertionError: <conftest.db_class.<locals>.DummyDB object at 0xdeadbeef0001>
    E       assert 0

    test_unittest_db.py:11: AssertionError
    ___________________________ MyTest.test_method2 ____________________________

    self = <test_unittest_db.MyTest testMethod=test_method2>

        def test_method2(self):
    >       assert 0, self.db  # 为演示目的而失败
            ^^^^^^^^^^^^^^^^^
    E       AssertionError: <conftest.db_class.<locals>.DummyDB object at 0xdeadbeef0001>
    E       assert 0

    test_unittest_db.py:14: AssertionError
    ========================= short test summary info ==========================
    FAILED test_unittest_db.py::MyTest::test_method1 - AssertionError: <conft...
    FAILED test_unittest_db.py::MyTest::test_method2 - AssertionError: <conft...
    ============================ 2 failed in 0.12s =============================

这个默认的 pytest 回溯显示两个测试方法共享相同的 ``self.db`` 实例，这是我们在上面编写类范围 fixture 函数时的意图。


使用 autouse fixtures 和访问其他 fixtures
---------------------------------------------------

虽然通常最好显式声明测试所需的 fixtures，但有时你可能希望有在特定上下文中自动使用的 fixtures。
毕竟，传统的 unittest 设置风格规定了这种隐式 fixture 编写，你可能已经习惯了或喜欢它。

你可以用 ``@pytest.fixture(autouse=True)`` 标记 fixture 函数，并在你希望使用它的上下文中定义 fixture 函数。
让我们看一个 ``initdir`` fixture，它使 ``TestCase`` 类的所有测试方法在带有预初始化 ``samplefile.ini`` 的临时目录中执行。
我们的 ``initdir`` fixture 本身使用 pytest 内置的 :fixture:`tmp_path` fixture 来委托创建每个测试的临时目录：

.. code-block:: python

    # test_unittest_cleandir.py 的内容
    import unittest

    import pytest


    class MyTest(unittest.TestCase):
        @pytest.fixture(autouse=True)
        def initdir(self, tmp_path, monkeypatch):
            monkeypatch.chdir(tmp_path)  # 更改为 pytest 提供的临时目录
            tmp_path.joinpath("samplefile.ini").write_text("# testdata", encoding="utf-8")

        def test_method(self):
            with open("samplefile.ini", encoding="utf-8") as f:
                s = f.read()
            assert "testdata" in s

由于 ``autouse`` 标志，``initdir`` fixture 函数将用于定义它的类的所有方法。
这是在类上使用 ``@pytest.mark.usefixtures("initdir")`` 标记的快捷方式，如上一个示例所示。

运行此测试模块 ...：

.. code-block:: pytest

    $ pytest -q test_unittest_cleandir.py
    .                                                                    [100%]
    1 passed in 0.12s

... 给我们一个通过的测试，因为 ``initdir`` fixture 函数在 ``test_method`` 之前执行。

.. note::

   ``unittest.TestCase`` 方法不能直接接收 fixture 参数，因为实现这一点可能会损害运行一般 unittest.TestCase 测试套件的能力。

   上面的 ``usefixtures`` 和 ``autouse`` 示例应该有助于将 pytest fixtures 混合到 unittest 套件中。

   你也可以逐渐从 ``unittest.TestCase`` 的子类转移，使用 *普通断言*，
   然后逐步开始受益于完整的 pytest 功能集。

.. _pdb-unittest-note:

.. note::

    由于两个框架之间的架构差异，基于 ``unittest`` 的测试的设置和拆卸在测试的 ``call`` 阶段执行，而不是在 ``pytest`` 的标准 ``setup`` 和 ``teardown`` 阶段。
    在某些情况下理解这一点很重要，特别是在处理错误时。例如，如果基于 ``unittest`` 的套件在设置期间出现错误，pytest 将不会在其 ``setup`` 阶段报告任何错误，而是在 ``call`` 期间引发错误。
