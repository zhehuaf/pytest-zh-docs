
.. _`captures`:

如何捕获 stdout/stderr 输出
=========================================================

pytest 通过 :option:`--capture=` 命令行参数或使用 fixtures 来拦截 stdout 和 stderr。``--capture=`` 标志配置报告，而 fixtures 提供更细粒度的控制，并允许在测试期间检查输出。报告可以使用 :option:`-r` 标志进行自定义。

默认的 stdout/stderr/stdin 捕获行为
---------------------------------------------------------

在测试执行期间，发送到 ``stdout`` 和 ``stderr`` 的任何输出都会被捕获。如果测试或设置方法失败，其相应的捕获输出通常将与失败回溯一起显示。（此行为可以通过 :option:`--show-capture` 命令行选项配置）。

此外，``stdin`` 被设置为将在尝试从它读取时失败的 "null" 对象，因为很少希望在运行自动化测试时等待交互式输入。

默认情况下，捕获是通过拦截对低级文件描述符的写入来完成的。这允许捕获简单打印语句的输出以及由测试启动的子进程的输出。

.. _capture-method:

设置捕获方法或禁用捕获
-------------------------------------------------

``pytest`` 可以执行捕获的方式有三种：

* ``fd``\（文件描述符）级别捕获（默认）：所有写入操作系统文件描述符 1 和 2 的操作都将被捕获。

* ``sys`` 级别捕获：只捕获写入 Python 文件 ``sys.stdout`` 和 ``sys.stderr`` 的操作。不执行对文件描述符的写入捕获。

* ``tee-sys`` 捕获：Python 写入 ``sys.stdout`` 和 ``sys.stderr`` 的操作将被捕获，但写入也会传递给实际的 ``sys.stdout`` 和 ``sys.stderr``。这允许输出被 "实时打印" 并捕获以供插件使用，例如 junitxml（pytest 5.4 中的新功能）。

.. _`disable capturing`:

你可以从命令行影响输出捕获机制：

.. code-block:: bash

    pytest -s                  # 禁用所有捕获
    pytest --capture=sys       # 用内存文件替换 sys.stdout/stderr
    pytest --capture=fd        # 也将文件描述符 1 和 2 指向临时文件
    pytest --capture=tee-sys   # 结合 'sys' 和 '-s'，捕获 sys.stdout/stderr
                               # 并传递给实际的 sys.stdout/stderr

.. _printdebugging:

使用 print 语句进行调试
---------------------------------------------------

默认捕获 stdout/stderr 输出的一个主要好处是你可以使用 print 语句进行调试：

.. code-block:: python

    # test_module.py 的内容


    def setup_function(function):
        print("setting up", function)


    def test_func1():
        assert True


    def test_func2():
        assert False


并运行此模块将精确显示失败函数的输出并隐藏另一个：

.. code-block:: pytest

    $ pytest
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 2 items

    test_module.py .F                                                    [100%]

    ================================= FAILURES =================================
    ________________________________ test_func2 ________________________________

        def test_func2():
    >       assert False
    E       assert False

    test_module.py:12: AssertionError
    -------------------------- Captured stdout setup ---------------------------
    setting up <function test_func2 at 0xdeadbeef0001>
    ========================= short test summary info ==========================
    FAILED test_module.py::test_func2 - assert False
    ======================= 1 failed, 1 passed in 0.12s ========================

.. _accessing-captured-output:

从测试函数访问捕获的输出
---------------------------------------------------

:fixture:`capsys`、:fixture:`capteesys`、:fixture:`capsysbinary`、:fixture:`capfd` 和 :fixture:`capfdbinary` fixtures 允许访问测试执行期间创建的 ``stdout``/``stderr`` 输出。

以下是一个执行一些与输出相关的检查的示例测试函数：

.. code-block:: python

    def test_myoutput(capsys):  # 或使用 "capfd" 进行 fd 级别
        print("hello")
        sys.stderr.write("world\n")
        captured = capsys.readouterr()
        assert captured.out == "hello\n"
        assert captured.err == "world\n"
        print("next")
        captured = capsys.readouterr()
        assert captured.out == "next\n"

``readouterr()`` 调用会快照迄今为止的输出 —— 并且捕获将继续。测试函数完成后，原始流将被恢复。以这种方式使用 :fixture:`capsys` 可以让你的测试不必关心设置/重置输出流，并且也能很好地与 pytest 自己的每测试捕获交互。

``readouterr()`` 的返回值是一个 ``namedtuple``，有两个属性，``out`` 和 ``err``。

如果被测代码写入非文本数据（``bytes``），你可以使用 :fixture:`capsysbinary` fixture 来捕获它，该 fixture 从 ``readouterr`` 方法返回 ``bytes``。

如果你想在文件描述符级别捕获，你可以使用 :fixture:`capfd` fixture，它提供完全相同的接口，但也允许捕获直接写入操作系统级别输出流（FD1 和 FD2）的库或子进程的输出。类似于 :fixture:`capsysbinary`，:fixture:`capfdbinary` 可用于在文件描述符级别捕获 ``bytes``。


要在测试中临时禁用捕获，捕获 fixtures 有一个 ``disabled()`` 方法，可以用作上下文管理器，在 ``with`` 块内禁用捕获：

.. code-block:: python

    def test_disabling_capturing(capsys):
        print("this output is captured")
        with capsys.disabled():
            print("output not captured, going directly to sys.stdout")
        print("this output is also captured")

.. note::

   当使用捕获 fixture 如 :fixture:`capsys` 或 :fixture:`capfd` 时，
   它优先于通过命令行选项（如 ``-s`` 或 ``--capture=no``）设置的全局捕获配置。

   这意味着即使禁用了全局捕获，在使用捕获 fixture 的测试中产生的输出仍将被捕获并通过 ``readouterr()`` 可用。
