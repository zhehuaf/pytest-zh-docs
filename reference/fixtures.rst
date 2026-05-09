.. _reference-fixtures:
.. _fixture:
.. _fixtures:
.. _`@pytest.fixture`:
.. _`pytest.fixture`:


Fixtures 参考
========================================================

.. seealso:: :ref:`about-fixtures`
.. seealso:: :ref:`how-to-fixtures`

.. _`Dependency injection`: https://en.wikipedia.org/wiki/Dependency_injection


内置 fixtures
-----------------

:ref:`Fixtures <fixtures-api>` 使用 :ref:`@pytest.fixture
<pytest.fixture-api>` 装饰器定义。Pytest 有几个有用的内置 fixtures：

   :fixture:`capfd`
        以文本形式捕获输出到文件描述符 ``1`` 和 ``2``。

   :fixture:`capfdbinary`
        以字节形式捕获输出到文件描述符 ``1`` 和 ``2``。

   :fixture:`caplog`
        控制日志记录并访问日志条目。

   :fixture:`capsys`
        以文本形式捕获输出到 ``sys.stdout`` 和 ``sys.stderr``。

   :fixture:`capteesys`
        以与 :fixture:`capsys` 相同的方式捕获，但也根据 :option:`--capture` 传递文本。

   :fixture:`capsysbinary`
        以字节形式捕获输出到 ``sys.stdout`` 和 ``sys.stderr``。

   :fixture:`cache`
        在 pytest 运行之间存储和检索值。

   :fixture:`doctest_namespace`
        提供一个注入到 doctests 命名空间中的字典。

   :fixture:`monkeypatch`
       临时修改类、函数、字典、
       ``os.environ`` 和其他对象。

   :fixture:`pytestconfig`
        访问配置值、pluginmanager 和插件 hooks。

   :fixture:`subtests`
        启用声明测试函数内的 subtests。

   :fixture:`record_property`
       向测试添加额外属性。

   :fixture:`record_testsuite_property`
       向测试套件添加额外属性。

   :fixture:`recwarn`
        记录测试函数发出的警告。

   :fixture:`request`
       提供有关正在执行的测试函数的信息。

   :fixture:`testdir`
        提供一个临时测试目录以帮助运行和
        测试 pytest 插件。

   :fixture:`tmp_path`
       提供一个 :class:`pathlib.Path` 对象指向一个临时目录
       该目录对每个测试函数是唯一的。

   :fixture:`tmp_path_factory`
        创建 session-scoped 临时目录并返回
        :class:`pathlib.Path` 对象。

   :fixture:`tmpdir`
        提供一个 `py.path.local <https://py.readthedocs.io/en/latest/path.html>`_ 对象指向一个临时
        目录，该目录对每个测试函数是唯一的；
        已被 :fixture:`tmp_path` 取代。

   :fixture:`tmpdir_factory`
        创建 session-scoped 临时目录并返回
        ``py.path.local`` 对象；
        已被 :fixture:`tmp_path_factory` 取代。


.. _`conftest.py`:
.. _`conftest`:

Fixture 可用性
---------------------

Fixture 可用性是从测试的角度确定的。一个 fixture
只有在其定义的范围内，测试才能请求它。如果一个 fixture 在类内部定义，它只能被该类内部的测试请求。但如果一个 fixture 在模块的全局范围内定义，那么该模块中的每个测试，即使定义在类内部，也可以请求它。

同样，一个测试也只能被与其所定义的 autouse fixture 相同范围内的 autouse fixture 影响（参见
:ref:`autouse order`）。

一个 fixture 也可以请求任何其他 fixture，无论它在哪里定义，只要请求它们的测试能看到所有涉及的 fixtures。

例如，这里有一个测试文件，其中有一个 fixture（``outer``）请求一个来自它未定义范围的 fixture（``inner``）：

.. literalinclude:: /example/fixtures/test_fixtures_request_different_scope.py

从测试的角度来看，它们在查找它们所依赖的每个 fixture 时没有问题：

