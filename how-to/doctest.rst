.. _doctest:

如何运行 doctests
=========================================================

默认情况下，所有匹配 ``test*.txt`` 模式的文件都会通过 Python 标准的 :mod:`doctest` 模块运行。你可以通过执行以下命令来更改模式：

.. code-block:: bash

    pytest --doctest-glob="*.rst"

在命令行上。:option:`--doctest-glob` 可以在命令行上多次给出。

如果你有一个像这样的文本文件：

.. code-block:: text

    # test_example.txt 的内容

    hello this is a doctest
    >>> x = 3
    >>> x
    3

然后你可以直接调用 ``pytest``：

.. code-block:: pytest

    $ pytest
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 1 item

    test_example.txt .                                                   [100%]

    ============================ 1 passed in 0.12s =============================

默认情况下，pytest 将收集 ``test*.txt`` 文件以查找 doctest 指令，但你可以使用 :option:`--doctest-glob` 选项（允许多次）传递其他 glob 模式。

除了文本文件，你还可以直接从类和函数的 docstrings 中执行 doctests，包括测试模块：

.. code-block:: python

    # mymodule.py 的内容
    def something():
        """a doctest in a docstring
        >>> something()
        42
        """
        return 42

.. code-block:: bash

    $ pytest --doctest-modules
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 2 items

    mymodule.py .                                                        [ 50%]
    test_example.txt .                                                   [100%]

    ============================ 2 passed in 0.12s =============================

你可以通过将这些更改放入配置文件来使它们在项目中永久生效：

.. code-block:: toml

    # pytest.toml 的内容
    [pytest]
    addopts = ["--doctest-modules"]

编码
--------

默认编码是 **UTF-8**，但你可以使用 :confval:`doctest_encoding` 配置选项来指定这些 doctest 文件将使用的编码：

.. tab:: toml

    .. code-block:: toml

        [pytest]
        doctest_encoding = "latin1"

.. tab:: ini

    .. code-block:: ini

        [pytest]
        doctest_encoding = latin1

.. _using doctest options:

使用 'doctest' 选项
-----------------------

Python 标准的 :mod:`doctest` 模块提供了一些 :ref:`选项 <python:option-flags-and-directives>` 来配置 doctest 测试的严格性。在 pytest 中，你可以使用配置文件启用这些标志。

例如，要使 pytest 忽略尾随空格并忽略冗长的异常堆栈跟踪，你可以这样写：

.. tab:: toml

    .. code-block:: toml

        [pytest]
        doctest_optionflags = ["NORMALIZE_WHITESPACE", "IGNORE_EXCEPTION_DETAIL"]

.. tab:: ini

    .. code-block:: ini

        [pytest]
        doctest_optionflags = NORMALIZE_WHITESPACE IGNORE_EXCEPTION_DETAIL

或者，可以通过 doc test 本身的内联注释启用选项：

.. code-block:: rst

    >>> something_that_raises()  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ValueError: ...

pytest 还引入了新选项：

* ``ALLOW_UNICODE``：启用时，从预期 doctest 输出中的 unicode 字符串中剥离 ``u`` 前缀。这允许 doctests 在 Python 2 和 Python 3 中不变地运行。

* ``ALLOW_BYTES``：类似地，从预期 doctest 输出中的字节字符串中剥离 ``b`` 前缀。

* ``NUMBER``：启用时，浮点数只需要匹配到你在预期 doctest 输出中写入的精度。数字使用 :func:`pytest.approx` 进行比较，相对容差等于精度。例如，当比较 ``3.14`` 到 ``pytest.approx(math.pi, rel=10**-2)`` 时，以下输出只需要匹配到 2 位小数：

      >>> math.pi
      3.14

  如果你写 ``3.1416`` 那么实际输出需要匹配到大约 4 位小数；以此类推。

  这避免了由于有限的浮点精度导致的假阳性，像这样：

      Expected:
          0.233
      Got:
          0.23300000000000001

  ``NUMBER`` 也支持浮点数列表 —— 事实上，它匹配出现在输出中任何位置的浮点数，甚至在字符串内部！这意味着在配置文件中全局启用 ``doctest_optionflags`` 可能不合适。

  .. versionadded:: 5.1


失败时继续
-------------------

默认情况下，pytest 将只报告给定 doctest 的第一个失败。如果你想在出现失败时继续测试，请执行：

.. code-block:: bash

    pytest --doctest-modules --doctest-continue-on-failure


输出格式
-------------

