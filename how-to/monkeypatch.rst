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
------------------------

考虑一个你正在使用用户目录的场景。在测试的上下文中，你不希望你的测试依赖于运行用户。``monkeypatch`` 可用于修补依赖于用户的函数以始终返回特定值。

在此示例中，:py:meth:`monkeypatch.setattr <MonkeyPatch.setattr>` 用于修补 ``Path.home``，以便在运行测试时始终使用已知的测试路径 ``Path("/abc")``。这消除了测试对运行用户的任何依赖。
:py:meth:`monkeypatch.setattr <MonkeyPatch.setattr>` 必须在将使用修补函数的函数被调用之前调用。
测试函数完成后，``Path.home`` 修改将被撤消。