.. image:: /example/fixtures/test_fixtures_request_different_scope.*
    :align: center

因此当它们运行时，``outer`` 查找 ``inner`` 不会有问题，因为
pytest 是从测试的角度搜索的。

.. note::
    fixture 定义的范围与其实例化顺序无关：顺序由 :ref:`此处 <fixture order>` 描述的逻辑决定。

``conftest.py``：在多个文件之间共享 fixtures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``conftest.py`` 文件用作向整个目录提供 fixtures 的一种方式。在 ``conftest.py`` 中定义的 fixtures 可以被该包中的任何测试使用，无需导入它们（pytest 会自动发现它们）。

你可以有多个包含测试的嵌套目录/包，每个目录可以有自己的 ``conftest.py``，有自己的 fixtures，添加到父目录中 ``conftest.py`` 文件提供的 fixtures 之上。

例如，给定如下测试文件结构：

::

    tests/
        __init__.py

        conftest.py
            # tests/conftest.py 的内容
            import pytest

            @pytest.fixture
            def order():
                return []

            @pytest.fixture
            def top(order, innermost):
                order.append("top")

        test_top.py
            # tests/test_top.py 的内容
            import pytest

            @pytest.fixture
            def innermost(order):
                order.append("innermost top")

            def test_order(order, top):
                assert order == ["innermost top", "top"]

        subpackage/
            __init__.py

            conftest.py
                # tests/subpackage/conftest.py 的内容
                import pytest

                @pytest.fixture
                def mid(order):
                    order.append("mid subpackage")

            test_subpackage.py
                # tests/subpackage/test_subpackage.py 的内容
                import pytest

                @pytest.fixture
                def innermost(order, mid):
                    order.append("innermost subpackage")

                def test_order(order, top):
                    assert order == ["mid subpackage", "innermost subpackage", "top"]

范围的边界可以像这样可视化：

.. image:: /example/fixtures/fixture_availability.*
    :align: center

目录成为它们自己的一种范围，其中在该目录的 ``conftest.py`` 文件中定义的 fixtures 可用于整个范围。

测试允许向上搜索（走出一个圆圈）以查找 fixtures，但绝不能向下（走进一个圆圈）以继续搜索。所以
``tests/subpackage/test_subpackage.py::test_order`` 能够找到在 ``tests/subpackage/test_subpackage.py`` 中定义的 ``innermost`` fixture，但定义在 ``tests/test_top.py`` 中的那个对它不可用，因为它需要向下走一级（走进一个圆圈）才能找到它。

测试找到的第一个 fixture 将是被使用的那个，所以
:ref:`fixtures 可以被覆盖 <override fixtures>` 如果你需要更改或扩展特定范围内的某个功能。

你也可以使用 ``conftest.py`` 文件来实现
:ref:`每个目录的本地插件 <conftest.py plugins>`。

来自第三方插件的 fixtures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

fixtures 不必定义在这种结构中才能用于测试，
尽管它们也可以由已安装的第三方插件提供，这就是许多 pytest 插件的工作方式。只要安装了这些插件，
它们提供的 fixtures 就可以从测试套件的任何地方请求。

因为它们是从你的测试套件结构外部提供的，
第三方插件并没有真正像 `conftest.py` 文件和你测试套件中的目录那样提供一个范围。因此，pytest 将像以前那样通过范围向外搜索 fixtures，只有在搜索完 ``tests/`` 内部的范围后，才会到达在插件中定义的 fixtures。

例如，给定以下文件结构：

::

    tests/
        __init__.py

        conftest.py
            # tests/conftest.py 的内容
            import pytest

            @pytest.fixture
            def order():
                return []

        subpackage/
            __init__.py

            conftest.py
                # tests/subpackage/conftest.py 的内容
                import pytest

                @pytest.fixture(autouse=True)
                def mid(order, b_fix):
                    order.append("mid subpackage")

            test_subpackage.py
                # tests/subpackage/test_subpackage.py 的内容
                import pytest

                @pytest.fixture
                def inner(order, mid, a_fix):
                    order.append("inner subpackage")

                def test_order(order, inner):
                    assert order == ["b_fix", "mid subpackage", "a_fix", "inner subpackage"]

