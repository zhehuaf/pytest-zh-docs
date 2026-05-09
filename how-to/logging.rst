.. _logging:

如何管理日志
---------------------

pytest 自动捕获 ``WARNING`` 级别或更高级别的日志消息，并在每个失败测试的自己的部分中显示它们，方式与捕获的 stdout 和 stderr 相同。

不带选项运行：

.. code-block:: bash

    pytest

显示失败的测试如下：

.. code-block:: pytest

    ----------------------- Captured stdlog call ----------------------
    test_reporting.py    26 WARNING  text going to logger
    ----------------------- Captured stdout call ----------------------
    text going to stdout
    ----------------------- Captured stderr call ----------------------
    text going to stderr
    ==================== 2 failed in 0.02 seconds =====================

默认情况下，每个捕获的日志消息显示模块、行号、日志级别和消息。

如果需要，可以将日志和日期格式指定为日志模块支持的任何格式，通过传递特定的格式选项：

.. code-block:: bash

    pytest --log-format="%(asctime)s %(levelname)s %(message)s" \
            --log-date-format="%Y-%m-%d %H:%M:%S"

显示失败的测试如下：

.. code-block:: pytest

    ----------------------- Captured stdlog call ----------------------
    2010-04-10 14:48:44 WARNING text going to logger
    ----------------------- Captured stdout call ----------------------
    text going to stdout
    ----------------------- Captured stderr call ----------------------
    text going to stderr
    ==================== 2 failed in 0.02 seconds =====================

这些选项也可以通过配置文件进行自定义：

.. tab:: toml

    .. code-block:: toml

        [pytest]
        log_format = "%(asctime)s %(levelname)s %(message)s"
        log_date_format = "%Y-%m-%d %H:%M:%S"

.. tab:: ini

    .. code-block:: ini

        [pytest]
        log_format = %(asctime)s %(levelname)s %(message)s
        log_date_format = %Y-%m-%d %H:%M:%S

可以通过 :option:`--log-disable={logger_name}` 禁用特定的日志记录器。此参数可以多次传递：

.. code-block:: bash

    pytest --log-disable=main --log-disable=testing

此外，可以完全禁用对失败测试的捕获内容（stdout、stderr 和日志）的报告：

.. code-block:: bash

    pytest --show-capture=no


caplog fixture
^^^^^^^^^^^^^^

在测试内部，可以更改捕获日志消息的日志级别。这是通过 ``caplog`` fixture 支持的：

.. code-block:: python

    def test_foo(caplog):
        caplog.set_level(logging.INFO)

默认情况下，级别设置在根日志记录器上，但为了方便，也可以设置任何日志记录器的日志级别：

.. code-block:: python

    def test_foo(caplog):
        caplog.set_level(logging.CRITICAL, logger="root.baz")

在测试结束时，设置的日志级别会自动恢复。

也可以使用上下文管理器在 ``with`` 块内临时更改日志级别：

.. code-block:: python

    def test_bar(caplog):
        with caplog.at_level(logging.INFO):
            pass

同样，默认情况下影响根日志记录器的级别，但可以使用以下方式更改任何日志记录器的级别：

.. code-block:: python

    def test_bar(caplog):
        with caplog.at_level(logging.CRITICAL, logger="root.baz"):
            pass

最后，测试运行期间发送到日志记录器的所有日志都以 ``logging.LogRecord`` 实例和最终日志文本的形式在 fixture 上提供。这对于想要断言消息内容时很有用：

.. code-block:: python

    def test_baz(caplog):
        func_under_test()
        for record in caplog.records:
            assert record.levelname != "CRITICAL"
        assert "wally" not in caplog.text

有关日志记录的所有可用属性，请参见 ``logging.LogRecord`` 类。

如果你想确保某些消息已使用给定的日志记录器名称和给定的严重性和消息记录，也可以使用 ``record_tuples``：

.. code-block:: python

    def test_foo(caplog):
        logging.getLogger().info("boo %s", "arg")

        assert caplog.record_tuples == [("root", logging.INFO, "boo arg")]

你可以调用 ``caplog.clear()`` 来重置测试中捕获的日志记录：

.. code-block:: python

    def test_something_with_clearing_records(caplog):
        some_method_that_creates_log_records()
        caplog.clear()
        your_test_method()
        assert ["Foo"] == [rec.message for rec in caplog.records]


``caplog.records`` 属性仅包含当前阶段的记录，因此在 ``setup`` 阶段，它只包含设置日志，``call`` 和 ``teardown`` 阶段也是如此。

要访问其他阶段的日志，请使用 ``caplog.get_records(when)`` 方法。例如，如果你想确保使用特定 fixture 的测试从不记录任何警告，你可以在拆卸期间检查 ``setup`` 和 ``call`` 阶段的记录，如下所示：

.. code-block:: python

    @pytest.fixture
    def window(caplog):
        window = create_window()
        yield window
        for when in ("setup", "call"):
            messages = [
                x.message for x in caplog.get_records(when) if x.levelno == logging.WARNING
            ]
            if messages:
                pytest.fail(f"warning messages encountered during testing: {messages}")



完整 API 可在 :class:`pytest.LogCaptureFixture` 查看。

