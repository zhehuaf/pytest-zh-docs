.. _writinghooks:

如何编写钩子函数
=========================

钩子函数验证和标记
-------------------------------------------

pytest 通过 :py:func:`pytest.hookimpl` 装饰器调用钩子函数。这允许通过标记将上下文/附加信息传递给钩子函数。

.. autofunction:: pytest.hookimpl
    :noindex:

通常，你可以直接编写钩子函数，而不需要装饰器：

.. code-block:: python

    def pytest_collection_modifyitems(items, config):
        # 直接在 items 上调用钩子
        items.append(MyItem())

如果在 pytest 或插件中发现没有标记的钩子函数，它将作为 ``hookwrapper=False`` 和 ``trylast=False`` 调用。它们将按照发现的顺序调用，即由 ``conftest.py`` 导入顺序决定。

如果你希望调用你的钩子函数作为包装器函数，请将其装饰为：

.. code-block:: python

    @pytest.hookimpl(wrapper=True)
    def pytest_collection_modifyitems(items, config):
        # 将在调用下一个钩子之前执行
        do_something_before_next_hook_executes()

        # 如果结果是一个异常，将引发该异常。
        res = yield

        new_res = post_process_result(res)

        # 覆盖返回给插件系统的值。
        return new_res

钩子包装器需要为钩子返回一个结果，或引发一个异常。

在许多情况下，包装器只需要在实际钩子实现周围执行跟踪或其他副作用，在这种情况下，它可以返回 ``yield`` 的结果值。最简单（但无用）的钩子包装器是 ``return (yield)``。

在其他情况下，包装器想要调整或适配结果，在这种情况下，它可以返回一个新值。如果底层钩子的结果是一个可变对象，包装器可以修改该结果，但最好避免这样做。

如果钩子实现失败并引发异常，包装器可以使用围绕 ``yield`` 的 ``try-catch-finally`` 来处理该异常，通过传播它、抑制它或完全引发不同的异常。

有关更多信息，请查阅 :ref:`pluggy 关于钩子包装器的文档 <pluggy:hookwrappers>`。

.. _plugin-hookorder:

钩子函数排序 / 调用示例
-------------------------------------

对于任何给定的钩子规范，可能有多个实现，因此我们通常将 ``hook`` 执行视为 ``1:N`` 函数调用，其中 ``N`` 是已注册函数的数量。有一些方法可以影响钩子实现在其他之前或之后执行，即在 ``N`` 大小的函数列表中的位置：

.. code-block:: python

    # 插件 1
    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(items):
        # 将尽可能早地执行
        ...


    # 插件 2
    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(items):
        # 将尽可能晚地执行
        ...


    # 插件 3
    @pytest.hookimpl(wrapper=True)
    def pytest_collection_modifyitems(items):
        # 甚至会在上面的 tryfirst 之前执行！
        try:
            return (yield)
        finally:
            # 将在所有非包装器执行后执行
            ...

执行顺序如下：

1. 调用 Plugin3 的 pytest_collection_modifyitems 直到 yield 点，因为它是一个钩子包装器。

2. 调用 Plugin1 的 pytest_collection_modifyitems，因为它标记为 ``tryfirst=True``。

3. 调用 Plugin2 的 pytest_collection_modifyitems，因为它标记为 ``trylast=True`` （但即使没有此标记，它也会在 Plugin1 之后执行）。

4. 然后执行 Plugin3 的 pytest_collection_modifyitems 的 yield 点之后的代码。yield 接收调用非包装器的结果，如果非包装器引发异常则引发异常。

也可以在钩子包装器上使用 ``tryfirst`` 和 ``trylast``，在这种情况下，它会影响钩子包装器之间的排序。

.. _`declaringhooks`:

声明新钩子
----------------

.. note::

    这是关于如何添加新钩子以及它们通常如何工作的快速概述，但更完整的概述可以在 `pluggy 文档 <https://pluggy.readthedocs.io/en/latest/>`__ 中找到。

插件和 ``conftest.py`` 文件可以声明新钩子，然后可以由其他插件实现以改变行为或与该新插件交互：

.. autofunction:: _pytest.hookspec.pytest_addhooks
    :noindex:

钩子通常声明为仅包含文档描述何时将调用钩子以及期望什么返回值的空操作函数。函数的名称必须以 ``pytest_`` 开头，否则 pytest 不会识别它们。

这里有一个示例。假设这段代码在 ``sample_hook.py`` 模块中。

.. code-block:: python

    def pytest_my_hook(config):
        """
        接收 pytest 配置并对其执行操作
        """

要在 pytest 中注册钩子，它们需要在自己的模块或类中结构化。然后可以将此类或模块传递给 ``pluginmanager`` 使用 ``pytest_addhooks`` 函数（它本身是 pytest 公开的一个钩子）。

.. code-block:: python

    def pytest_addhooks(pluginmanager):
        """此示例假设钩子分组在 'sample_hook' 模块中。"""
        from my_app.tests import sample_hook

        pluginmanager.add_hookspecs(sample_hook)