如果 ``plugin_a`` 已安装并提供 fixture ``a_fix``，且
``plugin_b`` 已安装并提供 fixture ``b_fix``，那么这就是测试对 fixtures 搜索的样子：

.. image:: /example/fixtures/fixture_availability_plugins.svg
    :align: center

pytest 只会在搜索完 ``tests/`` 内部的范围后，才在插件中搜索 ``a_fix`` 和 ``b_fix``。

.. note::

    如果你用测试的名称（或它所在的范围）调用
    ``pytest``，并提供
    :option:`--fixtures` 标志，例如 ``pytest --fixtures test_something.py``，pytest 可以告诉你给定测试有哪些 fixtures 可用
    （名称以 ``_`` 开头的 fixtures 只有在你也提供 :option:`-v` 标志时才会显示）。


.. _`fixture order`:

Fixture 实例化顺序
---------------------------

当 pytest 想要执行一个测试时，一旦它知道哪些 fixtures 将被执行，它就必须确定它们将按什么顺序执行。为此，它考虑 3 个因素：

1. 范围
2. 依赖关系
3. autouse

fixtures 或测试的名称、它们在哪里定义、它们定义的顺序以及 fixtures 被请求的顺序，除了巧合之外，对执行顺序没有影响。虽然 pytest 会尽量确保像这样的巧合在每次运行时保持一致，但这不应被依赖。如果你想控制顺序，最安全的是依靠这 3 件事，并确保依赖关系清晰建立。

高范围 fixtures 先执行
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

在 function 对 fixtures 的请求中，那些高范围的（如
``session``）在低范围 fixtures（如 ``function`` 或
``class``）之前执行。

这里有一个例子：

.. literalinclude:: /example/fixtures/test_fixtures_order_scope.py

测试将通过，因为较大范围的 fixtures 先执行。

顺序分解如下：

.. image:: /example/fixtures/test_fixtures_order_scope.*
    :align: center

相同顺序的 fixtures 基于依赖关系执行
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

当一个 fixture 请求另一个 fixture 时，另一个 fixture 先执行。
所以如果 fixture ``a`` 请求 fixture ``b``，fixture ``b`` 将先执行，
因为 ``a`` 依赖于 ``b``，没有它就无法运行。即使 ``a``
不需要 ``b`` 的结果，如果它需要确保它在 ``b`` 之后执行，它仍然可以请求 ``b``。

例如：

.. literalinclude:: /example/fixtures/test_fixtures_order_dependencies.py

如果我们映射出什么依赖于什么，我们会得到这样的东西：

.. image:: /example/fixtures/test_fixtures_order_dependencies.*
    :align: center

每个 fixture 提供的规则（关于每个 fixture 必须跟在哪些 fixture 之后）足够全面，可以将其扁平化为：

.. image:: /example/fixtures/test_fixtures_order_dependencies_flat.*
    :align: center

必须通过这些请求提供足够的信息，以便 pytest
能够确定一个清晰的线性依赖链，并因此
确定给定测试的操作顺序。如果有任何歧义，且操作顺序可以以多种方式解释，你应该假设 pytest
可能会随时选择其中任何一种解释。

例如，如果 ``d`` 没有请求 ``c``，即图形看起来像这样：

.. image:: /example/fixtures/test_fixtures_order_dependencies_unclear.*
    :align: center

因为除了 ``g`` 之外没有请求 ``c``，而 ``g`` 也请求 ``f``，
现在不清楚 ``c`` 应该放在 ``f``、``e`` 或 ``d`` 之前还是之后。为 ``c`` 设置的唯一规则是它必须在 ``b`` 之后执行且在
``g`` 之前。

pytest 不知道在这种情况下 ``c`` 应该放在哪里，所以应该假设它可能放在 ``g`` 和 ``b`` 之间的任何地方。

