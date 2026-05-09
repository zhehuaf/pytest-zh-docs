
.. _`python collection`:

Python 测试收集
=================================================


标准发现机制
----------------------------------------------------

pytest 默认实现以下标准 Python 测试发现：

* 如果未指定参数，则从 :confval:`testpaths` （如果已配置）或当前目录开始收集。或者，命令行参数可用于目录、文件名或节点 ID。
* 递归到目录中，除非它们匹配 :confval:`norecursedirs`。
* 在这些目录中，搜索 ``test_*.py`` 或 ``*_test.py`` 文件，按文件导入名称排序。
* 从这些文件中收集测试项目：

  * ``test`` 前缀在类外部或内部的函数或方法
  * ``Test`` 前缀在类内部的测试类（无 ``__init__`` 方法）

示例会话
--------------------------------------

这是一个简单的示例会话，使用上述约定来收集测试。

.. code-block:: python

    # pythoncollection.py 的内容

    def test_function():
        pass


    class TestClass:
        def test_method(self):
            pass


        def test_anothermethod(self):
            pass

我们可以使用 ``--collect-only`` 选项来演示：

.. code-block:: pytest

    . $ pytest --collect-only pythoncollection.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    configfile: pytest.toml
    collected 3 items

    <Dir pythoncollection.rst-214>
      <Dir CWD>
        <Module pythoncollection.py>
          <Function test_function>
          <Class TestClass>
            <Function test_method>
            <Function test_anothermethod>

    ======================== 3 tests collected in 0.12s ========================

.. _`change naming conventions`:

更改命名约定
-----------------------------------------------------

你可以在 :ref:`configuration file <config file formats>` 中设置 :confval:`python_files`、:confval:`python_classes` 和 :confval:`python_functions` 来配置不同的命名约定。这里有一个例子：

.. code-block:: toml

    # pytest.toml 的内容
    # 示例 1：让 pytest 查找 "check" 而不是 "test"
    [pytest]
    python_files = ["check_*.py"]
    python_classes = ["Check"]
    python_functions = ["*_check"]

这将使 ``pytest`` 查找匹配 ``check_*.py`` glob-pattern 的文件，类中的 ``Check`` 前缀，以及匹配 ``*_check`` 的函数和方法。例如，如果我们有：

.. code-block:: python

    # check_myapp.py 的内容
    class CheckMyApp:
        def simple_check(self):
            pass

        def complex_check(self):
            pass

测试收集将看起来像这样：

.. code-block:: pytest

    $ pytest --collect-only
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    configfile: pytest.toml
    collected 2 items

    <Dir pythoncollection.rst-214>
      <Module check_myapp.py>
        <Class CheckMyApp>
          <Function simple_check>
          <Function complex_check>

    ======================== 2 tests collected in 0.12s ========================

你可以通过在模式之间添加空格来检查多个 glob 模式：

.. code-block:: toml

    # pytest.toml 的内容
    # 示例 2：让 pytest 查找包含 "test" 和 "example" 的文件
    [pytest]
    python_files = ["test_*.py", "example_*.py"]

.. note::

   ``python_functions`` 和 ``python_classes`` 选项对 ``unittest.TestCase`` 测试发现没有影响，因为 pytest 将测试用例方法的发现委托给 unittest 代码。

将命令行参数解释为 Python 包
-----------------------------------------------------

你可以使用 :option:`--pyargs` 选项让 ``pytest`` 尝试将参数解释为 python 包名称，推导出它们的文件系统路径，然后运行测试。例如，如果你安装了 unittest2，你可以输入：

.. code-block:: bash

    pytest --pyargs unittest2.test.test_skipping -q

这将运行相应的测试模块。与其他选项一样，通过配置文件和 :confval:`addopts` 选项你可以更永久地更改此设置：

.. code-block:: toml

    # pytest.toml 的内容
    [pytest]
    addopts = ["--pyargs"]

