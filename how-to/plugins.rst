.. _`external plugins`:
.. _`extplugins`:
.. _`using plugins`:

如何安装和使用插件
===============================

本节讨论安装和使用第三方插件。关于编写自己的插件，请参见 :ref:`writing-plugins`。

使用 ``pip`` 可以轻松安装第三方插件：

.. code-block:: bash

    pip install pytest-NAME
    pip uninstall pytest-NAME

如果安装了插件，``pytest`` 会自动找到并集成它，无需激活。

以下是一些流行插件的简要注释列表：

* :pypi:`pytest-django`: 使用 pytest 集成编写 `django <https://docs.djangoproject.com/>`_ 应用程序的测试。

* :pypi:`pytest-twisted`: 编写 `twisted <https://twistedmatrix.com/>`_ 应用程序的测试，启动 reactor 并从测试函数处理 deferreds。

* :pypi:`pytest-cov`:
  覆盖率报告，与分布式测试兼容

* :pypi:`pytest-xdist`:
  将测试分发到 CPU 和远程主机，以 boxed 模式运行，允许在段错误中幸存，以 looponfailing 模式运行，在文件更改时自动重新运行失败的测试。

* :pypi:`pytest-instafail`:
  在测试运行进行时报告失败。

* :pypi:`pytest-bdd`:
  使用行为驱动测试编写测试。

* :pypi:`pytest-timeout`:
  基于函数标记或全局定义超时测试。

* :pypi:`pytest-pep8`:
  一个 ``--pep8`` 选项，用于启用 PEP8 合规性检查。

* :pypi:`pytest-flakes`:
  使用 pyflakes 检查源代码。

* :pypi:`allure-pytest`:
  通过 `allure-framework <https://github.com/allure-framework/>`_ 报告测试结果。

要查看所有插件及其针对不同 pytest 和 Python 版本的最新测试状态的完整列表，请访问 :ref:`plugin-list`。

你也可以通过 `pytest- pypi.org 搜索`_ 发现更多插件。

.. _`pytest- pypi.org search`: https://pypi.org/search/?q=pytest-


.. _`available installable plugins`:

在测试模块或 conftest 文件中要求/加载插件
-----------------------------------------------------------

你可以在测试模块或 conftest 文件中使用 :globalvar:`pytest_plugins` 要求插件：

.. code-block:: python

    pytest_plugins = ("myapp.testsupport.myplugin",)

当加载测试模块或 conftest 插件时，指定的插件也将被加载。

.. note::

    在非根 ``conftest.py`` 文件中使用 ``pytest_plugins`` 变量要求插件已被弃用。参见
    :ref:`写作插件部分中的完整说明 <requiring plugins in non-root conftests>`。

.. note::

   名称 ``pytest_plugins`` 是保留的，不应作为自定义插件模块的名称使用。


.. _`findpluginname`:

找出哪些插件是活动的
------------------------------------

如果你想找出环境中哪些插件是活动的，你可以输入：

.. code-block:: bash

    pytest --trace-config

这将获得一个扩展的测试头部，显示已激活的插件及其名称。它还将打印本地插件（即 :ref:`conftest.py <conftest.py plugins>` 文件）何时被加载。

.. _`cmdunregister`:

按名称停用/注销插件
---------------------------------------------

你可以阻止插件加载或注销它们：

.. code-block:: bash

    pytest -p no:NAME

这意味着任何后续尝试激活/加载命名的插件都将失败。

如果你想无条件地为项目禁用某个插件，你可以将此选项添加到配置文件中：

.. tab:: toml

    .. code-block:: toml

        [pytest]
        addopts = ["-p", "no:NAME"]

.. tab:: ini

    .. code-block:: ini

        [pytest]
        addopts = -p no:NAME

或者，要仅在特定环境中禁用它（例如在 CI 服务器中），你可以将 ``PYTEST_ADDOPTS`` 环境变量设置为 ``-p no:name``。

参见 :ref:`findpluginname` 了解如何获取插件的名称。

.. _`disable_plugin_autoload`:

禁用插件的自动加载
----------------------------------

如果你想禁用插件的自动加载，而不是需要手动使用 :option:`-p` 或 :envvar:`PYTEST_PLUGINS` 指定每个插件，你可以使用 :option:`--disable-plugin-autoload` 或 :envvar:`PYTEST_DISABLE_PLUGIN_AUTOLOAD`。

.. code-block:: bash

   export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
   export PYTEST_PLUGINS=NAME,NAME2
   pytest

.. code-block:: bash

   pytest --disable-plugin-autoload -p NAME -p NAME2

.. tab:: toml

    .. code-block:: toml

        [pytest]
        addopts = ["--disable-plugin-autoload", "-p", "NAME", "-p", "NAME2"]

.. tab:: ini

    .. code-block:: ini

        [pytest]
        addopts =
            --disable-plugin-autoload
            -p NAME
            -p NAME2

.. versionadded:: 8.4

    :option:`--disable-plugin-autoload` 命令行标志。

.. note::

   :option:`-p` 和 :envvar:`PYTEST_PLUGINS` 都是显式控制加载哪些插件的方式，但它们服务于略有不同的用例。

   * :option:`-p` 通过名称或入口点为特定的 pytest 调用加载（或使用 ``-p no:<name>`` 禁用）插件，并在启动期间早期处理。
   * :envvar:`PYTEST_PLUGINS` 是一个逗号分隔的 Python 模块列表，这些模块在启动期间作为插件导入和注册。此机制通常由测试套件使用，例如在测试插件时。

   当显式控制插件加载时（特别是使用 :envvar:`PYTEST_DISABLE_PLUGIN_AUTOLOAD` 或 :option:`--disable-plugin-autoload`），避免通过多种机制指定相同的插件。多次注册相同的插件可能导致插件注册期间的错误。

示例：

.. code-block:: bash

   # 禁用自动加载并仅为这次调用加载特定插件
   PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -p xdist

.. code-block:: bash

   # 禁用自动加载并在启动期间加载插件模块
   PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTEST_PLUGINS=mymodule.plugin,xdist pytest