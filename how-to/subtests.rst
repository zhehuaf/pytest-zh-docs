.. _subtests:

如何使用 subtests
===================

.. versionadded:: 9.0

.. note::

    此功能是实验性的。其行为，特别是如何报告失败，可能会在未来版本中演变。但是，核心功能和使用被认为是稳定的。

pytest 允许在正常测试中对断言进行分组，称为 *subtests*。

Subtests 是参数化的替代方案，特别适用于在收集时不知道确切参数化值的情况。


.. code-block:: python

    # test_subtest.py 的内容


    def test(subtests):
        for i in range(5):
            with subtests.test(msg="custom message", i=i):
                assert i % 2 == 0

每个断言失败或错误都会被上下文管理器捕获并单独报告：

.. code-block:: pytest

    $ pytest -q test_subtest.py
    uuuuuF                                                               [100%]
    ================================= FAILURES =================================
    _______________________ test [custom message] (i=1) ________________________

        subtests = <_pytest.subtests.Subtests object at 0xdeadbeef0001>

            def test(subtests):
                for i in range(5):
                    with subtests.test(msg="custom message", i=i):
        >               assert i % 2 == 0
        E               assert (1 % 2) == 0

        test_subtest.py:6: AssertionError
    _______________________ test [custom message] (i=3) ________________________

        subtests = <_pytest.subtests.Subtests object at 0xdeadbeef0001>

            def test(subtests):
                for i in range(5):
                    with subtests.test(msg="custom message", i=i):
        >               assert i % 2 == 0
        E               assert (3 % 2) == 0

        test_subtest.py:6: AssertionError
    ___________________________________ test ___________________________________
    contains 2 failed subtests
    ========================= short test summary info ==========================
    SUBFAILED[custom message] (i=1) test_subtest.py::test - assert (1 % 2) == 0
    SUBFAILED[custom message] (i=3) test_subtest.py::test - assert (3 % 2) == 0
    FAILED test_subtest.py::test - contains 2 failed subtests
    3 failed, 3 subtests passed in 0.12s

在上面的输出中：

* Subtest 失败报告为 ``SUBFAILED``。
* Subtests 首先报告，"顶层" 测试在最后单独报告。

请注意，可以在同一测试中多次使用 ``subtests``，甚至与 ``subtests.test`` 块外的普通断言混合使用：

.. code-block:: python

    def test(subtests):
        for i in range(5):
            with subtests.test("stage 1", i=i):
                assert i % 2 == 0

        assert func() == 10

        for i in range(10, 20):
            with subtests.test("stage 2", i=i):
                assert i % 2 == 0

.. note::

    参见 :ref:`parametrize` 了解 subtests 的替代方案。


详细程度
---------

默认情况下，只显示 subtest 失败。更高的详细程度（:option:`-v`）还将显示 通过 subtests 的进度输出。

可以通过设置 :confval:`verbosity_subtests` 来控制 subtests 的详细程度。


类型提示
--------

:class:`pytest.Subtests` 被导出以便可用于类型注解：

.. code-block:: python

    def test(subtests: pytest.Subtests) -> None: ...

.. _parametrize_vs_subtests:

参数化 vs Subtests
---------------------------

虽然 :ref:`传统的 pytest 参数化 <parametrize>` 和 ``subtests`` 相似，但它们有重要的区别和使用场景。


参数化
~~~~~~~~~~~~~~~

* 在收集时发生。
* 生成单独的测试。
* 参数化测试可以从命令行引用。
* 与处理测试执行的插件（如 :option:`--last-failed`）配合良好。
* 适用于决策表测试。

Subtests
~~~~~~~~

* 在测试执行期间发生。
* 在收集时未知。
* 可以动态生成。
* 不能从命令行单独引用。
* 处理测试执行的插件不能针对单个 subtests。
* subtest 中的断言失败不会中断测试，让用户可以在同一报告中看到所有失败。


.. note::

    此功能最初在 `pytest-subtests <https://github.com/pytest-dev/pytest-subtests>`__ 中作为单独插件实现，但自 ``9.0`` 起已合并到核心中。

    核心实现应该与插件实现兼容，但它不包含用于控制 subtest 输出的自定义命令行选项。
