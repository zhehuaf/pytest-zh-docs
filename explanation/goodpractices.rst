.. highlight:: python
.. _`goodpractices`:

良好集成实践
=================================================

使用 pip 安装包
-------------------------------------------------

对于开发，我们建议你使用 :mod:`venv` 创建虚拟环境，使用 :doc:`pip:index` 安装你的应用程序及其任何依赖项，以及 ``pytest`` 包本身。这可以确保你的代码和依赖项与系统 Python 安装隔离。

在仓库根目录中创建一个 ``pyproject.toml`` 文件，如 :doc:`packaging:tutorials/packaging-projects` 中所述。前几行应该如下所示：

.. code-block:: toml

    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"

    [project]
    name = "PACKAGENAME"
    version = "PACKAGEVERSION"

其中 ``PACKAGENAME`` 和 ``PACKAGEVERSION`` 分别是你的包的名称和版本。

然后你可以从同一目录运行以下命令以"可编辑"模式安装你的包：

.. code-block:: bash

    pip install -e .

这允许你更改源代码（包括测试和应用程序）并随时重新运行测试。

.. _`test discovery`:
.. _`Python test discovery`:

Python 测试发现约定
-------------------------------------------------

``pytest`` 实现了以下标准测试发现：

* 如果未指定参数，则从 :confval:`testpaths`\（如果已配置）或当前目录开始收集。或者，命令行参数可用于目录、文件名或节点 ID 的任意组合。
* 递归进入目录，除非它们匹配 :confval:`norecursedirs`。
* 在这些目录中，搜索由其 `test package name`_ 导入的 ``test_*.py`` 或 ``*_test.py`` 文件。
* 从这些文件中收集测试项：

  * 类外的 ``test`` 前缀测试函数或方法。
  * 类内的 ``test`` 前缀测试函数或方法，类名以 ``Test`` 为前缀（不含 ``__init__`` 方法）。使用 ``@staticmethod`` 和 ``@classmethods`` 装饰的方法也被考虑。

有关如何自定义测试发现的示例，请参见 :doc:`/example/pythoncollection`。

在 Python 模块内，``pytest`` 还使用标准的 :ref:`unittest.TestCase <unittest.TestCase>` 子类化技术发现测试。


.. _`test layout`:

选择测试布局
----------------------

``pytest`` 支持两种常见的测试布局：

应用程序代码外的测试
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

将测试放入实际应用程序代码之外的额外目录可能很有用，如果你有很多功能测试或出于其他原因想将测试与实际应用程序代码分开（通常是个好主意）：

.. code-block:: text

    pyproject.toml
    src/
        mypkg/
            __init__.py
            app.py
            view.py
    tests/
        test_app.py
        test_view.py
        ...

这有以下好处：

* 在执行 ``pip install .`` 后，你的测试可以针对已安装版本运行。
* 在执行 ``pip install --editable .`` 后，你的测试可以通过可编辑安装针对本地副本运行。

对于新项目，我们推荐使用 ``importlib`` :ref:`import mode <import-modes>`\（有关详细解释，请参见 which-import-mode_）。为此，将以下内容添加到你的配置文件中：

.. code-block:: toml

    # pytest.toml 的内容
    [pytest]
    addopts = ["--import-mode=importlib"]

.. _src-layout:

一般来说，但特别是如果你使用默认导入模式 ``prepend``，**强烈**\建议使用 ``src`` 布局。
在这里，你的应用程序根包位于根的子目录中，即 ``src/mypkg/`` 而不是 ``mypkg``。

这种布局可以防止很多常见的陷阱，有很多好处，这在 Ionel Cristian Mărieș 的这篇优秀 `blog post`_ 中有更好的解释。

.. _blog post: https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure>

.. note::

    如果你不使用可编辑安装并使用上述 ``src`` 布局，你需要扩展 Python 的模块文件搜索路径才能直接针对本地副本执行测试。你可以通过设置 ``PYTHONPATH`` 环境变量来临时执行此操作：

    .. code-block:: bash

       PYTHONPATH=src pytest

    或者通过使用 :confval:`pythonpath` 配置变量并添加以下内容到你的配置文件来永久执行此操作：

    .. tab:: toml

        .. code-block:: toml

            [pytest]
            pythonpath = ["src"]

    .. tab:: ini

        .. code-block:: ini

            [pytest]
            pythonpath = src

