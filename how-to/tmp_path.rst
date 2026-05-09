
.. _`tmp_path handling`:
.. _tmp_path:

如何在测试中使用临时目录和文件
===================================================

``tmp_path`` fixture
------------------------

你可以使用 ``tmp_path`` fixture，它将提供一个专属于每个测试函数的临时目录。

``tmp_path`` 是一个 :class:`pathlib.Path` 对象。以下是一个示例测试用法：

.. code-block:: python

    # test_tmp_path.py 的内容
    CONTENT = "content"


    def test_create_file(tmp_path):
        d = tmp_path / "sub"
        d.mkdir()
        p = d / "hello.txt"
        p.write_text(CONTENT, encoding="utf-8")
        assert p.read_text(encoding="utf-8") == CONTENT
        assert len(list(tmp_path.iterdir())) == 1
        assert 0

运行此测试会产生通过的测试，除了最后一个 ``assert 0`` 行，我们用它来看看值：

.. code-block:: pytest

    $ pytest test_tmp_path.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 1 item

    test_tmp_path.py F                                                   [100%]

    ================================= FAILURES =================================
    _____________________________ test_create_file _____________________________

    tmp_path = PosixPath('PYTEST_TMPDIR/test_create_file0')

        def test_create_file(tmp_path):
            d = tmp_path / "sub"
            d.mkdir()
            p = d / "hello.txt"
            p.write_text(CONTENT, encoding="utf-8")
            assert p.read_text(encoding="utf-8") == CONTENT
            assert len(list(tmp_path.iterdir())) == 1
    >       assert 0
    E       assert 0

    test_tmp_path.py:11: AssertionError
    ========================= short test summary info ==========================
    FAILED test_tmp_path.py::test_create_file - assert 0
    ============================ 1 failed in 0.12s =============================

默认情况下，``pytest`` 会保留最近 3 次 ``pytest`` 调用的临时目录。通过将基本临时目录配置为每次并发运行唯一，支持同一测试函数的并发调用。参见 `temporary directory location and retention`_ 了解详情。

.. _`tmp_path_factory example`:

``tmp_path_factory`` fixture
--------------------------------

``tmp_path_factory`` 是一个会话范围的 fixture，可用于从任何其他 fixture 或测试创建任意临时目录。

例如，假设你的测试套件需要一个磁盘上的大图像，该图像是程序生成的。与其为每个使用它的测试计算相同的图像到它自己的 ``tmp_path`` 中，不如每个会话只生成一次以节省时间：

.. code-block:: python

    # conftest.py 的内容
    import pytest


    @pytest.fixture(scope="session")
    def image_file(tmp_path_factory):
        img = compute_expensive_image()
        fn = tmp_path_factory.mktemp("data") / "img.png"
        img.save(fn)
        return fn


    # test_image.py 的内容
    def test_histogram(image_file):
        img = load_image(image_file)
        # compute and test histogram

参见 :ref:`tmp_path_factory API <tmp_path_factory factory api>` 了解详情。

.. _`tmpdir and tmpdir_factory`:
.. _tmpdir:

``tmpdir`` 和 ``tmpdir_factory`` fixtures
----------------------------------------------

``tmpdir`` 和 ``tmpdir_factory`` fixtures 类似于 ``tmp_path`` 和 ``tmp_path_factory``，但使用/返回遗留的 `py.path.local`_ 对象，而不是标准的 :class:`pathlib.Path` 对象。

.. note::
    如今，更倾向于使用 ``tmp_path`` 和 ``tmp_path_factory``。

    为了帮助现代化旧的代码库，可以在禁用 legacypath 插件的情况下运行 pytest：

    .. code-block:: bash

        pytest -p no:legacypath

    这将触发使用遗留路径的测试的错误。
    它也可以作为 :confval:`addopts` 参数的一部分永久设置在配置文件中。

参见 :fixture:`tmpdir <tmpdir>` :fixture:`tmpdir_factory <tmpdir_factory>` API 了解详情。


.. _`temporary directory location and retention`:

临时目录位置和保留
------------------------------------------

临时目录，
由 :fixture:`tmp_path` 和（现已弃用的）:fixture:`tmpdir` fixtures 返回，
在基本临时目录下自动创建，
结构取决于 :option:`--basetemp` 选项：

- 默认情况下（当未设置 :option:`--basetemp` 选项时），
  临时目录将遵循以下模板：

  .. code-block:: text

      {temproot}/pytest-of-{user}/pytest-{num}/{testname}/

  其中：

  - ``{temproot}`` 是系统临时目录，
    由 :py:func:`tempfile.gettempdir` 确定。
    它可以通过 :envvar:`PYTEST_DEBUG_TEMPROOT` 环境变量覆盖。
  - ``{user}`` 是运行测试的用户名，
  - ``{num}`` 是一个数字，每次测试套件运行时递增
  - ``{testname}`` 是 :py:attr:`当前测试的名称 <_pytest.nodes.Node.name>` 的清理版本。

  自动递增的 ``{num}`` 占位符提供了基本的保留功能，
  避免盲目删除先前测试运行的现有结果。
  默认情况下，保留最后 3 个临时目录，
  但此行为可以通过
  :confval:`tmp_path_retention_count` 和 :confval:`tmp_path_retention_policy` 配置。

- 当使用 :option:`--basetemp` 选项时（例如 ``pytest --basetemp=mydir``），
  它将直接用作基本临时目录：

  .. code-block:: text

      {basetemp}/{testname}/

  请注意，在这种情况下没有保留功能：
  只保留最近运行的结果。

  .. warning::

      给 :option:`--basetemp` 的目录将在每次测试运行之前被盲目清除，
      因此请确保仅将该目录用于此目的。

当使用 ``pytest-xdist`` 在本地机器上分发测试时，注意会自动为子进程配置一个 `basetemp` 目录，以便所有临时数据都位于每个测试运行的单一临时目录下。

.. _`py.path.local`: https://py.readthedocs.io/en/latest/path.html

