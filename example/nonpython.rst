
.. _`non-python tests`:

处理非 Python 测试
====================================================

.. _`yaml plugin`:

在 Yaml 文件中指定测试的基本示例
--------------------------------------------------------------

.. _`pytest-yamlwsgi`: https://pypi.org/project/pytest-yamlwsgi/

这里有一个示例 ``conftest.py``（从 Ali Afshar 的特殊用途 `pytest-yamlwsgi`_ 插件中提取）。这个 ``conftest.py`` 将收集 ``test*.yaml`` 文件并将 yaml 格式的内容作为自定义测试执行：

.. include:: nonpython/conftest.py
    :literal:

你可以创建一个简单的示例文件：

.. include:: nonpython/test_simple.yaml
    :literal:

如果你安装了 :pypi:`PyYAML` 或兼容的 YAML 解析器，你现在可以执行测试规范：

.. code-block:: pytest

    nonpython $ pytest test_simple.yaml
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project/nonpython
    collected 2 items

    test_simple.yaml F.                                                  [100%]

    ================================= FAILURES =================================
    ______________________________ usecase: hello ______________________________
    usecase execution failed
       spec failed: 'some': 'other'
       no further details known at this point.
    ========================= short test summary info ==========================
    FAILED test_simple.yaml::hello - usecase execution failed
    ======================= 1 failed, 1 passed in 0.12s ========================

.. regendoc:wipe

你会看到一个点表示通过的 ``sub1: sub1`` 检查和一个失败。
显然，在上面的 ``conftest.py`` 中，你会想要实现对 yaml 值更有趣的解释。你可以通过这种方式轻松编写自己的领域特定测试语言。

.. note::

    ``repr_failure(excinfo)`` 被调用用于表示测试失败。
    如果你创建自定义收集节点，你可以返回你选择的错误
    表示字符串。它将被报告为（红色的）字符串。

``reportinfo()`` 用于表示测试位置，也在
``verbose`` 模式下报告时查阅。它应该返回一个元组
``(path, lineno, description)``，其中：

* ``path`` 是报告中显示的路径（通常是 ``self.path`` 或 ``self.fspath``）。
* ``lineno`` 是零基行号，或者当没有特定行适用时为 ``0``。
* ``description`` 是为收集项显示的简短标签：

.. code-block:: pytest

    nonpython $ pytest -v
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y -- $PYTHON_PREFIX/bin/python
    cachedir: .pytest_cache
    rootdir: /home/sweet/project/nonpython
    collecting ... collected 2 items

    test_simple.yaml::hello FAILED                                       [ 50%]
    test_simple.yaml::ok PASSED                                          [100%]

    ================================= FAILURES =================================
    ______________________________ usecase: hello ______________________________
    usecase execution failed
       spec failed: 'some': 'other'
       no further details known at this point.
    ========================= short test summary info ==========================
    FAILED test_simple.yaml::hello - usecase execution failed
    ======================= 1 failed, 1 passed in 0.12s ========================

.. regendoc:wipe

在开发自定义测试收集和执行时，只查看收集树也很有趣：

.. code-block:: pytest

    nonpython $ pytest --collect-only
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project/nonpython
    collected 2 items

    <Package nonpython>
      <YamlFile test_simple.yaml>
        <YamlItem hello>
        <YamlItem ok>

    ======================== 2 tests collected in 0.12s ========================
