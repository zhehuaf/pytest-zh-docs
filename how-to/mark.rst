.. _mark:

如何使用属性标记测试函数
===========================================

通过使用 ``pytest.mark`` 辅助函数，你可以轻松地在测试函数上设置元数据。你可以在 :ref:`API Reference<marks ref>` 中找到内置标记的完整列表。或者你可以使用 CLI 列出所有标记，包括内置和自定义的 - :code:`pytest --markers`。

以下是一些内置标记：

* :ref:`usefixtures <usefixtures>` - 在测试函数或类上使用 fixtures
* :ref:`filterwarnings <filterwarnings>` - 过滤测试函数的某些警告
* :ref:`skip <skip>` - 始终跳过测试函数
* :ref:`skipif <skipif>` - 如果满足特定条件则跳过测试函数
* :ref:`xfail <xfail>` - 如果满足特定条件则产生"预期失败"结果
* :ref:`parametrize <parametrizemark>` - 对同一个测试函数进行多次调用。

创建自定义标记或将标记应用于整个测试类或模块很容易。这些标记可以被插件使用，也常用于使用 :option:`-m` 选项在命令行上 :ref:`选择测试 <mark run>`。

参见 :ref:`mark examples` 获取示例，这些示例也可作为文档使用。

.. note::

    标记只能应用于测试，对 :ref:`fixtures <fixtures>` 没有影响。


注册标记
-----------------

你可以在配置文件中像这样注册自定义标记：

.. tab:: toml

    .. code-block:: toml

        [pytest]
        markers = [
            "slow: marks tests as slow (deselect with '-m \"not slow\"')",
            "serial",
        ]

.. tab:: ini

    .. code-block:: ini

        [pytest]
        markers =
            slow: marks tests as slow (deselect with '-m "not slow"')
            serial

请注意，标记名称后面的 ``:`` 之后的所有内容都是可选的描述。

或者，你可以在 :ref:`pytest_configure <initialization-hooks>` 钩子中以编程方式注册新标记：

.. code-block:: python

    def pytest_configure(config):
        config.addinivalue_line(
            "markers", "env(name): mark test to run only on named environment"
        )


已注册的标记会出现在 pytest 的帮助文本中，并且不会发出警告（参见下一节）。建议第三方插件始终 :ref:`注册他们的标记 <registering-markers>`。

.. _unknown-marks:

对未知标记引发错误
-------------------------------

使用 ``@pytest.mark.name_of_the_mark`` 装饰器应用的未注册标记将始终发出警告，以避免由于拼写错误而静默执行令人惊讶的操作。如前一节所述，你可以通过在配置文件中注册它们或使用自定义的 ``pytest_configure`` 钩子来禁用自定义标记的警告。

当设置了 :confval:`strict_markers` 配置选项时，使用 ``@pytest.mark.name_of_the_mark`` 装饰器应用的任何未知标记都将触发错误。你可以通过在你的配置中设置 :confval:`strict_markers` 来在你的项目中强制执行此验证：

.. tab:: toml

    .. code-block:: toml

        [pytest]
        addopts = ["--strict-markers"]
        markers = [
            "slow: marks tests as slow (deselect with '-m \"not slow\"')",
            "serial",
        ]

.. tab:: ini

    .. code-block:: ini

        [pytest]
        strict_markers = true
        markers =
            slow: marks tests as slow (deselect with '-m "not slow"')
            serial

