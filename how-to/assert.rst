.. _`assert`:

如何在测试中编写和报告断言
==================================================

.. _`assert with the assert statement`:

使用 ``assert`` 语句进行断言
---------------------------------------------------------

``pytest`` 允许你使用标准的 Python ``assert`` 来验证 Python 测试中的期望值和实际值。例如，你可以编写以下内容：

.. code-block:: python

    # test_assert1.py 的内容
    def f():
        return 3


    def test_function():
        assert f() == 4

来断言你的函数返回某个值。如果此断言失败，你将看到函数调用的返回值：

.. code-block:: pytest

    $ pytest test_assert1.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 1 item

    test_assert1.py F                                                    [100%]

    ================================= FAILURES =================================
    ______________________________ test_function _______________________________

        def test_function():
    >       assert f() == 4
    E       assert 3 == 4
    E        +  where 3 = f()

    test_assert1.py:6: AssertionError
    ========================= short test summary info ==========================
    FAILED test_assert1.py::test_function - assert 3 == 4
    ============================ 1 failed in 0.12s =============================

``pytest`` 支持显示最常见子表达式的值，包括调用、属性、比较以及二元和一元运算符。（参见 :ref:`tbreportdemo`）。这允许你使用惯用的 Python 结构，而无需样板代码，同时不会丢失内省信息。

如果为断言指定了消息，如下所示：

.. code-block:: python

    assert a % 2 == 0, "value was odd, should be even"

它将与断言内省一起打印在回溯中。

有关断言内省的更多信息，请参见 :ref:`assert-details`。

.. _`assertraises`:

关于近似相等的断言
-------------------------------------

当比较浮点数值（或浮点数数组）时，小的舍入误差很常见。你可以使用 :func:`pytest.approx` 来代替 ``assert abs(a - b) < tol`` 或 ``numpy.isclose``：

.. code-block:: python

    import pytest
    import numpy as np


    def test_floats():
        assert (0.1 + 0.2) == pytest.approx(0.3)


    def test_arrays():
        a = np.array([1.0, 2.0, 3.0])
        b = np.array([0.9999, 2.0001, 3.0])
        assert a == pytest.approx(b)

``pytest.approx`` 适用于标量、列表、字典和 NumPy 数组。它还支持涉及 NaN 的比较。

详细信息请参见 :func:`pytest.approx`。

关于预期异常的断言
------------------------------------------

为了编写关于抛出异常的断言，你可以使用 :func:`pytest.raises` 作为上下文管理器，如下所示：

.. code-block:: python

    import pytest


    def test_zero_division():
        with pytest.raises(ZeroDivisionError):
            1 / 0

如果你需要访问实际的异常信息，可以使用：

.. code-block:: python

    def test_recursion_depth():
        with pytest.raises(RuntimeError) as excinfo:

            def f():
                f()

            f()
        assert "maximum recursion" in str(excinfo.value)

``excinfo`` 是一个 :class:`~pytest.ExceptionInfo` 实例，它是实际抛出异常的包装器。主要感兴趣的属性是 ``.type``、``.value`` 和 ``.traceback``。

注意 ``pytest.raises`` 将匹配异常类型或任何子类（就像标准的 ``except`` 语句）。如果你想检查代码块是否抛出确切的异常类型，需要显式检查：


.. code-block:: python

    def test_foo_not_implemented():
        def foo():
            raise NotImplementedError

        with pytest.raises(RuntimeError) as excinfo:
            foo()
        assert excinfo.type is RuntimeError

:func:`pytest.raises` 调用将会成功，即使函数抛出 :class:`NotImplementedError`，因为 :class:`NotImplementedError` 是 :class:`RuntimeError` 的子类；但是下面的 `assert` 语句会捕获问题。

匹配异常消息
~~~~~~~~~~~~~~~~~~~~~~~~~~~

你可以向上下文管理器传递 ``match`` 关键字参数来测试正则表达式是否匹配异常的字符串表示（类似于 ``unittest`` 中的 ``TestCase.assertRaisesRegex`` 方法）：

.. code-block:: python

    import pytest


    def myfunc():
        raise ValueError("Exception 123 raised")


    def test_match():
        with pytest.raises(ValueError, match=r".* 123 .*"):
            myfunc()

注意事项：

* ``match`` 参数使用 :func:`re.search` 函数进行匹配，所以在上面的例子中 ``match='123'`` 也会有效。
* ``match`` 参数也匹配 `PEP-678 <https://peps.python.org/pep-0678/>`__ 的 ``__notes__``。


.. _`assert-matching-exception-groups`:

关于预期异常组的断言
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