.. note::

    如果你不使用可编辑安装且不使用 ``src`` 布局（``mypkg`` 直接在根目录中），你可以依靠 Python 默认将当前目录放入 ``sys.path`` 的事实来导入你的包，并运行 ``python -m pytest`` 来直接针对本地副本执行测试。

    有关调用 ``pytest`` 和 ``python -m pytest`` 之间差异的更多信息，请参见 :ref:`pytest vs python -m pytest`。

.. seealso::

    :doc:`packaging:discussions/src-layout-vs-flat-layout`
        Python 打包用户指南讨论了 ``src`` 布局和 ``flat`` 布局之间的权衡。

作为应用程序代码一部分的测试
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

将测试目录内联到你的应用程序包中很有用，如果你希望测试与应用程序模块之间有直接关系，并希望将它们与你的应用程序一起分发：

.. code-block:: text

    pyproject.toml
    [src/]mypkg/
        __init__.py
        app.py
        view.py
        tests/
            __init__.py
            test_app.py
            test_view.py
            ...

在这种方案中，使用 :option:`--pyargs` 选项运行测试很容易：

.. code-block:: bash

    pytest --pyargs mypkg

``pytest`` 将发现 ``mypkg`` 的安装位置并从那里收集测试。

请注意，此布局也可以与前一部分提到的 ``src`` 布局结合使用。


.. note::

    你可以为应用程序使用命名空间包（PEP420），但 pytest 仍将基于 ``__init__.py`` 文件的存在执行 `test package name`_ 发现。如果你使用上述两个推荐的文件系统布局之一但从目录中省略 ``__init__.py`` 文件，它应该可以正常工作。然而，从 "内联测试" 中，你将需要使用绝对导入来访问应用程序代码。

.. _`test package name`:

.. note::

    在 ``prepend`` 和 ``append`` 导入模式下，如果 pytest 在递归文件系统时发现 ``"a/b/test_module.py"`` 测试文件，它按如下方式确定导入名称：

    * 确定 ``basedir``：这是第一个向上（朝向根）不包含 ``__init__.py`` 的目录。如果例如 ``a`` 和 ``b`` 都包含 ``__init__.py`` 文件，则 ``a`` 的父目录将成为 ``basedir``。

    * 执行 ``sys.path.insert(0, basedir)`` 以使测试模块在其完全限定导入名称下可导入。

    * ``import a.b.test_module``，其中路径通过将路径分隔符 ``/`` 转换为 "." 字符来确定。这意味着你必须遵循目录和文件名直接映射到导入名称的约定。

    这种有些演变的导入技术的原因是，在大型项目中，多个测试模块可能相互导入，因此派生规范的导入名称有助于避免诸如测试模块被导入两次之类的意外。

    使用 :option:`--import-mode=importlib` 时，事情不那么复杂，因为 pytest 不需要更改 ``sys.path``，使得事情不那么令人惊讶。


.. _which-import-mode:

选择导入模式
^^^^^^^^^^^^^^^^^^^^^^^

由于历史原因，pytest 默认使用 ``prepend`` :ref:`import mode <import-modes>`，而不是我们为新项目推荐的 ``importlib`` 导入模式。原因在于 ``prepend`` 模式的工作方式：

由于没有包可以派生完整包名称，``pytest`` 会将你的测试文件作为*顶级*模块导入。第一个示例（:ref:`src layout <src-layout>`）中的测试文件将通过将 ``tests/`` 添加到 ``sys.path`` 而作为 ``test_app`` 和 ``test_view`` 顶级模块导入。

与导入模式 ``importlib`` 相比，这导致一个缺点：你的测试文件必须具有**唯一名称**。

如果你需要具有相同名称的测试模块，作为一种解决方法，你可以将 ``__init__.py`` 文件添加到你的 ``tests`` 目录和子目录，将它们更改为包：

.. code-block:: text

    pyproject.toml
    mypkg/
        ...
    tests/
        __init__.py
        foo/
            __init__.py
            test_view.py
        bar/
            __init__.py
            test_view.py

