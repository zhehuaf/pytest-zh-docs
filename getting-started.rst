.. _get-started:

开始使用
===================================

.. _`getstarted`:
.. _`installation`:

安装 ``pytest``
----------------------------------------

1. 在命令行中运行以下命令：

.. code-block:: bash

    pip install -U pytest

2. 检查您安装了正确的版本：

.. code-block:: bash

    $ pytest --version
    pytest 9.0.3

.. _`simpletest`:

创建你的第一个测试
----------------------------------------------------------

创建一个名为 ``test_sample.py`` 的新文件，包含一个函数和一个测试：

.. code-block:: python

    # test_sample.py 的内容
    def func(x):
        return x + 1


    def test_answer():
        assert func(3) == 5

测试

.. code-block:: pytest

    $ pytest
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 1 item

    test_sample.py F                                                     [100%]

    ================================= FAILURES =================================
    _______________________________ test_answer ________________________________

        def test_answer():
    >       assert func(3) == 5
    E       assert 4 == 5
    E        +  where 4 = func(3)

    test_sample.py:6: AssertionError
    ========================= short test summary info ==========================
    FAILED test_sample.py::test_answer - assert 4 == 5
    ============================ 1 failed in 0.12s =============================

``[100%]`` 指的是运行所有测试用例的整体进度。完成后，pytest 显示失败报告，因为 ``func(3)`` 没有返回 ``5``。

.. note::

    你可以使用 ``assert`` 语句来验证测试期望。pytest 的 :ref:`高级断言内省 <python:assert>` 将智能地报告断言表达式的中间值，这样你可以避免许多 :ref:`JUnit 遗留方法的名称 <testcase-objects>`。

运行多个测试
----------------------------------------------------------

``pytest`` 将运行当前目录及其子目录中所有形式为 ``test_*.py`` 或 ``*_test.py`` 的文件。更一般地说，它遵循 :ref:`标准测试发现规则 <test discovery>`。


断言某个异常被抛出
--------------------------------------------------------------

使用 :ref:`raises <assertraises>` 辅助函数来断言某些代码抛出异常：

.. code-block:: python

    # test_sysexit.py 的内容
    import pytest


    def f():
        raise SystemExit(1)


    def test_mytest():
        with pytest.raises(SystemExit):
            f()

以"安静"报告模式执行测试函数：

.. code-block:: pytest

    $ pytest -q test_sysexit.py
    .                                                                    [100%]
    1 passed in 0.12s

.. note::

    在本示例及后续示例中，``-q/--quiet`` 标志保持输出简洁。

参见 :ref:`assertraises` 了解关于预期异常的更多详细信息。

在类中分组多个测试
--------------------------------------------------------------

.. regendoc:wipe

一旦你开发了多个测试，你可能希望将它们分组到一个类中。pytest 使得创建一个包含多个测试的类变得容易：

.. code-block:: python

    # test_class.py 的内容
    class TestClass:
        def test_one(self):
            x = "this"
            assert "h" in x

        def test_two(self):
            x = "hello"
            assert hasattr(x, "check")

``pytest`` 按照其 :ref:`Python 测试发现约定 <test discovery>` 发现所有测试，因此它找到两个 ``test_`` 前缀的函数。不需要继承任何东西，但确保你的类以 ``Test`` 开头，否则该类将被跳过。我们可以通过传递文件名来简单地运行该模块：

.. code-block:: pytest

    $ pytest -q test_class.py
    .F                                                                   [100%]
    ================================= FAILURES =================================
    ____________________________ TestClass.test_two ____________________________

    self = <test_class.TestClass object at 0xdeadbeef0001>

        def test_two(self):
            x = "hello"
    >       assert hasattr(x, "check")
    E       AssertionError: assert False
    E        +  where False = hasattr('hello', 'check')

    test_class.py:8: AssertionError
    ========================= short test summary info ==========================
    FAILED test_class.py::TestClass::test_two - AssertionError: assert False
    1 failed, 1 passed in 0.12s

第一个测试通过了，第二个失败了。你可以很容易地在断言中看到中间值，以帮助你理解失败的原因。