现在简单的 ``pytest NAME`` 调用将检查 NAME 是否存在作为可导入的包/模块，否则将其视为文件系统路径。

找出收集的内容
-----------------------------------------------

你可以随时查看收集树而不运行测试，像这样：

.. code-block:: pytest

    . $ pytest --collect-only pythoncollection.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    configfile: pytest.toml
    collected 3 items

    <Dir pythoncollection.rst-214>
      <Dir CWD>
        <Module pythoncollection.py>
          <Function test_function>
          <Class TestClass>
            <Function test_method>
            <Function test_anothermethod>

    ======================== 3 tests collected in 0.12s ========================

.. _customizing-test-collection:

自定义测试收集
---------------------------

.. regendoc:wipe

你可以轻松地指示 ``pytest`` 从每个 Python 文件中发现测试：

.. code-block:: toml

    # pytest.toml 的内容
    [pytest]
    python_files = ["*.py"]

然而，许多项目会有一个 ``setup.py`` 他们不想被导入。此外，可能有一些文件只能由特定的 python 版本导入。对于这种情况，你可以通过在 ``conftest.py`` 文件中列出它们来动态定义要忽略的文件：

.. code-block:: python

    # conftest.py 的内容
    import sys

    collect_ignore = ["setup.py"]
    if sys.version_info[0] > 2:
        collect_ignore.append("pkg/module_py2.py")

然后如果你有一个像这样的模块文件：

.. code-block:: python

    # pkg/module_py2.py 的内容
    def test_only_on_python2():
        try:
            assert 0
        except Exception, e:
            pass

和一个像这样的 ``setup.py`` 虚拟文件：

.. code-block:: python

    # setup.py 的内容
    0 / 0  # 如果导入将引发异常

如果你用 Python 2 解释器运行，你将找到那一个测试，并忽略 ``setup.py`` 文件：

.. code-block:: pytest

    #$ pytest --collect-only
    ====== test session starts ======
    platform linux2 -- Python 2.7.10, pytest-2.9.1, py-1.4.31, pluggy-0.3.1
    rootdir: $REGENDOC_TMPDIR, inifile: pytest.ini
    collected 1 items
    <Module 'pkg/module_py2.py'>
      <Function 'test_only_on_python2'>

    ====== 1 tests found in 0.04 seconds ======

如果你用 Python 3 解释器运行，那一个测试和 ``setup.py`` 文件都将被忽略：

.. code-block:: pytest

    $ pytest --collect-only
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    configfile: pytest.toml
    collected 0 items

    ======================= no tests collected in 0.12s ========================

也可以基于 Unix shell 风格的通配符忽略文件，通过将模式添加到 :globalvar:`collect_ignore_glob`。

以下示例 ``conftest.py`` 忽略了文件 ``setup.py``，此外还忽略了在 Python 3 解释器下执行时所有以 ``*_py2.py`` 结尾的文件：

.. code-block:: python

    # conftest.py 的内容
    import sys

    collect_ignore = ["setup.py"]
    if sys.version_info[0] > 2:
        collect_ignore_glob = ["*_py2.py"]

从 pytest 2.6 开始，用户可以通过将布尔值 ``__test__`` 属性设置为 ``False`` 来阻止 pytest 发现以 ``Test`` 开头的类。

.. code-block:: python

    # 不会被识别为测试
    class TestClass:
        __test__ = False

.. note::

   如果你正在处理抽象测试类，并且希望避免为子类手动设置 ``__test__`` 属性，你可以使用一个 mixin 类来自动处理。例如：

   .. code-block:: python

       # 用于处理抽象测试类的 Mixin
       class NotATest:
           def __init_subclass__(cls):
               cls.__test__ = NotATest not in cls.__bases__


       # 抽象测试类
       class AbstractTest(NotATest):
           pass


       # 将被收集为测试的子类
       class RealTest(AbstractTest):
           def test_example(self):
               assert 1 + 1 == 2

   这种方法确保抽象测试类的子类被自动收集，而无需显式设置 ``__test__`` 属性。