现在 pytest 将把模块加载为 ``tests.foo.test_view`` 和 ``tests.bar.test_view``，允许你拥有相同名称的模块。但现在这引入了一个微妙的问题：为了从 ``tests`` 目录加载测试模块，pytest 将仓库的根目录添加到 ``sys.path`` 前，这产生了一个副作用，即现在 ``mypkg`` 也可导入。

如果你使用像 tox_ 这样的工具在虚拟环境中测试你的包，这是有问题的，因为你希望测试包的*已安装*版本，而不是仓库中的本地代码。

``importlib`` 导入模式没有上述任何缺点，因为在导入测试模块时不会更改 ``sys.path``。


.. _`buildout`: http://www.buildout.org/en/latest/

.. _`use tox`:

tox
---

一旦你完成了工作并希望确保你的实际包通过所有测试，你可能希望查看 :doc:`tox <tox:index>`，这是一个虚拟环境测试自动化工具。``tox`` 帮助你设置具有预定义依赖项的 virtualenv 环境，然后使用选项执行预配置的测试命令。它将针对已安装的包而不是你的源代码检出运行测试，帮助检测打包故障。

不要通过 setuptools 运行
-------------------------

**不推荐使用** setuptools 集成，即你不应使用 ``python setup.py test`` 或 ``pytest-runner``，并且它们将来可能会停止工作。

这是不推荐的，因为它依赖于 setuptools 的已弃用功能，并依赖于破坏 pip 中安全机制的功能。例如 'setup_requires' 和 'tests_require' 绕过 ``pip --require-hashes``。
有关更多信息和迁移说明，请参见 `pytest-runner notice <https://github.com/pytest-dev/pytest-runner#deprecation-notice>`_。
另请参见 `pypa/setuptools#1684 <https://github.com/pypa/setuptools/issues/1684>`_。

setuptools 打算 `移除 test 命令 <https://github.com/pypa/setuptools/issues/931>`_。

使用 flake8-pytest-style 进行检查
---------------------------------

为了确保 pytest 在你的项目中正确使用，使用 `flake8-pytest-style <https://github.com/m-burst/flake8-pytest-style>`_ flake8 插件会很有帮助。

flake8-pytest-style 检查 pytest 代码中的常见错误和编码风格违规，例如 fixtures、测试函数名称和标记的不正确使用。通过使用此插件，你可以在开发过程的早期发现这些错误，并确保你的 pytest 代码一致且易于维护。

flake8-pytest-style 检测到的 lint 列表可以在其 `PyPI 页面 <https://pypi.org/project/flake8-pytest-style/>`_ 上找到。

.. note::

    flake8-pytest-style 不是官方的 pytest 项目。其中一些规则强制执行某些风格选择，例如使用 `@pytest.fixture()` 而不是 `@pytest.fixture`，但你可以配置插件以适应你喜欢的风格。

.. _`strict mode`:

使用 pytest 的严格模式
--------------------------

.. versionadded:: 9.0

Pytest 包含一组使其更严格的配置选项。这些选项默认关闭以兼容或其他原因，但如果你可以的话应该启用它们。

你可以通过设置 :confval:`strict` 配置选项来一次性启用所有严格性选项：

.. tab:: toml

    .. code-block:: toml

        [pytest]
        strict = true

.. tab:: ini

    .. code-block:: ini

        [pytest]
        strict = true

有关它启用的选项及其效果的文档，请参见 :confval:`strict`。

如果 pytest 在未来添加新的严格性选项，它们也会在严格模式下启用。因此，只有在你使用固定/锁定版本的 pytest，或者你想主动采用新添加的严格性选项时，才应该启用严格模式。如果你不想自动获取新选项，可以单独启用选项：

.. tab:: toml

    .. code-block:: toml

        [pytest]
        strict_config = true
        strict_markers = true
        strict_parametrization_ids = true
        strict_xfail = true

.. tab:: ini

    .. code-block:: ini

        [pytest]
        strict_config = true
        strict_markers = true
        strict_parametrization_ids = true
        strict_xfail = true

如果你想使用严格模式但在特定选项上遇到困难，可以单独关闭它：

.. tab:: toml

    .. code-block:: toml

        [pytest]
        strict = true
        strict_parametrization_ids = false

.. tab:: ini

    .. code-block:: ini

        [pytest]
        strict = true
        strict_parametrization_ids = false
