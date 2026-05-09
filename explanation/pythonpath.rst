.. _pythonpath:

pytest 导入机制和 ``sys.path``/``PYTHONPATH``
========================================================

.. _`import-modes`:

导入模式
------------

pytest 作为测试框架需要导入测试模块和 ``conftest.py`` 文件来执行。

在 Python 中导入文件是一个非平凡的过程，因此导入过程的各个方面可以通过 :option:`--import-mode` 命令行标志来控制，它可以采用以下值：

.. _`import-mode-prepend`:

* ``prepend``\（默认）：包含每个模块的目录路径将被插入到 :py:data:`sys.path`\的\*开头*\（如果尚未存在），然后使用 :func:`importlib.import_module <importlib.import_module>` 函数导入。

  强烈建议通过添加 ``__init__.py`` 文件将测试模块安排为包，添加到包含测试的目录中。这将使测试成为适当的 Python 包的一部分，允许 pytest 解析其完整名称（例如，对于 ``tests.core`` 包内的 ``test_core.py``，名称为 ``tests.core.test_core``）。

  如果测试目录树没有安排为包，则与其他测试文件相比，每个测试文件需要具有唯一的名称，否则如果 pytest 发现两个具有相同名称的测试，它将引发错误。

  这是经典机制，可以追溯到 Python 2 仍在使用的时代。

.. _`import-mode-append`:

* ``append``：包含每个模块的目录被附加到 :py:data:`sys.path` 的末尾（如果尚未存在），并使用 :func:`importlib.import_module <importlib.import_module>` 导入。

  这更好地允许用户针对已安装的包版本运行测试模块，即使被测包具有相同的导入根。例如：

  ::

        testing/__init__.py
        testing/test_pkg_under_test.py
        pkg_under_test/

  当使用 :option:`--import-mode=append` 时，测试将针对 ``pkg_under_test`` 的已安装版本运行，而使用 ``prepend`` 时，它们会选取本地版本。这种混乱就是我们提倡使用 :ref:`src-layouts <src-layout>` 的原因。

  与 ``prepend`` 相同，当测试目录树没有安排为包时，需要测试模块名称唯一，因为导入后模块将被放入 :py:data:`sys.modules` 中。

.. _`import-mode-importlib`:

* ``importlib``：此模式使用 :mod:`importlib` 提供的更精细的控制机制来导入测试模块，而不更改 :py:data:`sys.path`。

  此模式的优点：

  * pytest 根本不会更改 :py:data:`sys.path`。
  * 测试模块名称不需要唯一 -- pytest 将根据 ``rootdir`` 自动生成唯一的名称。

  缺点：

  * 测试模块无法相互导入。
  * 测试目录中的测试实用模块（例如包含测试相关函数/类的 ``tests.helpers`` 模块）不可导入。在这种情况下，建议将测试实用模块与应用程序/库代码放在一起，例如 ``app.testing.helpers``。

    重要提示：所谓"测试实用模块"，是指被其他测试直接导入的函数/类；这不包括 fixtures，它们应放在 ``conftest.py`` 文件中，与测试模块一起，并由 pytest 自动发现。

  它的工作原理如下：

  1. 给定某个模块路径，例如 ``tests/core/test_models.py``，派生一个规范名称如 ``tests.core.test_models`` 并尝试导入它。

     对于非测试模块，如果它们可以通过 :py:data:`sys.path` 访问，这将起作用。因此，例如，``.env/lib/site-packages/app/core.py`` 将可作为 ``app.core`` 导入。这发生在插件导入非测试模块时（例如 doctesting）。

     如果此步骤成功，则返回该模块。

     对于测试模块，除非它们可以从 :py:data:`sys.path` 到达，否则此步骤将失败。

  2. 如果上一步失败，我们直接使用 ``importlib`` 工具导入模块，这允许我们在不更改 :py:data:`sys.path` 的情况下导入它。

     由于 Python 要求模块在 :py:data:`sys.modules` 中也可用，pytest 根据其相对于 ``rootdir`` 的位置派生唯一的名称，并将模块添加到 :py:data:`sys.modules` 中。

     例如，``tests/core/test_models.py`` 最终将被导入为模块 ``tests.core.test_models``。

  .. versionadded:: 6.0

.. note::

    最初我们打算在将来的版本中让 ``importlib`` 成为默认设置，但现在已经很清楚它有自己的一套缺点，因此在可预见的将来，默认值将保持为 ``prepend``。

.. note::

    默认情况下，pytest 不会尝试自动解析命名空间包，但可以通过 :confval:`consider_namespace_packages` 配置变量更改。

.. seealso::

    :confval:`pythonpath` 配置变量。

    :confval:`consider_namespace_packages` 配置变量。

    :ref:`test layout`。


``prepend`` 和 ``append`` 导入模式场景
-------------------------------------------------

以下是使用 ``prepend`` 或 ``append`` 导入模式时，pytest 需要更改 :py:data:`sys.path` 以导入测试模块或 ``conftest.py`` 文件的场景列表，以及用户因此可能遇到的问题。

包内的测试模块 / ``conftest.py`` 文件
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

考虑此文件和目录布局::

    root/
    |- foo/
       |- __init__.py
       |- conftest.py
       |- bar/
          |- __init__.py
          |- tests/
             |- __init__.py
             |- test_foo.py


执行时：

.. code-block:: bash

    pytest root/

pytest 将找到 ``foo/bar/tests/test_foo.py`` 并意识到它是包的一部分，因为同一目录中有 ``__init__.py`` 文件。然后它将向上搜索，直到找到仍然包含 ``__init__.py`` 文件的最后一个目录，以找到包*根*（在本例中为 ``foo/``）。为了加载模块，它将 ``root/`` 插入到 :py:data:`sys.path` 的前面（如果尚未存在），以便将 ``test_foo.py`` 作为*模块* ``foo.bar.tests.test_foo`` 加载。

同样的逻辑适用于 ``conftest.py`` 文件：它将被导入为 ``foo.conftest`` 模块。

当测试位于包中时，保留完整的包名称很重要，以避免问题并允许测试模块具有重复的名称。这在 :ref:`test discovery` 中也有详细讨论。

独立测试模块 / ``conftest.py`` 文件
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

考虑此文件和目录布局::

    root/
    |- foo/
       |- conftest.py
       |- bar/
          |- tests/
             |- test_foo.py


执行时：

.. code-block:: bash

    pytest root/

pytest 将找到 ``foo/bar/tests/test_foo.py`` 并意识到它不是包的一部分，因为同一目录中没有 ``__init__.py`` 文件。然后它将 ``root/foo/bar/tests`` 添加到 :py:data:`sys.path`，以便将 ``test_foo.py`` 作为*模块* ``test_foo`` 导入。对 ``conftest.py`` 文件也执行同样的操作，通过将 ``root/foo`` 添加到 :py:data:`sys.path` 将其导入为 ``conftest``。

因此，这种布局不能具有相同名称的测试模块，因为它们都将被导入到全局导入命名空间中。

这在 :ref:`test discovery` 中也有详细讨论。

.. _`pytest vs python -m pytest`:

调用 ``pytest`` 与 ``python -m pytest``
-----------------------------------------------

使用 ``pytest [...]`` 而不是 ``python -m pytest [...]`` 运行 pytest 产生几乎相同的行为，除了后者会将当前目录添加到 :py:data:`sys.path`，这是标准的 ``python`` 行为。

另请参见 :ref:`invoke-python`。