在类中分组测试有以下好处：

 * 测试组织
 * 仅在该特定类中共享测试的 fixtures
 * 在类级别应用标记，并使它们隐式应用于所有测试

在类中分组测试时需要注意的一点是，每个测试都有类的唯一实例。
让每个测试共享相同的类实例将对测试隔离非常不利，并会促进不良的测试实践。
这在下面概述：

.. regendoc:wipe

.. code-block:: python

    # test_class_demo.py 的内容
    class TestClassDemoInstance:
        value = 0

        def test_one(self):
            self.value = 1
            assert self.value == 1

        def test_two(self):
            assert self.value == 1


.. code-block:: pytest

    $ pytest -k TestClassDemoInstance -q
    .F                                                                   [100%]
    ================================= FAILURES =================================
    ______________________ TestClassDemoInstance.test_two ______________________

    self = <test_class_demo.TestClassDemoInstance object at 0xdeadbeef0002>

        def test_two(self):
    >       assert self.value == 1
    E       assert 0 == 1
    E        +  where 0 = <test_class_demo.TestClassDemoInstance object at 0xdeadbeef0002>.value

    test_class_demo.py:9: AssertionError
    ========================= short test summary info ==========================
    FAILED test_class_demo.py::TestClassDemoInstance::test_two - assert 0 == 1
    1 failed, 1 passed in 0.12s

请注意，在类级别添加的属性是*类属性*，因此它们将在测试之间共享。

使用 pytest.approx 比较浮点数值
--------------------------------------------------------------

``pytest`` 还提供了许多实用程序，使编写测试更容易。
例如，你可以使用 :func:`pytest.approx` 来比较可能有微小舍入误差的浮点数值：

.. code-block:: python

    # test_approx.py 的内容
    import pytest


    def test_sum():
        assert (0.1 + 0.2) == pytest.approx(0.3)

这避免了手动容差检查或使用 ``math.isclose`` 的需要，并且适用于标量、列表和 NumPy 数组。


为功能测试请求唯一的临时目录
--------------------------------------------------------------

``pytest`` 提供 :std:doc:`内置 fixtures/函数参数 <builtin>` 来请求任意资源，比如唯一的临时目录：

.. code-block:: python

    # test_tmp_path.py 的内容
    def test_needsfiles(tmp_path):
        print(tmp_path)
        assert 0

在测试函数签名中列出名称 ``tmp_path``，``pytest`` 将在执行测试函数调用之前查找并调用 fixture 工厂来创建资源。在测试运行之前，``pytest`` 创建一个每次测试调用唯一的临时目录：

.. code-block:: pytest

    $ pytest -q test_tmp_path.py
    F                                                                    [100%]
    ================================= FAILURES =================================
    _____________________________ test_needsfiles ______________________________

    tmp_path = PosixPath('PYTEST_TMPDIR/test_needsfiles0')

        def test_needsfiles(tmp_path):
            print(tmp_path)
    >       assert 0
    E       assert 0

    test_tmp_path.py:3: AssertionError
    --------------------------- Captured stdout call ---------------------------
    PYTEST_TMPDIR/test_needsfiles0
    ========================= short test summary info ==========================
    FAILED test_tmp_path.py::test_needsfiles - assert 0
    1 failed in 0.12s

关于临时目录处理的更多信息可在 :ref:`临时目录和文件 <tmp_path handling>` 中找到。

使用以下命令找出存在哪些内置 :ref:`pytest fixtures <fixtures>`：

.. code-block:: bash

    pytest --fixtures   # 显示内置和自定义 fixtures

请注意，此命令会省略带有前导 ``_`` 的 fixtures，除非添加 :option:`-v` 选项。

继续阅读
-------------------------------------

查看其他 pytest 资源，帮助你为独特的工作流程自定义测试：

* ":ref:`usage`" 了解命令行调用示例
* ":ref:`existingtestsuite`" 了解如何处理预先存在的测试
* ":ref:`mark`" 了解 ``pytest.mark`` 机制的信息
* ":ref:`fixtures`" 了解如何为测试提供功能基线
* ":ref:`plugins`" 了解如何管理和编写插件
* ":ref:`goodpractices`" 了解 virtualenv 和测试布局

