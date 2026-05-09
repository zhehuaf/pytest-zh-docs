.. _monkeypatching:

如何 monkeypatch/模拟模块和环境
================================================================

.. currentmodule:: pytest

有时测试需要调用依赖于全局设置或调用不容易测试的代码（如网络访问）的功能。``monkeypatch`` fixture 帮助您安全地设置/删除属性、字典项或环境变量，或修改 ``sys.path`` 以进行导入。

``monkeypatch`` fixture 提供这些辅助方法来安全地在测试中打补丁和模拟功能：

* :meth:`monkeypatch.setattr(obj, name, value, raising=True) <pytest.MonkeyPatch.setattr>`
* :meth:`monkeypatch.delattr(obj, name, raising=True) <pytest.MonkeyPatch.delattr>`
* :meth:`monkeypatch.setitem(mapping, name, value) <pytest.MonkeyPatch.setitem>`
* :meth:`monkeypatch.delitem(obj, name, raising=True) <pytest.MonkeyPatch.delitem>`
* :meth:`monkeypatch.setenv(name, value, prepend=None) <pytest.MonkeyPatch.setenv>`
* :meth:`monkeypatch.delenv(name, raising=True) <pytest.MonkeyPatch.delenv>`
* :meth:`monkeypatch.syspath_prepend(path) <pytest.MonkeyPatch.syspath_prepend>`
* :meth:`monkeypatch.chdir(path) <pytest.MonkeyPatch.chdir>`
* :meth:`monkeypatch.context() <pytest.MonkeyPatch.context>`


所有修改将在请求的测试函数或 fixture 完成后撤消。``raising`` 参数决定如果设置/删除操作的目标不存在，是否会引发 ``KeyError`` 或 ``AttributeError``。

考虑以下场景：

1. 为测试修改函数的行为或类的属性，例如有 API 调用或数据库连接你不会为测试进行，但你知道预期的输出应该是什么。使用 :py:meth:`monkeypatch.setattr <MonkeyPatch.setattr>` 用您期望的测试行为修补函数或属性。这可以包括你自己的函数。使用 :py:meth:`monkeypatch.delattr <MonkeyPatch.delattr>` 删除测试的函数或属性。

2. 修改字典的值，例如你有一个全局配置，你想为某些测试用例修改。使用 :py:meth:`monkeypatch.setitem <MonkeyPatch.setitem>` 为测试修补字典。:py:meth:`monkeypatch.delitem <MonkeyPatch.delitem>` 可用于删除项目。

3. 为测试修改环境变量，例如测试如果环境变量缺失程序的行为，或将多个值设置为已知变量。:py:meth:`monkeypatch.setenv <MonkeyPatch.setenv>` 和 :py:meth:`monkeypatch.delenv <MonkeyPatch.delenv>` 可用于这些补丁。

4. 使用 ``monkeypatch.setenv("PATH", value, prepend=os.pathsep)`` 修改 ``$PATH``，和 :py:meth:`monkeypatch.chdir <MonkeyPatch.chdir>` 在测试期间更改当前工作目录的上下文。

5. 使用 :py:meth:`monkeypatch.syspath_prepend <MonkeyPatch.syspath_prepend>` 修改 ``sys.path``，它还将调用 ``pkg_resources.fixup_namespace_packages`` 和 :py:func:`importlib.invalidate_caches`。

6. 使用 :py:meth:`monkeypatch.context <MonkeyPatch.context>` 仅在特定范围内应用补丁，这有助于控制复杂 fixtures 或对 stdlib 的补丁的拆卸。

参见 `monkeypatch blog post`_ 了解一些介绍材料和对其动机的讨论。

.. _`monkeypatch blog post`: https://tetamap.wordpress.com//2009/03/03/monkeypatching-in-unit-tests-done-right/

Monkeypatching 函数
-----------------------

考虑一个你正在使用用户目录的场景。在测试的上下文中，你不希望你的测试依赖于运行用户。``monkeypatch`` 可用于修补依赖于用户的函数以始终返回特定值。

在此示例中，:py:meth:`monkeypatch.setattr <MonkeyPatch.setattr>` 用于修补 ``Path.home``，以便在运行测试时始终使用已知的测试路径 ``Path("/abc")``。这消除了测试对运行用户的任何依赖。
:py:meth:`monkeypatch.setattr <MonkeyPatch.setattr>` 必须在将使用修补函数的函数被调用之前调用。
测试函数完成后，``Path.home`` 修改将被撤消。

.. code-block:: python

    # test_module.py 的内容，包含源代码和测试
    from pathlib import Path


    def getssh():
        """返回扩展的主目录 ssh 路径的简单函数。"""
        return Path.home() / ".ssh"


    def test_getssh(monkeypatch):
        # 模拟返回函数以替换 Path.home
        # 始终返回 '/abc'
        def mockreturn():
            return Path("/abc")

        # 应用 monkeypatch 以用上面定义的 mockreturn 行为替换 Path.home
        monkeypatch.setattr(Path, "home", mockreturn)

        # 调用 getssh() 将在此测试中使用 mockreturn 代替 Path.home
        x = getssh()
        assert x == Path("/abc/.ssh")