当预期出现 :exc:`BaseExceptionGroup` 或 :exc:`ExceptionGroup` 时，你可以使用 :class:`pytest.RaisesGroup`：

.. code-block:: python

    def test_exception_in_group():
        with pytest.RaisesGroup(ValueError):
            raise ExceptionGroup("group msg", [ValueError("value msg")])
        with pytest.RaisesGroup(ValueError, TypeError):
            raise ExceptionGroup("msg", [ValueError("foo"), TypeError("bar")])


它接受一个 ``match`` 参数，用于检查组消息，以及一个 ``check`` 参数，该参数接受一个任意的可调用对象，将组传递给它，只有当可调用对象返回 ``True`` 时才成功。

.. code-block:: python

    def test_raisesgroup_match_and_check():
        with pytest.RaisesGroup(BaseException, match="my group msg"):
            raise BaseExceptionGroup("my group msg", [KeyboardInterrupt()])
        with pytest.RaisesGroup(
            Exception, check=lambda eg: isinstance(eg.__cause__, ValueError)
        ):
            raise ExceptionGroup("", [TypeError()]) from ValueError()

它对结构和未包装的异常是严格的，不像 :ref:`except* <except_star>`，所以你可能需要设置 ``flatten_subgroups`` 和/或 ``allow_unwrapped`` 参数。

.. code-block:: python

    def test_structure():
        with pytest.RaisesGroup(pytest.RaisesGroup(ValueError)):
            raise ExceptionGroup("", (ExceptionGroup("", (ValueError(),)),))
        with pytest.RaisesGroup(ValueError, flatten_subgroups=True):
            raise ExceptionGroup("1st group", [ExceptionGroup("2nd group", [ValueError()])])
        with pytest.RaisesGroup(ValueError, allow_unwrapped=True):
            raise ValueError

要指定包含异常的更多详细信息，你可以使用 :class:`pytest.RaisesExc`

.. code-block:: python

    def test_raises_exc():
        with pytest.RaisesGroup(pytest.RaisesExc(ValueError, match="foo")):
            raise ExceptionGroup("", (ValueError("foo")))

如果你想在作为 :external+python:std:ref:`context manager <context-managers>` 之外进行匹配，它们都提供了一个方法 :meth:`pytest.RaisesGroup.matches` :meth:`pytest.RaisesExc.matches`。这在检查 ``.__context__`` 或 ``.__cause__`` 时很有用。

.. code-block:: python

    def test_matches():
        exc = ValueError()
        exc_group = ExceptionGroup("", [exc])
        if RaisesGroup(ValueError).matches(exc_group):
            ...
        # 如果匹配失败，`.fail_reason` 中提供了有用的错误信息
        r = RaisesExc(ValueError)
        assert r.matches(e), r.fail_reason

有关更多详细信息和示例，请查看 :class:`pytest.RaisesGroup` 和 :class:`pytest.RaisesExc` 的文档。

``ExceptionInfo.group_contains()``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

   这个辅助函数使检查特定异常的存在变得容易，但对于检查组是否*不包含*任何其他异常来说，它非常不好。所以这将通过：

    .. code-block:: python

       class EXTREMELYBADERROR(BaseException):
           """This is a very bad error to miss"""


       def test_for_value_error():
           with pytest.raises(ExceptionGroup) as excinfo:
               excs = [ValueError()]
               if very_unlucky():
                   excs.append(EXTREMELYBADERROR())
               raise ExceptionGroup("", excs)
           # 无论是否有其他异常，这都会通过。
           assert excinfo.group_contains(ValueError)
           # 你不能简单地列出所有你不希望在这里出现的异常。


   没有好的方法可以使用 :func:`excinfo.group_contains() <pytest.ExceptionInfo.group_contains>` 来确保你没有获得除预期异常之外的任何其他异常。
   你应该使用 :class:`pytest.RaisesGroup`，参见 :ref:`assert-matching-exception-groups`。

你也可以使用 :func:`excinfo.group_contains() <pytest.ExceptionInfo.group_contains>` 方法来测试作为 :class:`ExceptionGroup` 一部分返回的异常：

.. code-block:: python

    def test_exception_in_group():
        with pytest.raises(ExceptionGroup) as excinfo:
            raise ExceptionGroup(
                "Group message",
                [
                    RuntimeError("Exception 123 raised"),
                ],
            )
        assert excinfo.group_contains(RuntimeError, match=r".* 123 .*")
        assert not excinfo.group_contains(TypeError)

可选的 ``match`` 关键字参数的工作方式与 :func:`pytest.raises` 相同。

