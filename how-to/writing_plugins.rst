.. _plugins:

如何编写插件
==================

本节包含编写你自己的 pytest 插件的信息。

插件包含一个或多个钩子函数。编写钩子 :ref:`解释 <writinghooks>` 了编写钩子函数的基础知识，包括它们的布局和参数。


conftest.py：本地目录插件
----------------------------

本地 ``conftest.py`` 插件包含特定于目录的钩子实现。钩子函数将实现 :ref:`hook 参考 <hook-reference>` 中定义的一个或多个钩子。它们可以使用 :py:func:`pytest.hookimpl` 标记并可选地接受一个 ``tryfirst`` 参数，以影响其他钩子实现的调用顺序。

示例：假设我们有以下目录结构：

.. code-block:: text

    a/conftest.py
    a/test_sub.py
    test_flat.py

.. code-block:: python

    # a/conftest.py 的内容


    def pytest_runtest_setup(item):
        # 只在 a/test_sub.py 中调用，不在 test_flat.py 中调用
        print("setting up", item)


    a/test_sub.py:
        def test_sub():
            pass

    test_flat.py:
        def test_flat():
            pass

你可以这样运行它：::

    pytest test_flat.py --capture=no  # 不会显示 "setting up"
    pytest a/test_sub.py --capture=no  # 会显示 "setting up"

.. note::
    如果你有 ``conftest.py`` 文件不位于 Python 包目录中（即包含 ``__init__.py`` 的目录），那么 "import conftest" 可能是模糊的，因为 ``PYTHONPATH`` 或 ``sys.path`` 上可能还有其他 ``conftest.py`` 文件。因此，对于项目来说，好的做法是将 ``conftest.py`` 放在包范围内，或者从不从 ``conftest.py`` 文件中导入任何东西。

    另见：:ref:`pythonpath`。

.. note::
    由于 pytest 在启动期间发现插件的方式，某些钩子不能在非 :ref:`initial <pluginorder>` 的 conftest.py 文件中实现。有关详细信息，请参阅每个钩子的文档。

编写自己的插件
-----------------

如果你想编写一个插件，有很多现实生活中的例子可以复制：

* 自定义收集示例插件：:ref:`yaml plugin`
* 提供 pytest 自身功能的内置插件
* 许多 :ref:`提供附加功能的外部插件 <plugin-list>`

所有这些插件都实现了 :ref:`hooks <hook-reference>` 和/或 :ref:`fixtures <fixture>` 来扩展和添加功能。

.. note::
    一定要查看出色的
    `cookiecutter-pytest-plugin <https://github.com/pytest-dev/cookiecutter-pytest-plugin>`_
    项目，这是一个用于编写插件的 `cookiecutter 模板 <https://github.com/audreyr/cookiecutter>`_

    该模板提供了一个出色的起点，包括一个工作的插件，
    使用 tox 运行测试，一个全面的 README 文件以及一个
    预配置的入口点。

    一旦你的插件有了一些除你自己以外的满意用户，也请考虑 :ref:`将你的插件贡献给 pytest-dev<submitplugin>`


.. _`setuptools entry points`:
.. _`pip-installable plugins`:

让你的插件可被他人安装
-------------------------------------

如果你想让你的插件对外可用，你可以为你的分发定义一个所谓的入口点，以便 ``pytest`` 找到你的插件模块。入口点是 :std:doc:`打包工具 <packaging:specifications/entry-points>` 提供的一个功能。

pytest 查找 ``pytest11`` 入口点来发现其插件，因此你可以通过在 ``pyproject.toml`` 文件中定义它来使你的插件可用。

.. sourcecode:: toml

    # 示例 ./pyproject.toml 文件
    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"

    [project]
    name = "myproject"
    classifiers = [
        "Framework :: Pytest",
    ]

    [project.entry-points.pytest11]
    myproject = "myproject.pluginmodule"

如果以这种方式安装包，``pytest`` 将加载 ``myproject.pluginmodule`` 作为可以定义 :ref:`hooks <hook-reference>` 的插件。使用 ``pytest --trace-config`` 确认注册

.. note::

    确保在你的 `PyPI 分类器 <https://pypi.org/classifiers/>`_ 列表中包含 ``Framework :: Pytest``
    以便用户轻松找到你的插件。


