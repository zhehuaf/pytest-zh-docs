历史说明
================

本页面列出了 pytest 之前版本中多年来已发生变化的功能或行为。它们作为历史记录保留在这里，以便查看旧代码的用户可以找到相关的文档。


.. _marker-revamp:

标记器的重构和迭代
---------------------------

.. versionchanged:: 3.6

pytest 的标记器实现传统上通过简单地更新函数的 ``__dict__`` 属性来累积添加标记器。因此，标记器会以令人惊讶的方式无意地沿类层次结构传递。此外，检索它们的 API 不一致，因为来自参数化的标记器存储方式与使用 ``@pytest.mark`` 装饰器和通过 ``node.add_marker`` 添加的标记器不同。

这种状态使得在没有深入了解内部机制的情况下几乎不可能正确使用标记器数据，导致在更高级的用法中出现微妙且难以理解的错误。

根据标记器的声明/修改方式，你可能会得到一个可能包含来自兄弟类的标记器的 ``MarkerInfo``，当标记来自参数化或 ``node.add_marker`` 调用时的 ``MarkDecorators``，丢弃先前的标记。此外，``MarkerInfo`` 表现得像单个标记，而实际上它代表了对多个同名标记的合并视图。

除此之外，标记器对模块、类和方法/函数的访问方式不一致。事实上，标记器只能在函数中访问，即使它们是在类/模块上声明的。

为了解决初始设计的问题，pytest 3.6 引入了一个新的 API 来访问标记器，提供了 :func:`_pytest.nodes.Node.iter_markers` 方法以一致的方式遍历标记器，并重新设计了内部机制，这解决了初始设计的大量问题。


.. _update marker code:

更新代码
~~~~~~~~~~~~~

旧的 ``Node.get_marker(name)`` 函数被认为已弃用，因为它返回一个内部 ``MarkerInfo`` 对象，该对象包含应用于该节点的所有标记器的合并名称、``*args`` 和 ``**kwargs``。

一般来说，处理标记器有两种场景：

1. 标记器相互覆盖。顺序很重要，但你只想将标记视为单个项目。例如，模块级别的 ``log_level('info')`` 可以被特定测试的 ``log_level('debug')`` 覆盖。

    在这种情况下，使用 ``Node.get_closest_marker(name)``：

    .. code-block:: python

        # 替换这个：
        marker = item.get_marker("log_level")
        if marker:
            level = marker.args[0]

        # 用这个：
        marker = item.get_closest_marker("log_level")
        if marker:
            level = marker.args[0]

2. 标记器以加法方式组合。例如，``skipif(condition)`` 标记意味着你只想评估所有标记，顺序甚至都不重要。在这里你可能想将标记视为一个集合。

   在这种情况下，遍历每个标记并单独处理它们的 ``*args`` 和 ``**kwargs``。

   .. code-block:: python

        # 替换这个
        skipif = item.get_marker("skipif")
        if skipif:
            for condition in skipif.args:
                # 评估条件
                ...

        # 用这个：
        for skipif in item.iter_markers("skipif"):
            condition = skipif.args[0]
            # 评估条件


如果你不确定或有任何问题，请考虑提交 :issue:`问题 <new>`。

相关问题
~~~~~~~~~~~~~~

以下是新实现修复的问题的非详尽列表：

* 标记器不识别嵌套类 (:issue:`199`)。

* 标记器污染所有相关类 (:issue:`568`)。

* 组合标记 - 参数和关键字参数计算 (:issue:`2897`)。

* ``request.node.get_marker('name')`` 对应用于类的标记返回 ``None`` (:issue:`902`)。

* 应用于参数化的标记存储为 markdecorator (:issue:`2400`)。

* 以向后不兼容的方式修复标记交互 (:issue:`1670`)。

* 重构标记以摆脱当前的"标记传递"机制 (:issue:`2363`)。

* 引入 FunctionDefinition 节点，在 generate_tests 中使用它 (:issue:`2522`)。

* 删除命名标记属性并在项目中收集标记 (:issue:`891`)。

* 来自参数化的 skipif 标记隐藏了模块级别的 skipif 标记 (:issue:`1540`)。

* skipif + 参数化不跳过测试 (:issue:`1296`)。

* 标记传递与继承不兼容 (:issue:`535`)。

更多细节可以在 :pr:`原始 PR <3317>` 中找到。

.. note::

    在未来的主要版本中，我们将引入基于类的标记器，届时标记器将不再仅限于 :py:class:`~pytest.Mark` 的实例。


cache 插件集成到核心中
-------------------------------------



:ref:`核心 cache <cache>` 插件的功能以前作为名为 ``pytest-cache`` 的第三方插件分发。核心插件在命令行选项和 API 使用方面是兼容的，只是你只能存储/接收在测试运行之间可 JSON 序列化的数据。

.. _historical funcargs and pytest.funcargs:

funcargs 和 ``pytest_funcarg__``
---------------------------------



在 2.3 之前的版本中没有 ``@pytest.fixture`` 标记器，你必须使用魔术 ``pytest_funcarg__NAME`` 前缀作为 fixture 工厂。这种方式仍然并继续得到支持，但不再作为主要声明 fixture 函数的方式。