Monkeypatching 返回对象：构建模拟类
------------------------------------------------------

:py:meth:`monkeypatch.setattr <MonkeyPatch.setattr>` 可以与类一起使用，以模拟函数返回的对象而不是值。
想象一个简单的函数，接受一个 API url 并返回 json 响应。

.. code-block:: python

    # app.py 的内容，一个简单的 API 检索示例
    import requests


    def get_json(url):
        """接受一个 URL，返回 JSON。"""
        r = requests.get(url)
        return r.json()

我们需要模拟 ``r``，即返回的响应对象以进行测试。
模拟的 ``r`` 需要一个 ``.json()`` 方法，该方法返回一个字典。
这可以在我们的测试文件中通过定义一个表示 ``r`` 的类来完成。

.. code-block:: python

    # test_app.py 的内容，一个我们 API 检索的简单测试
    # 为了 monkeypatching 的目的导入 requests
    import requests

    # 包含 get_json() 函数的 app.py
    # 这是前面的代码块示例
    import app


    # 自定义类作为模拟返回值
    # 将覆盖从 requests.get 返回的 requests.Response
    class MockResponse:
        # 模拟 json() 方法始终返回特定的测试字典
        @staticmethod
        def json():
            return {"mock_key": "mock_response"}


    def test_get_json(monkeypatch):
        # 可以传递任何参数，mock_get() 将始终返回我们的模拟对象
        def mock_get(*args, **kwargs):
            return MockResponse()

        # 应用 monkeypatch 将 requests.get 替换为 mock_get
        monkeypatch.setattr(requests, "get", mock_get)

        # app.get_json 包含 requests.get，使用 monkeypatch
        result = app.get_json("https://fakeurl")
        assert result["mock_key"] == "mock_response"


``monkeypatch`` 使用我们的 ``mock_get`` 函数为 ``requests.get`` 应用模拟。
``mock_get`` 函数返回 ``MockResponse`` 类的一个实例，该类定义了一个 ``json()`` 方法，该方法返回一个已知的测试字典，不需要任何外部 API 连接。

你可以为要测试的场景构建适当复杂程度的 ``MockResponse`` 类。例如，它可以包含一个始终返回 ``True`` 的 ``ok`` 属性，或根据输入字符串从模拟的 ``json()`` 方法返回不同的值。

这个模拟可以使用 ``fixture`` 跨测试共享：

.. code-block:: python

    # test_app.py 的内容，一个我们 API 检索的简单测试
    import pytest
    import requests

    # 包含 get_json() 函数的 app.py
    import app


    # 自定义类作为 requests.get() 的模拟返回值
    class MockResponse:
        @staticmethod
        def json():
            return {"mock_key": "mock_response"}


    # 将 monkeypatched requests.get 移到 fixture 中
    @pytest.fixture
    def mock_response(monkeypatch):
        """Requests.get() 被模拟返回 {'mock_key':'mock_response'}。"""

        def mock_get(*args, **kwargs):
            return MockResponse()

        monkeypatch.setattr(requests, "get", mock_get)


    # 注意我们的测试使用了自定义 fixture 而不是直接使用 monkeypatch
    def test_get_json(mock_response):
        result = app.get_json("https://fakeurl")
        assert result["mock_key"] == "mock_response"


此外，如果模拟被设计为应用于所有测试，则可以将 ``fixture`` 移到 ``conftest.py`` 文件中，并使用 ``autouse=True`` 选项。


全局补丁示例：阻止 "requests" 进行远程操作
------------------------------------------------------------------

如果你想阻止 "requests" 库在所有测试中执行 http 请求，你可以这样做：

.. code-block:: python

    # conftest.py 的内容
    import pytest


    @pytest.fixture(autouse=True)
    def no_requests(monkeypatch):
        """为所有测试删除 requests.sessions.Session.request。"""
        monkeypatch.delattr("requests.sessions.Session.request")

这个 autouse fixture 将为每个测试函数执行，并删除方法 ``request.session.Session.request``，因此测试中任何创建 http 请求的尝试都将失败。


.. note::

    请注意，不建议修补内置函数（如 ``open``、``compile`` 等），因为这可能会破坏 pytest 的内部机制。如果无法避免，传递 :option:`--tb=native`、:option:`--assert=plain` 和 :option:`--capture=no` 可能会有所帮助，尽管不能保证。

.. note::

    注意修补 ``stdlib`` 函数和一些由 pytest 使用的第三方库可能会破坏 pytest 本身，因此在这些情况下建议使用 :meth:`MonkeyPatch.context` 将修补限制到你要测试的块：

    .. code-block:: python

        import functools


        def test_partial(monkeypatch):
            with monkeypatch.context() as m:
                m.setattr(functools, "partial", 3)
                assert functools.partial == 3

    参见 :issue:`3290` 了解详情。


Monkeypatching 环境变量
------------------------------------

如果你正在使用环境变量，你经常需要安全地更改值或从系统中删除它们以进行测试。``monkeypatch`` 提供了一种使用 ``setenv`` 和 ``delenv`` 方法来实现此目的的机制。我们的示例测试代码：