你可以通过使用标准 doctest 模块的格式选项之一来更改失败时的 diff 输出格式（参见 :data:`python:doctest.REPORT_UDIFF`、:data:`python:doctest.REPORT_CDIFF`、:data:`python:doctest.REPORT_NDIFF`、:data:`python:doctest.REPORT_ONLY_FIRST_FAILURE`）：

.. code-block:: bash

    pytest --doctest-modules --doctest-report none
    pytest --doctest-modules --doctest-report udiff
    pytest --doctest-modules --doctest-report cdiff
    pytest --doctest-modules --doctest-report ndiff
    pytest --doctest-modules --doctest-report only_first_failure


pytest 特定功能
------------------------

提供了一些功能以使编写 doctests 更容易或与现有测试套件更好地集成。但是请记住，通过使用这些功能，你的 doctests 将与标准 ``doctests`` 模块不兼容。

使用 fixtures
^^^^^^^^^^^^^^

可以使用 ``getfixture`` 帮助器使用 fixtures：

.. code-block:: text

    # example.rst 的内容
    >>> tmp = getfixture('tmp_path')
    >>> ...
    >>>

请注意，fixture 需要定义在 pytest 可见的地方，例如 `conftest.py` 文件或插件；包含 docstrings 的普通 python 文件通常不会被扫描以查找 fixtures，除非通过 :confval:`python_files` 显式配置。

此外，:ref:`usefixtures <usefixtures>` 标记和标记为 :ref:`autouse <autouse>` 的 fixtures 在执行文本 doctest 文件时也受支持。


.. _`doctest_namespace`:

'doctest_namespace' fixture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``doctest_namespace`` fixture 可用于将项目注入到你的 doctests 运行的命名空间中。它旨在在你自己的 fixtures 中使用，为使用它们的测试提供上下文。

``doctest_namespace`` 是一个标准的 ``dict`` 对象，你可以将希望出现在 doctest 命名空间中的对象放入其中：

.. code-block:: python

    # conftest.py 的内容
    import pytest
    import numpy


    @pytest.fixture(autouse=True)
    def add_np(doctest_namespace):
        doctest_namespace["np"] = numpy

然后可以直接在你的 doctests 中使用：

.. code-block:: python

    # numpy.py 的内容
    def arange():
        """
        >>> a = np.arange(10)
        >>> len(a)
        10
        """

请注意，像普通的 ``conftest.py`` 一样，fixtures 是在 conftest 所在的目录树中发现的。这意味着如果你将 doctest 放在源代码中，相关的 conftest.py 需要在同一个目录树中。fixtures 不会在兄弟目录树中被发现！

跳过测试
^^^^^^^^^^^^^^

出于可能想要跳过正常测试的相同原因，也可能跳过 doctests 中的测试。

要跳过 doctest 中的单个检查，你可以使用标准的 :data:`doctest.SKIP` 指令：

.. code-block:: python

    def test_random(y):
        """
        >>> random.random()  # doctest: +SKIP
        0.156231223

        >>> 1 + 1
        2
        """

这将跳过第一个检查，但不是第二个。

pytest 还允许在 doctests 中使用标准的 pytest 函数 :func:`pytest.skip` 和 :func:`pytest.xfail`，这可能很有用，因为你可以根据外部条件跳过/预期失败测试：


.. code-block:: text

    >>> import sys, pytest
    >>> if sys.platform.startswith('win'):
    ...     pytest.skip('此 doctest 在 Windows 上不起作用')
    ...
    >>> import fcntl
    >>> ...

然而，不鼓励使用这些函数，因为它会降低 docstring 的可读性。

.. note::

    :func:`pytest.skip` 和 :func:`pytest.xfail` 的行为取决于 doctests 是在 Python 文件（在 docstrings 中）还是在包含与文本混合的 doctests 的文本文件中：

    * Python 模块（docstrings）：函数只在特定 docstring 中起作用，让同一模块中的其他 docstrings 正常执行。

    * 文本文件：函数将跳过/xfail 整个文件的剩余检查。


替代方案
------------

虽然内置的 pytest 支持提供了使用 doctests 的良好功能集，但如果你广泛使用它们，你可能会对这些外部包感兴趣，它们增加了更多功能并包括 pytest 集成：

* `pytest-doctestplus <https://github.com/scientific-python/pytest-doctestplus>`__：提供高级的 doctest 支持并启用对 reStructuredText (".rst") 文件的测试。

* `Sybil <https://sybil.readthedocs.io>`__：提供一种通过从文档源解析它们并在正常测试运行中评估解析的示例来测试文档中的示例的方法。