``@pytest.yield_fixture`` 装饰器
-----------------------------------



在 2.10 版本之前，为了使用 ``yield`` 语句执行清理代码，必须使用 ``yield_fixture`` 标记标记 fixture。从 2.10 开始，普通 fixture 可以直接使用 ``yield``，因此不再需要 ``yield_fixture`` 装饰器，它被认为已弃用。


``[pytest]`` 标题在 ``setup.cfg`` 中
--------------------------------------



在 3.0 之前，支持的部分名称是 ``[pytest]``。由于这可能与某些 distutils 命令冲突，现在 ``setup.cfg`` 文件推荐的部分名称是 ``[tool:pytest]``。

请注意，对于 ``pytest.ini`` 和 ``tox.ini`` 文件，部分名称是 ``[pytest]``。


将标记应用于 ``@pytest.mark.parametrize`` 参数
---------------------------------------------------------



在 3.1 版本之前，支持标记值的机制使用以下语法：

.. code-block:: python

    import pytest


    @pytest.mark.parametrize(
        "test_input,expected", [("3+5", 8), ("2+4", 6), pytest.mark.xfail(("6*9", 42))]
    )
    def test_eval(test_input, expected):
        assert eval(test_input) == expected


这是支持该功能的初始 hack，但很快就被证明是不完整的，对于传递函数或应用同名但不同参数的多个标记时失效。

旧语法计划在 pytest-4.0 中移除。


``@pytest.mark.parametrize`` 参数名称作为元组
------------------------------------------------------



在 2.4 之前的版本中，需要将参数名称指定为元组。这仍然有效，但更简单的 ``"name1,name2,..."`` 逗号分隔字符串语法现在被优先推荐，因为它更容易编写且产生的行噪音更少。


setup: 现在是 "autouse fixture"
----------------------------------



在 pytest-2.3 发布之前的开发期间，名称 ``pytest.setup`` 被使用，但在发布之前它被重命名并移动成为通用 fixture 机制的一部分，即 :ref:`autouse fixtures`


.. _string conditions:

字符串条件而非布尔条件
-----------------------------------------



在 pytest-2.4 之前，指定 skipif/xfail 条件的唯一方式是使用字符串：

.. code-block:: python

    import sys


    @pytest.mark.skipif("sys.version_info >= (3,3)")
    def test_function(): ...

在测试函数设置期间，通过调用 ``eval('sys.version_info >= (3,0)', namespace)`` 评估 skipif 条件。命名空间包含所有模块全局变量，以及 ``os`` 和 ``sys`` 作为最低要求。

由于标记器可以自由导入到测试模块之间，pytest-2.4 以来 :ref:`布尔条件 <condition booleans>` 被认为是首选的。使用字符串时，你不仅需要导入标记器，还需要导入标记器使用的所有变量，这违反了封装原则。

将条件指定为字符串的原因是 ``pytest`` 可以仅基于条件字符串报告 skip 条件的摘要。使用布尔条件时，你需要指定一个 ``reason`` 字符串。

请注意，字符串条件将继续得到完全支持，如果你不需要跨模块导入标记器，可以自由使用它们。

``pytest.mark.skipif(conditionstring)`` 或 ``pytest.mark.xfail(conditionstring)`` 中条件字符串的评估在按如下方式构建的命名空间字典中进行：

* 命名空间通过将 ``sys`` 和 ``os`` 模块以及 pytest ``config`` 对象放入其中进行初始化。

* 用应用表达式的测试函数的模块全局变量进行更新。

pytest ``config`` 对象允许你基于你可能添加的测试配置值进行跳过：

.. code-block:: python

    @pytest.mark.skipif("not config.getvalue('db')")
    def test_function(): ...

使用 ``request.config`` 的"布尔条件"等效方式是：

.. code-block:: python

    @pytest.fixture(autouse=True)
    def skip_if_no_db(request):
        if not request.config.getoption("--db", default=False):
            pytest.skip("--db was not specified")


    def test_function():
        pass

.. note::

    ``pytest.config`` 在 pytest 5.0 中被移除。请改用 ``request.config``（通过 ``request`` fixture）或 ``pytestconfig`` fixture。详情请参见 :ref:`pytest.config global deprecated`。

``pytest.set_trace()``
----------------------



在 2.4 版本之前，要在代码中设置断点需要使用 ``pytest.set_trace()``：

.. code-block:: python

    import pytest


    def test_function():
        ...
        pytest.set_trace()  # 调用 PDB 调试器和跟踪


这不再需要了，可以直接使用原生的 ``import pdb;pdb.set_trace()`` 调用。

更多细节请参见 :ref:`breakpoints`。

"compat" 属性
-------------------



通过 ``Node`` 实例访问 ``Module``、``Function``、``Class``、``Instance``、``File`` 和 ``Item`` 长期以来一直被记录为已弃用，但从 pytest ``3.9`` 开始发出警告。

用户应该只 ``import pytest`` 并使用 ``pytest`` 模块访问这些对象。