.. code-block:: python

    # 我们原始代码文件的内容，例如 code.py
    import os


    def get_os_user_lower():
        """简单的检索函数。
        返回小写的 USER 或引发 OSError。"""
        username = os.getenv("USER")

        if username is None:
            raise OSError("USER environment is not set.")

        return username.lower()

有两个可能的路径。第一，``USER`` 环境变量设置为一个值。第二，``USER`` 环境变量不存在。使用 ``monkeypatch``，这两个路径都可以安全地测试，而不会影响运行环境：

.. code-block:: python

    # 我们测试文件的内容，例如 test_code.py
    import pytest


    def test_upper_to_lower(monkeypatch):
        """设置 USER 环境变量以断言行为。"""
        monkeypatch.setenv("USER", "TestingUser")
        assert get_os_user_lower() == "testinguser"


    def test_raise_exception(monkeypatch):
        """删除 USER 环境变量并断言引发 OSError。"""
        monkeypatch.delenv("USER", raising=False)

        with pytest.raises(OSError):
            _ = get_os_user_lower()

这种行为可以移到 ``fixture`` 结构中并跨测试共享：

.. code-block:: python

    # 我们测试文件的内容，例如 test_code.py
    import pytest


    @pytest.fixture
    def mock_env_user(monkeypatch):
        monkeypatch.setenv("USER", "TestingUser")


    @pytest.fixture
    def mock_env_missing(monkeypatch):
        monkeypatch.delenv("USER", raising=False)


    # 注意测试引用了 fixtures 进行模拟
    def test_upper_to_lower(mock_env_user):
        assert get_os_user_lower() == "testinguser"


    def test_raise_exception(mock_env_missing):
        with pytest.raises(OSError):
            _ = get_os_user_lower()


Monkeypatching 字典
--------------------------

:py:meth:`monkeypatch.setitem <MonkeyPatch.setitem>` 可用于在测试期间安全地将字典的值设置为特定值。以这个简化的连接字符串示例为例：

.. code-block:: python

    # app.py 的内容，生成一个简单的连接字符串
    DEFAULT_CONFIG = {"user": "user1", "database": "db1"}


    def create_connection_string(config=None):
        """根据输入或默认值创建连接字符串。"""
        config = config or DEFAULT_CONFIG
        return f"User Id={config['user']}; Location={config['database']};"

为了测试目的，我们可以将 ``DEFAULT_CONFIG`` 字典修补为特定值。

.. code-block:: python

    # test_app.py 的内容
    # app.py 包含连接字符串函数（前面的代码块）
    import app


    def test_connection(monkeypatch):
        # 仅为此测试将 DEFAULT_CONFIG 的值修补为特定的测试值
        monkeypatch.setitem(app.DEFAULT_CONFIG, "user", "test_user")
        monkeypatch.setitem(app.DEFAULT_CONFIG, "database", "test_db")

        # 基于模拟的期望结果
        expected = "User Id=test_user; Location=test_db;"

        # 测试使用 monkeypatched 的字典设置
        result = app.create_connection_string()
        assert result == expected

你可以使用 :py:meth:`monkeypatch.delitem <MonkeyPatch.delitem>` 删除值。

.. code-block:: python

    # test_app.py 的内容
    import pytest

    # app.py 包含连接字符串函数
    import app


    def test_missing_user(monkeypatch):
        # 修补 DEFAULT_CONFIG 使其缺少 'user' 键
        monkeypatch.delitem(app.DEFAULT_CONFIG, "user", raising=False)

        # 期望 KeyError，因为没有传递配置，且默认值现在缺少 'user' 条目。
        with pytest.raises(KeyError):
            _ = app.create_connection_string()


Fixtures 的模块化使你能够为每个潜在的模拟定义单独的 fixtures，并在需要的测试中引用它们。

.. code-block:: python

    # test_app.py 的内容
    import pytest

    # app.py 包含连接字符串函数
    import app


    # 所有模拟都移到单独的 fixtures 中
    @pytest.fixture
    def mock_test_user(monkeypatch):
        """将 DEFAULT_CONFIG 的 user 设置为 test_user。"""
        monkeypatch.setitem(app.DEFAULT_CONFIG, "user", "test_user")


    @pytest.fixture
    def mock_test_database(monkeypatch):
        """将 DEFAULT_CONFIG 的 database 设置为 test_db。"""
        monkeypatch.setitem(app.DEFAULT_CONFIG, "database", "test_db")


    @pytest.fixture
    def mock_missing_default_user(monkeypatch):
        """从 DEFAULT_CONFIG 中删除 user 键"""
        monkeypatch.delitem(app.DEFAULT_CONFIG, "user", raising=False)


    # 测试只引用需要的 fixture 模拟
    def test_connection(mock_test_user, mock_test_database):
        expected = "User Id=test_user; Location=test_db;"

        result = app.create_connection_string()
        assert result == expected


    def test_missing_user(mock_missing_default_user):
        with pytest.raises(KeyError):
            _ = app.create_connection_string()


.. currentmodule:: pytest

API 参考
-------------

查阅 :class:`MonkeyPatch` 类的文档。
