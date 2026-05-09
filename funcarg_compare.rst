:orphan:

.. _`funcargcompare`:

pytest-2.3: fixture/funcarg 演变的原因
=============================================================

目标读者：阅读本文档需要了解 Python 测试、xUnit 设置方法以及（之前的）基本 pytest funcarg 机制的基本知识，请参阅 :ref:`historical funcargs and pytest.funcargs`。如果你是 pytest 的新手，你可以直接忽略本节并阅读其他部分。

先前 ``pytest_funcarg__`` 机制的缺点
--------------------------------------------------------------

在 pytest-2.3 之前的 funcarg 机制每次需要为测试函数提供 funcarg 时都会调用一次工厂。如果工厂希望在不同范围内重用资源，它通常使用 ``request.cached_setup()`` 助手来管理资源的缓存。以下是我们如何实现每会话 Database 对象的基本示例：

.. code-block:: python

    # conftest.py 的内容
    class Database:
        def __init__(self):
            print("database instance created")

        def destroy(self):
            print("database instance destroyed")


    def pytest_funcarg__db(request):
        return request.cached_setup(
            setup=DataBase, teardown=lambda db: db.destroy, scope="session"
        )

这种方法有几个局限性和困难：

1. 对 funcarg 资源创建进行作用域管理并不简单，相反，必须理解复杂的 cached_setup() 方法机制。

2. 对 "db" 资源进行参数化并不简单：
   你需要应用 "parametrize" 装饰器或实现一个
   :hook:`pytest_generate_tests` 钩子
   调用 :py:func:`~pytest.Metafunc.parametrize`
   在资源被使用的地方执行参数化。
   此外，你需要修改工厂以使用包含 ``request.param`` 的 ``extrakey`` 参数
   传递给 ``Request.cached_setup`` 调用。

3. 多个参数化的 session-scoped 资源将同时处于活动状态，这使得它们难以影响被测应用程序的全局状态。

4. 你无法在 xUnit 设置方法中使用 funcarg 工厂。

5. 非参数化的 fixture 函数无法使用参数化的 funcarg 资源，除非它在测试函数签名中声明。

所有这些局限性都在 pytest-2.3 及其改进的 :ref:`fixture 机制 <fixture>` 中得到了解决。


Fixture/funcarg 工厂的直接作用域
--------------------------------------------------------

你可以使用
:ref:`@pytest.fixture <pytest.fixture>` 装饰器并直接声明作用域，
而不是调用 cached_setup() 来设置缓存作用域：

.. code-block:: python

    @pytest.fixture(scope="session")
    def db(request):
        # 每个会话只调用一次工厂
        db = DataBase()
        request.addfinalizer(db.destroy)  # 会话结束时销毁
        return db

这个工厂实现不再需要调用 ``cached_setup()``，
因为它每个会话只会调用一次。此外，
``request.addfinalizer()`` 根据工厂函数正在操作的指定资源作用域注册一个终结器。


Funcarg 资源工厂的直接参数化
----------------------------------------------------------

以前，funcarg 工厂不能直接引起参数化。
你需要在测试函数上指定 ``@parametrize`` 装饰器
或实现一个 :hook:`pytest_generate_tests` 钩子来执行
参数化，即对测试进行多次调用并使用不同的值集。
pytest-2.3 引入了一个可以在工厂本身上使用的装饰器：

.. code-block:: python

    @pytest.fixture(params=["mysql", "pg"])
    def db(request): ...  # 使用 request.param

这里工厂将被调用两次（将各自的 "mysql" 和 "pg" 值设置为 ``request.param`` 属性），所有需要 "db" 的测试也将运行两次。"mysql" 和 "pg" 值也将用于报告测试调用变体。

这种新的参数化 funcarg 工厂的方式在许多情况下应该允许重用已经编写好的工厂，因为当通过 :py:func:`metafunc.parametrize(indirect=True) <pytest.Metafunc.parametrize>` 调用对测试函数/类进行参数化时，实际上已经使用了 ``request.param``。

