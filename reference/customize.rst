Configuration
=============

命令行选项和配置文件设置
-----------------------------------------------------------------

你可以通过使用常规帮助选项来获取命令行和配置选项的帮助：

.. code-block:: bash

    pytest -h   # 打印选项 _和_ 配置文件设置

这将显示由已安装插件注册的命令行和配置文件设置。

.. _`config file formats`:

配置文件格式
--------------------------

许多 :ref:`pytest 设置 <ini options ref>` 可以在*配置文件*中设置，
按照约定位于你的仓库根目录中。

pytest 支持的配置文件的快速示例：

pytest.toml
~~~~~~~~~~~

.. versionadded:: 9.0

``pytest.toml`` 文件优先于其他文件，即使为空。

或者，可以使用隐藏版本 ``.pytest.toml``。

.. tab:: toml

    .. code-block:: toml

        # pytest.toml 或 .pytest.toml
        [pytest]
        minversion = "9.0"
        addopts = ["-ra", "-q"]
        testpaths = [
            "tests",
            "integration",
        ]

pytest.ini
~~~~~~~~~~

``pytest.ini`` 文件优先于其他文件（除了 ``pytest.toml`` 和 ``.pytest.toml``），即使为空。

或者，可以使用隐藏版本 ``.pytest.ini``。

.. tab:: ini

    .. code-block:: ini

        # pytest.ini 或 .pytest.ini
        [pytest]
        minversion = 6.0
        addopts = -ra -q
        testpaths =
            tests
            integration


pyproject.toml
~~~~~~~~~~~~~~

.. versionadded:: 6.0
.. versionchanged:: 9.0

``pyproject.toml`` 文件被支持用于配置。

.. tab:: toml

    使用 ``[tool.pytest]`` 来利用原生 TOML 类型（pytest 9.0 起支持）：

    .. code-block:: toml

        # pyproject.toml
        [tool.pytest]
        minversion = "9.0"
        addopts = ["-ra", "-q"]
        testpaths = [
            "tests",
            "integration",
        ]

.. tab:: ini

    使用 ``[tool.pytest.ini_options]`` 进行 INI 风格配置（pytest 6.0 起支持）：

    .. code-block:: toml

        # pyproject.toml
        [tool.pytest.ini_options]
        minversion = "6.0"
        addopts = "-ra -q"
        testpaths = [
            "tests",
            "integration",
        ]

    对于仍在运行低于 6.0 版本 pytest 的项目，
    也在 ``pytest.ini`` 或 ``setup.cfg`` 中保留 ``minversion``。那些版本
    不读取 ``pyproject.toml``。

tox.ini
~~~~~~~

``tox.ini`` 文件是 `tox <https://tox.readthedocs.io>`__ 项目的配置文件，
如果它们有 ``[pytest]`` 部分，也可以用于保存 pytest 配置。

.. tab:: ini

    .. code-block:: ini

        # tox.ini
        [pytest]
        minversion = 6.0
        addopts = -ra -q
        testpaths =
            tests
            integration


setup.cfg
~~~~~~~~~

``setup.cfg`` 文件是通用配置文件，最初由 ``distutils``（现已弃用）和 :std:doc:`setuptools <setuptools:userguide/declarative_config>` 使用，如果它们有 ``[tool:pytest]`` 部分，也可以用于保存 pytest 配置。

.. tab:: ini

    .. code-block:: ini

        # setup.cfg
        [tool:pytest]
        minversion = 6.0
        addopts = -ra -q
        testpaths =
            tests
            integration

.. warning::

    除非用于非常简单的用例，否则不推荐使用 ``setup.cfg``。``.cfg``
    文件使用与 ``pytest.ini`` 和 ``tox.ini`` 不同的解析器，可能会导致难以追踪的问题。
    如果可能，建议使用后面的文件或 ``pyproject.toml`` 来保存你的 pytest 配置。


.. _rootdir:
.. _configfiles:

初始化：确定 rootdir 和 configfile
--------------------------------------------------

pytest 为每个测试运行确定一个 ``rootdir``，它取决于命令行参数（指定的测试文件、路径）和配置文件的存在。
确定的 ``rootdir`` 和 ``configfile`` 在启动时作为 pytest 标题的一部分打印。

以下是 ``pytest`` 使用 ``rootdir`` 的摘要：

* 在收集期间构造 *nodeid*；每个测试被分配一个唯一的 *nodeid*，该 id 根植于 ``rootdir`` 并考虑完整路径、类名、函数名和参数化（如果有的话）。

* 被插件用作存储项目/测试运行特定信息的稳定位置；例如，内部 :ref:`cache <cache>` 插件在 ``rootdir`` 中创建一个 ``.pytest_cache`` 子目录来存储其跨测试运行状态。

``rootdir`` 不 用于修改 ``sys.path``/``PYTHONPATH`` 或影响模块的导入方式。有关更多详细信息，请参阅 :ref:`pythonpath`。

:option:`--rootdir=path` 命令行选项可用于强制指定特定目录。请注意，与其他命令行选项不同，``--rootdir`` 不能在配置文件内部与 :confval:`addopts` 一起使用，因为 ``rootdir`` 已经用于*查找*配置文件。

