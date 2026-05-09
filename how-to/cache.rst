.. _`cache_provider`:
.. _cache:


如何重新运行失败的测试并在测试运行之间保持状态
===============================================================



用法
---------

该插件提供两个命令行选项来重新运行上次 ``pytest`` 调用中的失败：

* :option:`--lf, --last-failed <--lf>` - 仅重新运行失败。
* :option:`--ff, --failed-first <--ff>` - 先运行失败的测试，然后运行其余的测试。

对于清理（通常不需要），:option:`--cache-clear` 选项允许在测试运行之前删除所有跨会话缓存内容。

其他插件可以访问 `config.cache`_ 对象来在 ``pytest`` 调用之间设置/获取 **json 可编码** 值。

.. note::

    此插件默认启用，但如果需要可以禁用：参见
    :ref:`cmdunregister`（此插件的内部名称是
    ``cacheprovider``）。


仅重新运行失败或先运行失败
-----------------------------------------------

首先，让我们创建 50 个测试调用，其中只有 2 个失败：

.. code-block:: python

    # test_50.py 的内容
    import pytest


    @pytest.mark.parametrize("i", range(50))
    def test_num(i):
        if i in (17, 25):
            pytest.fail("bad luck")

如果你第一次运行此测试，你将看到两个失败：

.. code-block:: pytest

    $ pytest -q
    .................F.......F........................                   [100%]
    ================================= FAILURES =================================
    _______________________________ test_num[17] _______________________________

    i = 17

        @pytest.mark.parametrize("i", range(50))
        def test_num(i):
            if i in (17, 25):
    >           pytest.fail("bad luck")
    E           Failed: bad luck

    test_50.py:7: Failed
    _______________________________ test_num[25] _______________________________

    i = 25

        @pytest.mark.parametrize("i", range(50))
        def test_num(i):
            if i in (17, 25):
    >           pytest.fail("bad luck")
    E           Failed: bad luck

    test_50.py:7: Failed
    ========================= short test summary info ==========================
    FAILED test_50.py::test_num[17] - Failed: bad luck
    FAILED test_50.py::test_num[25] - Failed: bad luck
    2 failed, 48 passed in 0.12s

如果你随后使用 :option:`--lf` 运行：

.. code-block:: pytest

    $ pytest --lf
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 2 items
    run-last-failure: rerun previous 2 failures

    test_50.py FF                                                        [100%]

    ================================= FAILURES =================================
    _______________________________ test_num[17] _______________________________

    i = 17

        @pytest.mark.parametrize("i", range(50))
        def test_num(i):
            if i in (17, 25):
    >           pytest.fail("bad luck")
    E           Failed: bad luck

    test_50.py:7: Failed
    _______________________________ test_num[25] _______________________________

    i = 25

        @pytest.mark.parametrize("i", range(50))
        def test_num(i):
            if i in (17, 25):
    >           pytest.fail("bad luck")
    E           Failed: bad luck

    test_50.py:7: Failed
    ========================= short test summary info ==========================
    FAILED test_50.py::test_num[17] - Failed: bad luck
    FAILED test_50.py::test_num[25] - Failed: bad luck
    ============================ 2 failed in 0.12s =============================

你只运行了上次运行中两个失败的测试，而 48 个通过的测试没有被运行（"deselected"）。

现在，如果你使用 :option:`--ff` 选项运行，所有测试都将被运行，但先前的失败将首先执行（可以从 ``FF`` 和点的序列中看出）：

.. code-block:: pytest

    $ pytest --ff
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 50 items
    run-last-failure: rerun previous 2 failures first

    test_50.py FF................................................        [100%]

    ================================= FAILURES =================================
    _______________________________ test_num[17] _______________________________

    i = 17

        @pytest.mark.parametrize("i", range(50))
        def test_num(i):
            if i in (17, 25):
    >           pytest.fail("bad luck")
    E           Failed: bad luck

    test_50.py:7: Failed
    _______________________________ test_num[25] _______________________________

    i = 25

        @pytest.mark.parametrize("i", range(50))
        def test_num(i):
            if i in (17, 25):
    >           pytest.fail("bad luck")
    E           Failed: bad luck

    test_50.py:7: Failed
    ========================= short test summary info ==========================
    FAILED test_50.py::test_num[17] - Failed: bad luck
    FAILED test_50.py::test_num[25] - Failed: bad luck
    ======================= 2 failed, 48 passed in 0.12s =======================

.. _`config.cache`:

新的 :option:`--nf, --new-first <--nf>` 选项：先运行新测试，然后运行其余测试，在这两种情况下，测试也按文件修改时间排序，最近的文件在前。