.. warning::

    ``caplog`` fixture 向根日志记录器添加一个处理程序以捕获日志。如果在测试期间修改根日志记录器，例如使用 ``logging.config.dictConfig``，此处理程序可能会被删除并导致没有日志被捕获。为避免这种情况，请确保任何根日志记录器配置仅添加到现有处理程序。


.. _live_logs:

实时日志
^^^^^^^^^

通过将 :confval:`log_cli` 配置选项设置为 ``true``，pytest 将在日志记录发出时直接将它们输出到控制台。

你可以通过传递 :option:`--log-cli-level` 指定日志级别，具有相等或更高级别的日志记录将打印到控制台。此设置接受日志级别名称或数值，如 :ref:`logging's documentation <python:levels>` 中所示。

此外，你还可以指定 :option:`--log-cli-format` 和 :option:`--log-cli-date-format`，它们镜像并默认为 :option:`--log-format` 和 :option:`--log-date-format` （如果未提供），但仅应用于控制台日志处理程序。

所有 CLI 日志选项也可以在配置文件中设置。选项名称为：

* :confval:`log_cli_level`
* :confval:`log_cli_format`
* :confval:`log_cli_date_format`

如果你需要将整个测试套件的日志记录调用记录到文件，你可以传递 :option:`--log-file=/path/to/log/file`。默认情况下，此日志文件以写入模式打开，这意味着它将在每次测试会话时被覆盖。
如果你想以追加模式打开文件，则可以传递 :option:`--log-file-mode=a`。请注意，日志文件位置的相对路径，无论是在 CLI 上传递还是在配置文件中声明，都始终相对于当前工作目录解析。

你还可以通过传递 :option:`--log-file-level` 指定日志文件的日志级别。此设置接受日志级别名称或数值，如 :ref:`logging's documentation <python:levels>` 中所示。

此外，你还可以指定 :option:`--log-file-format` 和 :option:`--log-file-date-format`，它们等于 ``--log-format`` 和 :option:`--log-date-format`，但应用于日志文件日志处理程序。

所有日志文件选项也可以在配置文件中设置。选项名称为：

* :confval:`log_file`
* :confval:`log_file_mode`
* :confval:`log_file_level`
* :confval:`log_file_format`
* :confval:`log_file_date_format`

你可以调用 ``set_log_path()`` 来动态自定义 log_file 路径。此功能被认为是实验性的。请注意，``set_log_path()`` 遵循 :confval:`log_file_mode` 选项。

.. _log_colors:

自定义颜色
^^^^^^^^^^^^^^^^^^

如果启用了彩色终端输出，日志级别将显示为彩色。通过 ``add_color_level()`` 支持从默认颜色更改或在自定义日志级别上添加颜色。示例：

.. code-block:: python

    @pytest.hookimpl(trylast=True)
    def pytest_configure(config):
        logging_plugin = config.pluginmanager.get_plugin("logging-plugin")

        # 更改现有日志级别的颜色
        logging_plugin.log_cli_handler.formatter.add_color_level(logging.INFO, "cyan")

        # 为自定义日志级别添加颜色（自定义日志级别 `SPAM` 已设置）
        logging_plugin.log_cli_handler.formatter.add_color_level(logging.SPAM, "blue")
.. warning::

    此功能及其 API 被认为是实验性的，可能在版本之间更改，而不需要弃用通知。
.. _log_release_notes:

发布说明
^^^^^^^^^^^^^

此功能是作为 :pypi:`pytest-catchlog` 插件的直接替代品引入的，它们相互冲突。当引入此功能时，与 ``pytest-capturelog`` 的向后兼容性 API 已被删除，因此如果由于该原因你仍然需要 ``pytest-catchlog``，你可以通过添加到你的配置文件来禁用内部功能：

.. tab:: toml

    .. code-block:: toml

        [pytest]
        addopts = ["-p", "no:logging"]

.. tab:: ini

    .. code-block:: ini

        [pytest]
        addopts = -p no:logging


.. _log_changes_3_4:

pytest 3.4 中的不兼容更改
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

此功能在 ``3.3`` 中引入，在 ``3.4`` 中根据社区反馈进行了一些不兼容的更改：

* 除非 :confval:`log_level` 配置或 :option:`--log-level` 命令行选项明确要求，否则不再更改日志级别。这允许用户自己配置日志记录器对象。设置 :confval:`log_level` 将全局设置捕获的级别，因此如果特定测试需要比此更低的级别，请使用 ``caplog.set_level()`` 功能，否则该测试将容易失败。
* :ref:`实时日志 <live_logs>` 现在默认禁用，可以通过将 :confval:`log_cli` 配置选项设置为 ``true`` 来启用。启用后，详细程度会增加，以便可以看到每个测试的日志记录。
* :ref:`实时日志 <live_logs>` 现在发送到 ``sys.stdout``，不再需要 :option:`-s` 命令行选项即可工作。

如果你想部分恢复版本 ``3.3`` 的日志行为，你可以将这些选项添加到你的配置文件：

.. tab:: toml

    .. code-block:: toml

        [pytest]
        log_cli = true
        log_level = "NOTSET"

.. tab:: ini

    .. code-block:: ini

        [pytest]
        log_cli = true
        log_level = NOTSET

有关导致这些更改的讨论的更多详细信息，请阅读 :issue:`3013`。