默认情况下，``group_contains()`` 将在嵌套 ``ExceptionGroup`` 实例的任何级别递归搜索匹配的异常。如果你只想在特定级别匹配异常，可以指定 ``depth`` 关键字参数；直接包含在顶层 ``ExceptionGroup`` 中的异常将匹配 ``depth=1``。

.. code-block:: python

    def test_exception_in_group_at_given_depth():
        with pytest.raises(ExceptionGroup) as excinfo:
            raise ExceptionGroup(
                "Group message",
                [
                    RuntimeError(),
                    ExceptionGroup(
                        "Nested group",
                        [
                            TypeError(),
                        ],
                    ),
                ],
            )
        assert excinfo.group_contains(RuntimeError, depth=1)
        assert excinfo.group_contains(TypeError, depth=2)
        assert not excinfo.group_contains(RuntimeError, depth=2)
        assert not excinfo.group_contains(TypeError, depth=1)

替代的 `pytest.raises` 形式（传统）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:func:`pytest.raises` 有一种替代形式，你传递一个将要执行的函数，以及 ``*args`` 和 ``**kwargs``。:func:`pytest.raises` 然后将使用这些参数执行函数并断言抛出给定的异常：

.. code-block:: python

    def func(x):
        if x <= 0:
            raise ValueError("x needs to be larger than zero")


    pytest.raises(ValueError, func, x=-1)

这种形式是最初的 :func:`pytest.raises` API，在 ``with`` 语句被添加到 Python 语言之前开发。如今，这种形式很少使用，上下文管理器形式（使用 ``with``）被认为更具可读性。

xfail 标记和 pytest.raises
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

也可以为 :ref:`pytest.mark.xfail <pytest.mark.xfail ref>` 指定 ``raises`` 参数，它检查测试是否以更具体的方式失败，而不仅仅是抛出任何异常：

.. code-block:: python

    def f():
        raise IndexError()


    @pytest.mark.xfail(raises=IndexError)
    def test_f():
        f()


只有当测试通过抛出 ``IndexError`` 或其子类而失败时，这才会 "xfail"。

* 对于记录未修复的错误（其中测试描述了"应该"发生什么）或依赖项中的错误，使用带 ``raises`` 参数的 :ref:`pytest.mark.xfail <pytest.mark.xfail ref>` 可能更好。

* 对于测试你自己代码故意抛出的异常的情况（这是大多数情况），使用 :func:`pytest.raises` 可能更好。

你也可以使用 :class:`pytest.RaisesGroup`：

.. code-block:: python

    def f():
        raise ExceptionGroup("", [IndexError()])


    @pytest.mark.xfail(raises=RaisesGroup(IndexError))
    def test_f():
        f()


.. _`assertwarns`:

关于预期警告的断言
-----------------------------------------



你可以使用 :ref:`pytest.warns <warns>` 检查代码是否抛出特定警告。


.. _newreport:

利用上下文相关的比较
-------------------------------------------------



``pytest`` 在遇到比较时具有丰富的上下文相关信息支持。例如：

.. code-block:: python

    # test_assert2.py 的内容
    def test_set_comparison():
        set1 = set("1308")
        set2 = set("8035")
        assert set1 == set2

如果你运行此模块：

