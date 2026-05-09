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

