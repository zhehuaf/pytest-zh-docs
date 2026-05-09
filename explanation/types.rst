.. _types:

pytest 中的类型
================

.. note::
    本页面假设读者熟悉 Python 的类型系统及其优势。

    有关更多信息，请参阅 `Python 的类型文档 <https://docs.python.org/3/library/typing.html>`_。

为什么要对测试进行类型检查？
----------------------------

对测试进行类型检查提供了显著的优势：

- **可读性：** 清晰定义预期输入和输出，提高可读性，特别是在复杂或参数化测试中。

- **重构：** 这是类型化测试的主要好处，因为它将极大地帮助重构，让类型检查器指出生产和测试中的必要更改，而无需运行完整的测试套件。

对于生产代码，类型检查还有助于捕获一些可能完全无法被测试捕获的错误（无论覆盖率如何），例如：

.. code-block:: python

    def get_caption(target: int, items: list[tuple[int, str]]) -> str:
        for value, caption in items:
            if value == target:
                return caption


类型检查器会正确地报错说该函数可能返回 `None`，然而即使具有完整覆盖率的测试套件也可能遗漏该情况：

.. code-block:: python

    def test_get_caption() -> None:
        assert get_caption(10, [(1, "foo"), (10, "bar")]) == "bar"


请注意上面的代码有 100% 覆盖率，但错误没有被捕获（当然示例是"显而易见"的，但用于说明这一点）。


在测试套件中使用类型
---------------------------

要在 pytest 中为 fixtures 添加类型，只需向 fixture 函数添加普通类型——由于 `fixture` 装饰器的原因，没有什么特殊需要做的。

.. code-block:: python

    import pytest


    @pytest.fixture
    def sample_fixture() -> int:
        return 38

同样，传递给测试函数的 fixtures 需要用 fixture 的返回类型进行注解：

.. code-block:: python

    def test_sample_fixture(sample_fixture: int) -> None:
        assert sample_fixture == 38

从类型检查器的角度来看，`sample_fixture` 实际上是由 pytest 管理的 fixture 并不重要，重要的是 `sample_fixture` 是类型为 `int` 的参数。


同样的逻辑适用于 :ref:`@pytest.mark.parametrize <@pytest.mark.parametrize>`：

.. code-block:: python


    @pytest.mark.parametrize("input_value, expected_output", [(1, 2), (5, 6), (10, 11)])
    def test_increment(input_value: int, expected_output: int) -> None:
        assert input_value + 1 == expected_output


同样的逻辑适用于接收其他 fixtures 的 fixture 函数的类型注解：

.. code-block:: python

    @pytest.fixture
    def mock_env_user(monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("USER", "TestingUser")


结论
----------

将类型检查纳入 pytest 测试增强了**清晰度**，改善了**调试**和**维护**，并确保**类型安全**。
这些实践产生了一个**健壮**、**可读**\且**易于维护**\的测试套件，更好地装备以应对未来的更改，并将错误风险降至最低。
