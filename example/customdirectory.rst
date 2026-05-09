.. _`custom directory collectors`:

使用自定义目录收集器
====================================================

默认情况下，pytest 使用 :class:`pytest.Package` 收集有 ``__init__.py`` 文件的目录，使用 :class:`pytest.Dir` 收集其他目录。
如果你想自定义如何收集目录，你可以编写自己的 :class:`pytest.Directory` 收集器，并使用 :hook:`pytest_collect_directory` 将其挂接到系统中。

.. _`directory manifest plugin`:

目录清单文件的基本示例
--------------------------------------------------------------

假设你想自定义如何在每个目录的基础上进行收集。
这里有一个示例 ``conftest.py`` 插件，允许目录包含一个 ``manifest.json`` 文件，它定义了应该如何为该目录进行收集。
在这个示例中，只支持简单的文件列表，不过你可以想象添加其他键，如排除项和通配符。

.. include:: customdirectory/conftest.py
    :literal:

你可以创建一个 ``manifest.json`` 文件和一些测试文件：

.. include:: customdirectory/tests/manifest.json
    :literal:

.. include:: customdirectory/tests/test_first.py
    :literal:

.. include:: customdirectory/tests/test_second.py
    :literal:

.. include:: customdirectory/tests/test_third.py
    :literal:

你现在可以执行测试规范：

.. code-block:: pytest

    customdirectory $ pytest
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project/customdirectory
    configfile: pytest.ini
    collected 2 items

    tests/test_first.py .                                                [ 50%]
    tests/test_second.py .                                               [100%]

    ============================ 2 passed in 0.12s ============================

.. regendoc:wipe

注意 ``test_three.py`` 是如何没有被执行的，因为它没有列在清单中。

你可以验证你的自定义收集器是否出现在收集树中：

.. code-block:: pytest

    customdirectory $ pytest --collect-only
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project/customdirectory
    configfile: pytest.ini
    collected 2 items

    <Dir customdirectory>
      <ManifestDirectory tests>
        <Module test_first.py>
          <Function test_1>
        <Module test_second.py>
          <Function test_2>

    ======================== 2 tests collected in 0.12s ========================
