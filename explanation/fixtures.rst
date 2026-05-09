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