.. _assertion-rewriting:

断言重写
-----------------

``pytest`` 的一个主要功能是使用普通 assert 语句以及在断言失败时对表达式的详细内省。这是通过 "断言重写" 实现的，它在模块被编译为字节码之前修改解析后的 AST。这是通过在 :pep:`302` 导入钩子，在 ``pytest`` 启动时尽早安装，并在模块被导入时执行此重写。然而，由于我们不希望测试与你在生产中运行的不同的字节码，此钩子只重写测试模块本身（由 :confval:`python_files` 配置选项定义）以及作为插件一部分的任何模块。
任何其他导入的模块都不会被重写，正常的断言行为将发生。

如果你在其他模块中有断言助手，你希望在那里启用断言重写，你需要在模块被导入之前明确要求 ``pytest`` 重写该模块。

.. autofunction:: pytest.register_assert_rewrite
    :noindex:

这在编写使用包创建的 pytest 插件时尤其重要。导入钩子只将 ``conftest.py`` 文件和 ``pytest11`` 入口点中列出的任何模块视为插件。作为示例，考虑以下包::

   pytest_foo/__init__.py
   pytest_foo/plugin.py
   pytest_foo/helper.py

使用以下典型的 ``setup.py`` 片段：

.. code-block:: python

   setup(..., entry_points={"pytest11": ["foo = pytest_foo.plugin"]}, ...)

在这种情况下，只有 ``pytest_foo/plugin.py`` 会被重写。如果 helper 模块也包含需要重写的 assert 语句，它需要在被导入之前被标记为这样。
最简单的方法是在 ``__init__.py`` 模块内部标记它进行重写，当包内的模块被导入时，该模块总是首先被导入。这样 ``plugin.py`` 仍然可以正常导入 ``helper.py``。然后 ``pytest_foo/__init__.py`` 的内容需要如下所示：

.. code-block:: python

   import pytest

   pytest.register_assert_rewrite("pytest_foo.helper")


在测试模块或 conftest 文件中需要/加载插件
-------------------------------------------------------

你可以在测试模块或 ``conftest.py`` 文件中使用 :globalvar:`pytest_plugins` 来要求插件：

.. code-block:: python

    pytest_plugins = ["name1", "name2"]

当测试模块或 conftest 插件被加载时，指定的插件也会被加载。任何模块都可以被指定为插件，包括内部应用程序模块：

.. code-block:: python

    pytest_plugins = "myapp.testsupport.myplugin"

:globalvar:`pytest_plugins` 是递归处理的，因此请注意，在上面的示例中，如果 ``myapp.testsupport.myplugin`` 也声明了 :globalvar:`pytest_plugins`，该变量的内容也会被加载为插件，依此类推。

.. _`requiring plugins in non-root conftests`:

.. note::
    在非根 ``conftest.py`` 文件中使用 :globalvar:`pytest_plugins` 变量来要求插件已被弃用。

    这很重要，因为 ``conftest.py`` 文件实现了每个目录的钩子实现，但一旦插件被导入，它会影响整个目录树。为了避免混淆，在任何不位于测试根目录的 ``conftest.py`` 文件中定义 :globalvar:`pytest_plugins` 已被弃用，并将引发警告。

这种机制使得在应用程序内部甚至外部应用程序之间共享 fixtures 变得容易，而无需使用 :std:doc:`entry point packaging metadata <packaging:guides/creating-and-discovering-plugins>` 技术创建外部插件。

通过 :globalvar:`pytest_plugins` 导入的插件也会自动被标记为断言重写（参见 :func:`pytest.register_assert_rewrite`）。然而，为了使其产生任何效果，模块必须尚未被导入；如果它在 :globalvar:`pytest_plugins` 语句被处理时已经被导入，将会产生警告，并且插件内部的断言不会被重写。要解决此问题，你可以在模块被导入之前自己调用 :func:`pytest.register_assert_rewrite`，或者安排代码延迟导入直到插件被注册之后。


通过名称访问另一个插件
--------------------------------

如果插件想要与来自另一个插件的代码协作，它可以通过插件管理器获得一个引用，如下所示：

