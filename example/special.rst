
可以查看所有已收集测试的 session-fixture
----------------------------------------------------------------

一个 session-scoped 的 fixture 实际上可以访问所有已收集的测试项。这里是一个 fixture 函数的示例，它遍历所有已收集的测试，并查看它们的测试类是否定义了 ``callme`` 方法，如果有就调用它：

.. code-block:: python

    # conftest.py 的内容

    import pytest


    @pytest.fixture(scope="session", autouse=True)
    def callattr_ahead_of_alltests(request):
        print("callattr_ahead_of_alltests called")
        seen = {None}
        session = request.node
        for item in session.items:
            cls = item.getparent(pytest.Class)
            if cls not in seen:
                if hasattr(cls.obj, "callme"):
                    cls.obj.callme()
                seen.add(cls)

测试类现在可以定义一个 ``callme`` 方法，它将在运行任何测试之前被调用：

.. code-block:: python

    # test_module.py 的内容


    class TestHello:
        @classmethod
        def callme(cls):
            print("callme called!")

        def test_method1(self):
            print("test_method1 called")

        def test_method2(self):
            print("test_method2 called")


    class TestOther:
        @classmethod
        def callme(cls):
            print("callme other called")

        def test_other(self):
            print("test other")


    # 也适用于 unittest ...
    import unittest


    class SomeTest(unittest.TestCase):
        @classmethod
        def callme(self):
            print("SomeTest callme called")

        def test_unit1(self):
            print("test_unit1 method called")

如果你运行此测试而不捕获输出：

.. code-block:: pytest

    $ pytest -q -s test_module.py
    callattr_ahead_of_alltests called
    callme called!
    callme other called
    SomeTest callme called
    test_method1 called
    .test_method2 called
    .test other
    .test_unit1 method called
    .
    4 passed in 0.12s