上一次运行中没有失败时的行为
---------------------------------------------

:option:`--lfnf, --last-failed-no-failures <--lfnf>` 选项管理 :option:`--last-failed` 的行为。决定何时没有先前（已知）失败或未找到缓存的 ``lastfailed`` 数据时是否执行测试。

有两个选项：

* ``all``：当没有已知的测试失败时，运行所有测试（完整测试套件）。这是默认值。
* ``none``：当没有已知的测试失败时，仅显示一条消息说明此情况并成功退出。

示例：

.. code-block:: bash

    pytest --last-failed --last-failed-no-failures all    # 运行完整的测试套件（默认行为）
    pytest --last-failed --last-failed-no-failures none   # 不运行测试并成功退出

新的 config.cache 对象
--------------------------------

.. regendoc:wipe

插件或 conftest.py 支持代码可以使用 pytest ``config`` 对象获取缓存的值。这里有一个基本示例插件，它实现了一个 :ref:`fixture <fixture>`，跨 pytest 调用重用先前创建的状态：

.. code-block:: python

    # test_caching.py 的内容
    import pytest


    def expensive_computation():
        print("running expensive computation...")


    @pytest.fixture
    def mydata(pytestconfig):
        val = pytestconfig.cache.get("example/value", None)
        if val is None:
            expensive_computation()
            val = 42
            pytestconfig.cache.set("example/value", val)
        return val


    def test_function(mydata):
        assert mydata == 23

如果你第一次运行此命令，你会看到打印语句：

.. code-block:: pytest

    $ pytest -q
    F                                                                    [100%]
    ================================= FAILURES =================================
    ______________________________ test_function _______________________________

    mydata = 42

        def test_function(mydata):
    >       assert mydata == 23
    E       assert 42 == 23

    test_caching.py:19: AssertionError
    -------------------------- Captured stdout setup ---------------------------
    running expensive computation...
    ========================= short test summary info ==========================
    FAILED test_caching.py::test_function - assert 42 == 23
    1 failed in 0.12s

如果你第二次运行，该值将从缓存中检索，不会打印任何内容：

.. code-block:: pytest

    $ pytest -q
    F                                                                    [100%]
    ================================= FAILURES =================================
    ______________________________ test_function _______________________________

    mydata = 42

        def test_function(mydata):
    >       assert mydata == 23
    E       assert 42 == 23

    test_caching.py:19: AssertionError
    ========================= short test summary info ==========================
    FAILED test_caching.py::test_function - assert 42 == 23
    1 failed in 0.12s

有关更多详细信息，请参阅 :fixture:`config.cache fixture <cache>`。


检查缓存内容
------------------------

你可以随时使用 :option:`--cache-show` 命令行选项查看缓存的内容：

.. code-block:: pytest

    $ pytest --cache-show
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    cachedir: /home/sweet/project/.pytest_cache
    --------------------------- cache values for '*' ---------------------------
    cache/lastfailed contains:
      {'test_caching.py::test_function': True}
    cache/nodeids contains:
      ['test_caching.py::test_function']
    example/value contains:
      42

    ========================== no tests ran in 0.12s ===========================

:option:`--cache-show` 接受一个可选参数来指定用于过滤的 glob 模式：

.. code-block:: pytest

    $ pytest --cache-show example/*
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    cachedir: /home/sweet/project/.pytest_cache
    ----------------------- cache values for 'example/*' -----------------------
    example/value contains:
      42

    ========================== no tests ran in 0.12s ===========================

清除缓存内容
------------------------

你可以通过添加 :option:`--cache-clear` 选项来指示 pytest 清除所有缓存文件和值，如下所示：

.. code-block:: bash

    pytest --cache-clear

对于来自持续集成服务器的调用，建议使用此选项，因为隔离和正确性比速度更重要。


.. _cache stepwise:

Stepwise
--------

作为 :option:`--lf` :option:`-x` 的替代方案，特别是当你预计测试套件的大部分会失败时，:option:`--sw, --stepwise <--sw>` 允许你一次修复一个。测试套件将运行直到第一个失败然后停止。在下一次调用时，测试将从最后一个失败的测试继续，然后一直运行到下一个失败的测试。你可以使用 :option:`--stepwise-skip` 选项忽略一个失败的测试，而在第二个失败的测试时停止测试执行。如果你卡在一个失败的测试上，想忽略它以后再处理，这很有用。提供 ``--stepwise-skip`` 也会隐式启用 ``--stepwise``。
