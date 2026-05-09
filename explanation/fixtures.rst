.. _about-fixtures:

关于 fixtures
===============

.. seealso:: :ref:`how-to-fixtures`
.. seealso:: :ref:`Fixtures reference <reference-fixtures>`

pytest fixtures 被设计为显式、模块化和可扩展的。

什么是 fixtures
-----------------

在测试中，`fixture <https://en.wikipedia.org/wiki/Test_fixture#Software>`_
为测试提供了定义的、可靠的和一致的上下文。这可能包括环境（例如配置了已知参数的数据库）或内容（例如数据集）。

Fixtures 定义了构成测试的*准备*阶段的步骤和数据（参见 :ref:`test-anatomy`）。在 pytest 中，它们是你定义的用于此目的的函数。它们也可以用于定义测试的*执行*阶段；这是设计更复杂测试的强大技术。

通过参数访问由 fixtures 设置的服务、状态或其他操作环境。对于测试函数使用的每个 fixture，通常在测试函数的定义中有一个参数（以 fixture 命名）。

我们可以通过用 :py:func:`@pytest.fixture <pytest.fixture>` 装饰特定函数来告诉 pytest 它是一个 fixture。以下是 pytest 中 fixture 的简单示例：

.. code-block:: python

    import pytest


    class Fruit:
        def __init__(self, name):
            self.name = name

        def __eq__(self, other):
            return self.name == other.name


    @pytest.fixture
    def my_fruit():
        return Fruit("apple")


    @pytest.fixture
    def fruit_basket(my_fruit):
        return [Fruit("banana"), my_fruit]


    def test_my_fruit_in_basket(my_fruit, fruit_basket):
        assert my_fruit in fruit_basket

测试也不必局限于单个 fixture。它们可以依赖于任意多个 fixtures，fixtures 也可以使用其他 fixtures。这就是 pytest 的 fixture 系统真正闪耀的地方。


对 xUnit 风格设置/拆卸函数的改进
-----------------------------------------------------------

pytest fixtures 比经典的 xUnit
风格的设置/拆卸函数提供了显著的改进：

* fixtures 具有显式名称，并通过从测试函数、模块、类或整个项目中声明其使用来激活。

* fixtures 以模块化方式实现，因为每个 fixture 名称都会触发一个*fixture 函数*，该函数本身可以使用其他 fixtures。

* fixture 管理从简单单元测试扩展到复杂功能测试，允许根据配置和组件选项参数化 fixtures 和测试，或在函数、类、模块或整个测试会话范围内重用 fixtures。

* 无论使用了多少 fixtures，都可以轻松且安全地管理拆卸逻辑，无需手动小心处理错误或微调控件添加清理步骤的顺序。

此外，pytest 继续支持 :ref:`xunitsetup`。你可以混合使用两种风格，根据需要逐步从经典风格过渡到新风格。你也可以从现有的 :ref:`unittest.TestCase style <unittest.TestCase>` 开始。



Fixture 错误
-------------

pytest 会尽力将给定测试的所有 fixtures 按线性顺序排列，以便确定哪个 fixture 先执行、哪个其次，以此类推。然而，如果较早的 fixture 出现问题并引发异常，pytest 将停止执行该测试的 fixtures，并将该测试标记为有错误。

当测试被标记为有错误时，并不意味着测试失败。它只意味着测试甚至无法尝试执行，因为它依赖的某个东西出了问题。

这是为什么尽量减少给定测试中不必要的依赖关系的一个好理由。这样，不相关的问题就不会导致我们对什么可能有或没有问题有不完整的了解。

这里有一个快速示例来帮助说明：

.. code-block:: python

    import pytest


    @pytest.fixture
    def order():
        return []


    @pytest.fixture
    def append_first(order):
        order.append(1)


    @pytest.fixture
    def append_second(order, append_first):
        order.extend([2])


    @pytest.fixture(autouse=True)
    def append_third(order, append_second):
        order += [3]


    def test_order(order):
        assert order == [1, 2, 3]


如果无论出于何种原因，``order.append(1)`` 有一个 bug 并引发异常，我们将无法知道 ``order.extend([2])`` 或 ``order += [3]`` 是否也有问题。在 ``append_first`` 抛出异常后，pytest 不会为 ``test_order`` 运行任何更多 fixtures，甚至不会尝试运行 ``test_order`` 本身。唯一会运行的是 ``order`` 和 ``append_first``。


共享测试数据
-----------------

如果你想将文件中的测试数据提供给测试使用，一个好的方法是在 fixture 中加载这些数据以供测试使用。这利用了 pytest 的自动缓存机制。

另一个好的方法是将数据文件添加到 ``tests`` 目录中。还有一些社区插件可以帮助管理测试的这一方面，例如 :pypi:`pytest-datadir` 和 :pypi:`pytest-datafiles`。

.. _fixtures-signal-cleanup:

关于 fixture 清理的说明
----------------------------

pytest 不会对 :data:`SIGTERM <signal.SIGTERM>` 和 ``SIGQUIT`` 信号进行任何特殊处理（:data:`SIGINT <signal.SIGINT>` 由 Python 运行时通过 :class:`KeyboardInterrupt` 自然处理），因此管理在 Python 进程终止时（通过那些信号）需要被清除的重要外部资源的 fixtures 可能会泄漏资源。

pytest 不处理这些信号来执行 fixture 清理的原因是信号处理函数是全局的，更改它们可能会干扰正在执行的代码。

如果你的套件中的 fixtures 在这些场景中需要特殊处理终止，请参阅问题跟踪器中的 :issue:`此评论 <5243#issuecomment-491522595>` 以获取可能的解决方法。
