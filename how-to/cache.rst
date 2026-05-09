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