.. sourcecode:: python

    plugin = config.pluginmanager.get_plugin("name_of_plugin")

如果你想查看现有插件的名称，请使用 :option:`--trace-config` 选项。


.. _registering-markers:

注册自定义标记
---------------------------

如果你的插件使用任何标记，你应该注册它们，以便它们出现在 pytest 的帮助文本中，并且不会 :ref:`导致虚假警告 <unknown-marks>`。例如，以下插件将为所有用户注册 ``cool_marker`` 和 ``mark_with``：

.. code-block:: python

    def pytest_configure(config):
        config.addinivalue_line("markers", "cool_marker: this one is for cool tests.")
        config.addinivalue_line(
            "markers", "mark_with(arg, arg2): this marker takes arguments."
        )


测试插件
---------------

pytest 带有一个名为 ``pytester`` 的插件，可帮助你为插件代码编写测试。该插件默认禁用，因此你需要先启用它才能使用。

你可以通过在测试目录的 ``conftest.py`` 文件中添加以下行来这样做：

.. code-block:: python

    # conftest.py 的内容

    pytest_plugins = ["pytester"]

或者你可以使用 ``-p pytester`` 命令行选项调用 pytest。

这将允许你使用 :py:class:`pytester <pytest.Pytester>` fixture 来测试你的插件代码。

让我们用一个示例演示你可以用这个插件做什么。想象我们开发了一个提供 fixture ``hello`` 的插件，它产生一个函数，我们可以用这个函数调用一个可选参数。如果我们不提供值，它将返回一个字符串值 ``Hello World!`` 或如果我们提供一个字符串值则返回 ``Hello {value}!``。

.. code-block:: python

    import pytest


    def pytest_addoption(parser):
        group = parser.getgroup("helloworld")
        group.addoption(
            "--name",
            action="store",
            dest="name",
            default="World",
            help='Default "name" for hello().',
        )


    @pytest.fixture
    def hello(request):
        name = request.config.getoption("name")

        def _hello(name=None):
            if not name:
                name = request.config.getoption("name")
            return f"Hello {name}!"

        return _hello


现在 ``pytester`` fixture 提供了一个方便的 API 用于创建临时的 ``conftest.py`` 文件和测试文件。它还允许我们运行测试并返回一个结果对象，我们可以用它断言测试的结果。

.. code-block:: python

    def test_hello(pytester):
        """确保我们的插件正常工作。"""

        # 创建一个临时的 conftest.py 文件
        pytester.makeconftest(
            """
            import pytest

            @pytest.fixture(params=[
                "Brianna",
                "Andreas",
                "Floris",
            ])
            def name(request):
                return request.param
        """
        )

        # 创建一个临时的 pytest 测试文件
        pytester.makepyfile(
            """
            def test_hello_default(hello):
                assert hello() == "Hello World!"

            def test_hello_name(hello, name):
                assert hello(name) == "Hello {0}!".format(name)
        """
        )

        # 使用 pytest 运行所有测试
        result = pytester.runpytest()

        # 检查所有 4 个测试都通过了
        result.assert_outcomes(passed=4)


此外，可以将示例复制到 ``pytester`` 的隔离环境中，然后在它上面运行 pytest。这样我们可以将测试逻辑抽象到单独的文件中，这对于较长的测试和/或较长的 ``conftest.py`` 文件特别有用。

注意，为了让 ``pytester.copy_example`` 工作，我们需要在我们的配置文件中设置 `pytester_example_dir` 来告诉 pytest 在哪里查找示例文件。

.. code-block:: toml

    # pytest.toml 的内容
    [pytest]
    pytester_example_dir = "."


.. code-block:: python

    # test_example.py 的内容


    def test_plugin(pytester):
        pytester.copy_example("test_example.py")
        pytester.runpytest("-k", "test_example")


    def test_example():
        pass

.. code-block:: pytest

    $ pytest
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    configfile: pytest.toml
    collected 2 items

    test_example.py ..                                                   [100%]

    ============================ 2 passed in 0.12s =============================

有关 ``runpytest()`` 返回的结果对象及其提供的方法的更多信息，请查看 :py:class:`RunResult <_pytest.pytester.RunResult>` 文档。
