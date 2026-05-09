
.. _`classic xunit`:
.. _xunitsetup:

如何实现 xunit 风格的设置
========================================

本节描述了一种经典且流行的方法，可以在模块/类/函数的基础上实现 fixtures（设置和拆卸测试状态）。


.. note::

    虽然这些设置/拆卸方法对于来自 ``unittest`` 或 ``nose`` 背景的人来说简单且熟悉，但你也可以考虑使用 pytest 更强大的 :ref:`fixture 机制 <fixture>`，它利用依赖注入的概念，允许更模块化和更可扩展的方法来管理测试状态，特别是对于大型项目和功能测试。你可以在同一文件中混合使用这两种 fixture 机制，但 ``unittest.TestCase`` 子类的测试方法不能接收 fixture 参数。


模块级别设置/拆卸
--------------------------------------

如果你在单个模块中有多个测试函数和测试类，你可以选择性实现以下 fixture 方法，这些方法通常将为所有函数调用一次：

.. code-block:: python

    def setup_module(module):
        """设置特定于执行给定模块的任何状态。"""


    def teardown_module(module):
        """拆卸之前使用 setup_module 方法设置的任何状态。
        """

自 pytest-3.0 起，``module`` 参数是可选的。

类级别设置/拆卸
----------------------------------

类似地，以下方法在类级别调用，在类的所有测试方法被调用之前和之后：

.. code-block:: python

    @classmethod
    def setup_class(cls):
        """设置特定于执行给定类（通常包含测试）的任何状态。
        """


    @classmethod
    def teardown_class(cls):
        """拆卸之前使用对 setup_class 的调用设置的任何状态。
        """

.. _xunit-method-setup:

方法和函数级别设置/拆卸
-----------------------------------------------

类似地，以下方法在每个方法调用前后调用：

.. code-block:: python

    def setup_method(self, method):
        """设置与类中给定方法执行绑定的任何状态。setup_method 为类的每个测试方法调用。
        """


    def teardown_method(self, method):
        """拆卸之前使用 setup_method 调用设置的任何状态。
        """

自 pytest-3.0 起，``method`` 参数是可选的。

如果你更愿意在模块级别直接定义测试函数，你也可以使用以下函数来实现 fixtures：

.. code-block:: python

    def setup_function(function):
        """设置与给定函数执行绑定的任何状态。为模块中的每个测试函数调用。
        """


    def teardown_function(function):
        """拆卸之前使用 setup_function 调用设置的任何状态。
        """

自 pytest-3.0 起，``function`` 参数是可选的。

备注：

* 每个测试过程中可能多次调用设置/拆卸对。

* 如果相应的设置函数存在且失败/被跳过，则不会调用拆卸函数。

* 在 pytest-4.2 之前，xunit 风格的函数不遵守 fixtures 的范围规则，所以例如 ``setup_method`` 可能在 session-scoped 的 autouse fixture 之前被调用。

  现在 xunit 风格的函数已与 fixture 机制集成，并遵守调用中涉及的 fixtures 的正确范围规则。