有关真实示例，请参见 `xdist <https://github.com/pytest-dev/pytest-xdist>`_ 中的 `newhooks.py`_。

.. _`newhooks.py`: https://github.com/pytest-dev/pytest-xdist/blob/974bd566c599dc6a9ea291838c6f226197208b46/xdist/newhooks.py

钩子可以从 fixtures 或其他钩子中调用。在这两种情况下，都是通过 ``config`` 对象中可用的 ``hook`` 对象调用钩子。大多数钩子直接接收 ``config`` 对象，而 fixtures 可以使用提供相同对象的 ``pytestconfig`` fixture。

.. code-block:: python

    @pytest.fixture()
    def my_fixture(pytestconfig):
        # 调用名为 "pytest_my_hook" 的钩子
        # 'result' 将是所有已注册函数的返回值列表。
        result = pytestconfig.hook.pytest_my_hook(config=pytestconfig)

.. note::
    钩子仅使用关键字参数接收参数。

现在你的钩子已准备好被使用。要注册钩子上的函数，其他插件或用户现在只需在它们的 ``conftest.py`` 中用正确的签名定义函数 ``pytest_my_hook``。

示例：

.. code-block:: python

    def pytest_my_hook(config):
        """
        将所有活动钩子打印到屏幕。
        """
        print(config.hook)

.. note::

    与其他钩子不同，:hook:`pytest_generate_tests` 钩子即使在测试模块或测试类中定义时也会被识别。其他钩子必须存在于 :ref:`conftest.py 插件 <localplugin>` 或外部插件中。
    参见 :ref:`parametrize-basics` 和 :ref:`hook-reference`。

.. _`addoptionhooks`:

在 pytest_addoption 中使用钩子
--------------------------------------

偶尔，有必要根据另一个插件中的钩子改变一个插件定义命令行选项的方式。例如，一个插件可能暴露一个命令行选项，另一个插件需要为该选项定义默认值。可以使用 pluginmanager 安装和使用钩子来完成此任务。插件将定义并添加钩子，并使用 pytest_addoption 如下所示：

.. code-block:: python

   # hooks.py 的内容


   # 使用 firstresult=True 因为我们只希望一个插件定义此默认值
   @hookspec(firstresult=True)
   def pytest_config_file_default_value():
       """返回配置文件命令行选项的默认值。"""


   # myplugin.py 的内容


   def pytest_addhooks(pluginmanager):
       """此示例假设钩子分组在 'hooks' 模块中。"""
       from . import hooks

       pluginmanager.add_hookspecs(hooks)


   def pytest_addoption(parser, pluginmanager):
       default_value = pluginmanager.hook.pytest_config_file_default_value()
       parser.addoption(
           "--config-file",
           help="要使用的配置文件，默认为 %(default)s",
           default=default_value,
       )

使用 myplugin 的 conftest.py 只需如下定义钩子：

.. code-block:: python

    def pytest_config_file_default_value():
        return "config.yaml"


可选地使用第三方插件的钩子
-------------------------------------------

如上所述，使用来自插件的新钩子可能有点棘手，因为标准 :ref:`验证机制 <validation>`：
如果你依赖于未安装的插件，验证将失败，错误消息对你的用户来说意义不大。

一种方法是将钩子实现推迟到新插件，而不是直接在插件模块中声明钩子函数，例如：

.. code-block:: python

    # myplugin.py 的内容


    class DeferPlugin:
        """简单的插件来推迟 pytest-xdist 钩子函数。"""

        def pytest_testnodedown(self, node, error):
            """标准的 xdist 钩子函数。"""


    def pytest_configure(config):
        if config.pluginmanager.hasplugin("xdist"):
            config.pluginmanager.register(DeferPlugin())

这还有一个好处，允许你根据安装了哪些插件来有条件地安装钩子。

.. _plugin-stash:

在钩子函数之间跨项存储数据
-------------------------------------------

插件经常需要在一个钩子实现中将数据存储在 :class:`~pytest.Item` 上，并在另一个中访问它。一个常见的解决方案是直接在项上分配一些私有属性，但像 mypy 这样的类型检查器不赞成这样做，而且也可能与其他插件冲突。
所以 pytest 提供了更好的方法来做到这一点，:attr:`item.stash <_pytest.nodes.Node.stash>`。

要在你的插件中使用 "stash"，首先在插件的顶层某处创建 "stash keys"：

.. code-block:: python

    been_there_key = pytest.StashKey[bool]()
    done_that_key = pytest.StashKey[str]()

然后在某个时刻使用 keys 来存储你的数据：

.. code-block:: python

    def pytest_runtest_setup(item: pytest.Item) -> None:
        item.stash[been_there_key] = True
        item.stash[done_that_key] = "no"

并在另一个时刻检索它们：

.. code-block:: python

    def pytest_runtest_teardown(item: pytest.Item) -> None:
        if not item.stash[been_there_key]:
            print("Oh?")
        item.stash[done_that_key] = "yes!"

Stashes 在所有节点类型上可用（如 :class:`~pytest.Class`、:class:`~pytest.Session`），如果需要的话也在 :class:`~pytest.Config` 上可用。
