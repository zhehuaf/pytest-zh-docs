
.. _`python collection`:

更改标准 (Python) 测试发现
=================================================

在收集期间忽略路径
-----------------------------------

你可以通过在 CLI 上传递 :option:`--ignore=path` 选项来轻松忽略某些测试目录和模块。``pytest`` 支持多个 ``--ignore`` 选项。示例：

.. code-block:: text

    tests/
    |-- example
    |   |-- test_example_01.py
    |   |-- test_example_02.py
    |   '-- test_example_03.py
    |-- foobar
    |   |-- test_foobar_01.py
    |   |-- test_foobar_02.py
    |   '-- test_foobar_03.py
    '-- hello
        '-- world
            |-- test_world_01.py
            |-- test_world_02.py
            '-- test_world_03.py

现在，如果你使用 ``--ignore=tests/foobar/test_foobar_03.py --ignore=tests/hello/`` 调用 ``pytest``，你会看到 ``pytest`` 只收集不匹配指定模式的测试模块：

.. code-block:: pytest

    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-5.x.y, py-1.x.y, pluggy-0.x.y
    rootdir: $REGENDOC_TMPDIR, inifile:
    collected 5 items

    tests/example/test_example_01.py .                                   [ 20%]
    tests/example/test_example_02.py .                                   [ 40%]
    tests/example/test_example_03.py .                                   [ 60%]
    tests/foobar/test_foobar_01.py .                                     [ 80%]
    tests/foobar/test_foobar_02.py .                                     [100%]

    ========================= 5 passed in 0.02 seconds =========================

:option:`--ignore-glob` 选项允许基于 Unix shell 风格的通配符忽略测试文件路径。如果你想排除以 ``_01.py`` 结尾的测试模块，使用 :option:`--ignore-glob='*_01.py'` 执行 ``pytest``。

在收集期间取消选择测试
-------------------------------------

可以在收集期间通过传递 :option:`--deselect=item` 选项来单独取消选择测试。例如，假设 ``tests/foobar/test_foobar_01.py`` 包含 ``test_a`` 和 ``test_b``。你可以通过使用 ``--deselect=tests/foobar/test_foobar_01.py::test_a`` 调用 ``pytest`` 来运行 ``tests/`` 内*除了* ``tests/foobar/test_foobar_01.py::test_a`` 之外的所有测试。``pytest`` 支持多个 ``--deselect`` 选项。

.. _duplicate-paths:

保留从命令行指定的重复路径
----------------------------------------------------

``pytest`` 的默认行为是忽略从命令行指定的重复路径。示例：

.. code-block:: pytest

    pytest path_a path_a

    ...
    collected 1 item
    ...

只收集一次测试。

要收集重复的测试，请在 CLI 上使用 :option:`--keep-duplicates` 选项。示例：

.. code-block:: pytest

    pytest --keep-duplicates path_a path_a

    ...
    collected 2 items
    ...


更改目录递归
-----------------------------------------------------

你可以在配置文件中设置 :confval:`norecursedirs` 选项：

.. code-block:: toml

    # pytest.toml 的内容
    [pytest]
    norecursedirs = [".svn", "_build", "tmp*"]

这将告诉 ``pytest`` 不要递归进入典型的 subversion 或 sphinx-build 目录或任何以 ``tmp`` 为前缀的目录。

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