.. code-block:: pytest

    $ pytest test_assert2.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 1 item

    test_assert2.py F                                                    [100%]

    ================================= FAILURES =================================
    ___________________________ test_set_comparison ____________________________

        def test_set_comparison():
            set1 = set("1308")
            set2 = set("8035")
    >       assert set1 == set2
    E       AssertionError: assert {'0', '1', '3', '8'} == {'0', '3', '5', '8'}
    E
    E         Extra items in the left set:
    E         '1'
    E         Extra items in the right set:
    E         '5'
    E         Use -v to get more diff

    test_assert2.py:4: AssertionError
    ========================= short test summary info ==========================
    FAILED test_assert2.py::test_set_comparison - AssertionError: assert {'0'...
    ============================ 1 failed in 0.12s =============================

对多种情况进行了特殊比较：

* 比较长字符串：显示上下文差异
* 比较长序列：显示首次失败的索引
* 比较字典：显示不同的条目

在字符串上下文差异中，以 ``-`` 为前缀的行来自 ``assert left == right`` 的左侧，而以 ``+`` 为前缀的行来自右侧。

有关更多示例，请参见 :ref:`reporting demo <tbreportdemo>`。

为失败的断言定义自己的解释
---------------------------------------------------

可以通过实现 ``pytest_assertrepr_compare`` 钩子来添加你自己的详细解释。

.. autofunction:: _pytest.hookspec.pytest_assertrepr_compare
   :noindex:

例如，考虑在 :ref:`conftest.py <conftest.py>` 文件中添加以下钩子，为 ``Foo`` 对象提供替代解释：

.. code-block:: python

   # conftest.py 的内容
   from test_foocompare import Foo


   def pytest_assertrepr_compare(op, left, right):
       if isinstance(left, Foo) and isinstance(right, Foo) and op == "==":
           return [
               "Comparing Foo instances:",
               f"   vals: {left.val} != {right.val}",
           ]

现在，给定此测试模块：

.. code-block:: python

   # test_foocompare.py 的内容
   class Foo:
       def __init__(self, val):
           self.val = val

       def __eq__(self, other):
           return self.val == other.val


   def test_compare():
       f1 = Foo(1)
       f2 = Foo(2)
       assert f1 == f2

你可以运行测试模块并获得在 conftest 文件中定义的自定义输出：

.. code-block:: pytest

   $ pytest -q test_foocompare.py
   F                                                                    [100%]
   ================================= FAILURES =================================
   _______________________________ test_compare _______________________________

       def test_compare():
           f1 = Foo(1)
           f2 = Foo(2)
   >       assert f1 == f2
   E       assert Comparing Foo instances:
   E            vals: 1 != 2

   test_foocompare.py:12: AssertionError
   ========================= short test summary info ==========================
   FAILED test_foocompare.py::test_compare - assert Comparing Foo instances:
   1 failed in 0.12s

.. _`return-not-none`:

在测试函数中返回非 None 值
------------------------------------------

当测试函数返回 ``None`` 以外的值时，会发出 :class:`pytest.PytestReturnNotNoneWarning`。

这有助于防止初学者犯的一个常见错误，他们认为返回 ``bool``（例如 ``True`` 或 ``False``）将决定测试是通过还是失败。

示例：

.. code-block:: python

    @pytest.mark.parametrize(
        ["a", "b", "result"],
        [
            [1, 2, 5],
            [2, 3, 8],
            [5, 3, 18],
        ],
    )
    def test_foo(a, b, result):
        return foo(a, b) == result  # 错误用法，不要这样做。

由于 pytest 忽略返回值，测试永远不会根据返回值失败，这可能会令人惊讶。

正确的修复方法是将 ``return`` 语句替换为 ``assert``：

.. code-block:: python

    @pytest.mark.parametrize(
        ["a", "b", "result"],
        [
            [1, 2, 5],
            [2, 3, 8],
            [5, 3, 18],
        ],
    )
    def test_foo(a, b, result):
        assert foo(a, b) == result




.. _assert-details:
.. _`assert introspection`:

断言内省详细信息
-------------------------------


通过在运行前重写断言语句来实现关于失败断言的详细信息报告。重写的断言语句将内省信息放入断言失败消息中。``pytest`` 只重写由其测试收集过程直接发现的测试模块，因此支持模块中的断言（这些模块本身不是测试模块）将不会被重写。

你可以通过在导入模块之前调用 :ref:`register_assert_rewrite <assertion-rewriting>` 来手动为导入的模块启用断言重写（这样做的好地方是在你的根 ``conftest.py`` 中）。

有关更多信息，Benjamin Peterson 撰写了 `Behind the scenes of pytest's new assertion rewriting <http://pybites.blogspot.com/2011/07/behind-scenes-of-pytests-new-assertion.html>`_。

断言重写将文件缓存到磁盘
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``pytest`` 会将重写的模块写回磁盘进行缓存。你可以通过在 ``conftest.py`` 文件顶部添加以下内容来禁用此行为（例如，为了避免在频繁移动文件的项目中留下过时的 ``.pyc`` 文件）：

.. code-block:: python

   import sys

   sys.dont_write_bytecode = True

请注意，你仍然可以获得断言内省的好处，唯一的变化是 ``.pyc`` 文件不会缓存到磁盘上。

此外，如果无法写入新的 ``.pyc`` 文件（例如在只读文件系统或 zipfile 中），重写将静默跳过缓存。


禁用断言重写
~~~~~~~~~~~~~~~~~~~~~~~~~~

``pytest`` 通过使用导入钩子写入新的 ``pyc`` 文件来在导入时重写测试模块。大多数情况下这是透明工作的。但是，如果你自己处理导入机制，导入钩子可能会干扰。

如果是这种情况，你有两个选择：

* 通过向模块的文档字符串添加字符串 ``PYTEST_DONT_REWRITE`` 来为特定模块禁用重写。

* 使用 :option:`--assert=plain` 为所有模块禁用重写。