这不一定不好，但这是需要注意的事情。如果它们执行的顺序可能影响测试所针对的行为，或可能
以其他方式影响测试结果，那么应该以允许 pytest 线性化/"扁平化"该顺序的方式显式定义顺序。

.. _`autouse order`:

Autouse fixtures 在其范围内先执行
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Autouse fixtures 被假设应用于每个可以引用它们的测试，所以它们在该范围内的其他 fixtures 之前执行。被 autouse fixtures 请求的 fixtures 对于 autouse fixture 应用到的测试，实际上本身也成为 autouse fixtures。

所以如果 fixture ``a`` 是 autouse 的而 fixture ``b`` 不是，但 fixture ``a``
请求 fixture ``b``，那么 fixture ``b`` 实际上也将是 autouse fixture，但仅适用于 ``a`` 应用到的测试。

在上面的例子中，如果 ``d`` 没有请求 ``c``，图形会变得不清楚。但如果 ``c`` 是 autouse 的，那么 ``b`` 和 ``a`` 实际上也将是 autouse 的，因为 ``c`` 依赖于它们。因此，它们都会被移到该范围内非 autouse fixtures 之上。

所以如果测试文件看起来像这样：

.. literalinclude:: /example/fixtures/test_fixtures_order_autouse.py

图形看起来会像这样：

.. image:: /example/fixtures/test_fixtures_order_autouse.*
    :align: center

因为现在 ``c`` 可以放在图形中 ``d`` 的上方，pytest 可以再次将图形线性化为：

.. image:: /example/fixtures/test_fixtures_order_autouse_flat.*
    :align: center

在这个例子中，``c`` 使 ``b`` 和 ``a`` 实际上也成为 autouse fixtures。

不过要小心使用 autouse，因为 autouse fixture 将为每个可以到达它的测试自动执行，即使它们没有请求它。例如，考虑这个文件：

.. literalinclude:: /example/fixtures/test_fixtures_order_autouse_multiple_scopes.py

即使 ``TestClassWithoutC1Request`` 中没有任何东西请求 ``c1``，它仍然对里面的测试执行：

.. image:: /example/fixtures/test_fixtures_order_autouse_multiple_scopes.*
    :align: center

但仅仅因为一个 autouse fixture 请求了一个非 autouse fixture，并不意味着非 autouse fixture 对于它可能应用到的所有上下文都成为 autouse fixture。它只对真正的 autouse fixture（请求非 autouse fixture 的那个）可以应用到的上下文有效成为 autouse fixture。

例如，看看这个测试文件：

.. literalinclude:: /example/fixtures/test_fixtures_order_autouse_temp_effects.py

它会分解为这样的东西：

.. image:: /example/fixtures/test_fixtures_order_autouse_temp_effects.*
    :align: center

对于 ``TestClassWithAutouse`` 内部的 ``test_req`` 和 ``test_no_req``，``c3``
有效地使 ``c2`` 成为 autouse fixture，这就是为什么 ``c2`` 和 ``c3`` 都为两个测试执行，尽管没有被请求，以及为什么 ``c2`` 和 ``c3`` 在 ``test_req`` 的 ``c1`` 之前执行。

如果这使 ``c2`` 成为*实际*的 autouse fixture，那么 ``c2`` 也会为 ``TestClassWithoutAutouse`` 内部的测试执行，因为它们可以引用 ``c2`` 如果它们想的话。但它没有，因为从 ``TestClassWithoutAutouse`` 测试的角度来看，``c2`` 不是 autouse fixture，因为它们看不到 ``c3``。


.. note::

    如果你用测试的名称（或它所在的范围）调用 ``pytest``，并提供 :option:`--setup-plan` 标志，例如
    ``pytest --setup-plan test_something.py``，pytest 可以告诉你给定测试的 fixtures 将按什么顺序执行
    （名称以 ``_`` 开头的 fixtures 只有在你也提供 :option:`-v` 标志时才会显示）。