查找 ``rootdir``
~~~~~~~~~~~~~~~~~~~~~~~

以下是从 ``args`` 查找 rootdir 的算法：

- 如果在命令行中传递了 :option:`-c`，则使用该文件作为配置文件，并将其目录作为 ``rootdir``。

- 确定指定 ``args`` 的公共祖先目录，这些参数被识别为文件系统中存在的路径。如果未找到此类路径，则将公共祖先目录设置为当前工作目录。

- 在祖先目录及其上级目录中查找 ``pytest.toml``、``.pytest.toml``、``pytest.ini``、``.pytest.ini``、``pyproject.toml``、``tox.ini`` 和 ``setup.cfg`` 文件。如果匹配到一个，它将成为 ``configfile``，其目录将成为 ``rootdir``。

- 如果未找到配置文件，则从公共祖先目录向上查找 ``setup.py`` 以确定 ``rootdir``。

- 如果未找到 ``setup.py``，则在每个指定的 ``args`` 及其上级目录中查找 ``pytest.toml``、``.pytest.toml``、``pytest.ini``、``.pytest.ini``、``pyproject.toml``、``tox.ini`` 和 ``setup.cfg``。如果匹配到一个，它将成为 ``configfile``，其目录将成为 ``rootdir``。

- 如果未找到 ``configfile`` 且未传递配置参数，则使用已确定的公共祖先作为根目录。这允许在不属于包的没有任何特定配置文件的架构中使用 pytest。

如果未给出 ``args``，pytest 收集当前工作目录下方的测试，并从那里开始确定 ``rootdir``。

文件只有在以下情况下才会被匹配用于配置：

* ``pytest.toml``：将始终匹配并具有最高优先级，即使为空。
* ``pytest.ini``：将始终匹配并具有优先级（在 ``pytest.toml`` 和 ``.pytest.toml`` 之后），即使为空。
* ``pyproject.toml``：包含 ``[tool.pytest]`` 或 ``[tool.pytest.ini_options]`` 表。
* ``tox.ini``：包含 ``[pytest]`` 部分。
* ``setup.cfg``：包含 ``[tool:pytest]`` 部分。

最后，如果没有找到其他匹配项，``pyproject.toml`` 文件将被视为 ``configfile``，在这种情况下，即使它不包含 ``[tool.pytest]`` 表（从版本 ``9.0`` 起）或 ``[tool.pytest.ini_options]`` 表（从版本 ``8.1`` 起）。

文件按上述顺序考虑。来自多个 ``configfiles`` 候选者的选项永远不会合并 - 第一个匹配获胜。

配置文件还确定 ``rootpath`` 的值。

:class:`Config <pytest.Config>` 对象（可通过 hooks 或 :fixture:`pytestconfig` fixture 访问）随后将携带这些属性：

- :attr:`config.rootpath <pytest.Config.rootpath>`：确定的根目录，保证存在。它被用作构造测试地址（"nodeid"）的参考目录，也可被插件用于存储每次测试运行的信息。

- :attr:`config.inipath <pytest.Config.inipath>`：确定的 ``configfile``，可能为 ``None``（因历史原因命名为 ``inipath``）。

.. versionadded:: 6.1
    ``config.rootpath`` 和 ``config.inipath`` 属性。它们是 :class:`pathlib.Path`
    版本的旧 ``config.rootdir`` 和 ``config.inifile``，具有类型 ``py.path.local``，并且仍然存在以保持向后兼容。



示例：

.. code-block:: bash

    pytest path/to/testdir path/other/

将把公共祖先确定为 ``path``，然后按以下方式检查配置文件：

.. code-block:: text

    # 首先查找 path/pytest.toml
    path/pytest.toml
    path/pytest.ini
    path/pyproject.toml  # 必须包含 [tool.pytest] 表才能匹配
    path/tox.ini         # 必须包含 [pytest] 部分才能匹配
    path/setup.cfg       # 必须包含 [tool:pytest] 部分才能匹配
    pytest.toml
    pytest.ini
    ... # 一直到根目录

    # 现在查找 setup.py
    path/setup.py
    setup.py
    ... # 一直到根目录


.. warning::

    自定义 pytest 插件命令行参数可能包含路径，如
    ``pytest --log-output ../../test.log args``。那么 ``args`` 是必需的，
    否则 pytest 会使用 test.log 的目录进行 rootdir 确定
    （另请参阅 :issue:`1435`）。
    也可以使用点 ``.`` 来引用当前工作目录。


.. _`how to change command line options defaults`:
.. _`adding default options`:


内置配置文件选项
----------------------------------------------

有关完整选项列表，请参阅 :ref:`参考文档 <ini options ref>`。

语法高亮主题自定义
---------------------------------------

pytest 使用的语法高亮主题可以使用两个环境变量进行自定义：

- :envvar:`PYTEST_THEME` 设置要使用的 `pygment 样式 <https://pygments.org/docs/styles/>`_。
- :envvar:`PYTEST_THEME_MODE` 将此样式设置为 *light* 或 *dark*。