当然，结合参数化和作用域是完全可以的：

.. code-block:: python

    @pytest.fixture(scope="session", params=["mysql", "pg"])
    def db(request):
        if request.param == "mysql":
            db = MySQL()
        elif request.param == "pg":
            db = PG()
        request.addfinalizer(db.destroy)  # 会话结束时销毁
        return db

这将执行需要每会话 "db" 资源的所有测试两次，接收由对工厂函数的两次相应调用创建的值。


使用 @fixture 装饰器时无需 ``pytest_funcarg__`` 前缀
-------------------------------------------------------------------

使用 ``@fixture`` 装饰器时，函数的名称表示可以作为函数参数访问资源的名称：

.. code-block:: python

    @pytest.fixture()
    def db(request): ...

可以作为 funcarg 资源请求的名称是 ``db``。

你仍然可以使用 "旧的" 非装饰器方式来指定 funcarg 工厂：

.. code-block:: python

    def pytest_funcarg__db(request): ...

但这样一来就无法定义作用域和参数化。
因此建议使用工厂装饰器。


解决每会话设置 / 自动使用 fixtures
--------------------------------------------------------------

pytest 长期以来提供了 pytest_configure 和 pytest_sessionstart 钩子，它们经常用于设置全局资源。这存在几个问题：

1. 在分布式测试中，管理进程会设置测试资源而这些资源从未被使用，因为它只协调工作进程的测试运行活动。

2. 如果你只执行收集（使用 "--collect-only"），资源设置仍将执行。

3. 如果 pytest_sessionstart 包含在某些子目录的 conftest.py 文件中，它将不会被调用。这源于这样一个事实：这个钩子实际上用于报告，特别是平台/自定义信息的测试标题。

此外，除了实现一个 ``pytest_runtest_setup()`` 钩子并自己管理作用域/缓存外，不容易从插件或 conftest 文件定义有作用域的设置。而且在参数化方面几乎不可能做到这一点，因为 ``pytest_runtest_setup()`` 是在测试执行期间调用的，而参数化发生在收集时。

因此，pytest_configure/session/runtest_setup 通常不适合实现常见的 fixture 需求。因此，pytest-2.3 引入了 :ref:`autouse fixtures`，它们完全集成通用的 :ref:`fixture 机制 <fixture>`，并淘汰了许多以前使用的 pytest 钩子。


Funcargs/fixture 发现在收集时进行
---------------------------------------------------------------------

从 pytest-2.3 起，fixture/funcarg 工厂的发现是在收集时处理的。这对于大型测试套件尤其高效。此外，将来调用 "pytest --collect-only" 应该能够显示大量设置信息，因此提供了一个很好的方法来获取项目中 fixture 管理的概览。

.. _`compatibility notes`:

.. _`funcargscompat`:

结论和兼容性说明
---------------------------------------------------------

funcargs 最初在 pytest-2.0 中引入。在 pytest-2.3 中，该机制被扩展和精炼，现在被描述为 fixtures：

* 以前 funcarg 工厂使用特殊的 ``pytest_funcarg__NAME`` 前缀指定，而不是使用 ``@pytest.fixture`` 装饰器。

* 工厂接收到一个 ``request`` 对象，该对象通过 ``request.cached_setup()`` 调用管理缓存，并通过 ``request.getfuncargvalue()`` 调用允许使用其他 funcargs。这些复杂的 API 使得很难进行适当的参数化并实现资源缓存。新的 :py:func:`pytest.fixture` 装饰器允许声明作用域，让 pytest 为你处理一切。

* 如果你使用了参数化并且使用了 ``request.cached_setup()`` 的 funcarg 工厂，建议花几分钟时间简化你的 fixture 函数代码以使用 :ref:`@pytest.fixture` 装饰器。这也将允许利用按资源自动分组测试的优势。
