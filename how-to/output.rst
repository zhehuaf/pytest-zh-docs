.. _reporting:

如何定制测试报告
================================

.. _showing-durations:

显示每个测试用例的执行时间
--------------------------------------------------

.. regendoc:wipe

要获得每个最慢测试用例的列表，请使用 ``--durations=N`` 选项：

.. code-block:: pytest

    $ pytest --durations=3
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 3 items

    test_slow.py ...                                                     [100%]

    ========================= slowest 3 durations =============================
    0.01s call     test_slow.py::test_1
    0.00s call     test_slow.py::test_2
    0.00s call     test_slow.py::test_3
    =========================== 3 passed in 0.12s =============================

默认情况下，pytest 将显示 ``.00s`` 持续时间，对于非常慢的测试（通常表示 IO 操作），这将正确显示为 ``15.28s``。

你可以传递 ``--durations-min=3.5`` 来隐藏低于特定值（在本例中为 3.5 秒）的持续时间。``--durations`` 默认值为 ``N=10``。

::

    ========================= slowest 3 durations =============================
    15.28s call     test_slow.py::test_1
    5.42s call      test_slow.py::test_2
    0.32s call      test_slow.py::test_3
    =========================== 3 passed in 15.32s =============================

或者传递 ``--durations=-1`` 来显示所有测试的持续时间，顺序从慢到快。

默认情况下，此功能将排序并显示 ``call`` 持续时间，但也可以使用 ``--durations-order={duration_type}`` 选项按其他持续时间排序，包括 ``call``、``setup``、``teardown`` 或这三者的组合（例如 ``setup teardown call``）。

注意，无论使用哪个持续时间顺序，这都会显示每个测试的这三个持续时间，但测试会话摘要中只包含排序依据的那个。

还要注意，排序是按阶段时长完成的，因此如果你选择 ``setup``，时长为 10 秒的 fixture（影响三个测试）将排在前面，因为它在三个测试中的总时长为 30 秒，而 3 秒的测试在单独一行上。

还要注意，这对 ``-vv`` 或 ``--no-header`` 或 ``-q`` 输出没有影响，因为实际测试中很少需要按持续时间排序。

.. _pytest.detailed_failed_tests_usage:

生成详细的摘要报告
--------------------------------------------------

:option:`-r` 标志可用于在测试会话结束时显示"短测试摘要信息"，
使大型测试套件能够轻松清晰地了解所有失败、跳过、xfail 等。

它默认为 ``fE`` 以列出失败和错误。

.. regendoc:wipe

示例：

.. code-block:: python

    # test_example.py 的内容
    import pytest


    @pytest.fixture
    def error_fixture():
        assert 0


    def test_ok():
        print("ok")


    def test_fail():
        assert 0


    def test_error(error_fixture):
        pass


    def test_skip():
        pytest.skip("跳过此测试")


    def test_xfail():
        pytest.xfail("预期失败此测试")


    @pytest.mark.xfail(reason="总是 xfail")
    def test_xpass():
        pass


.. code-block:: pytest

    $ pytest -ra
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 6 items

    test_example.py .FEsxX                                               [100%]

    ================================== ERRORS ==================================
    _______________________ ERROR at setup of test_error _______________________

        @pytest.fixture
        def error_fixture():
    >       assert 0
    E       assert 0

    test_example.py:6: AssertionError
    ================================= FAILURES =================================
    ________________________________ test_fail _________________________________

        def test_fail():
    >       assert 0
    E       assert 0

    test_example.py:14: AssertionError
    ================================= XPASSES ==================================
    ========================= short test summary info ==========================
    SKIPPED [1] test_example.py:22: 跳过此测试
    XFAIL test_example.py::test_xfail - 预期失败此测试
    XPASS test_example.py::test_xpass - 总是 xfail
    ERROR test_example.py::test_error - assert 0
    FAILED test_example.py::test_fail - assert 0
    == 1 failed, 1 passed, 1 skipped, 1 xfailed, 1 xpassed, 1 error in 0.12s ===

:option:`-r` 选项后面可以接受多个字符，上面使用的 ``a`` 表示"除通过外的所有"。

以下是可用字符的完整列表：

 - ``f`` - 失败
 - ``E`` - 错误
 - ``s`` - 跳过
 - ``x`` - xfailed
 - ``X`` - xpassed
 - ``p`` - 通过
 - ``P`` - 有输出的通过

用于（取消）选择组的特殊字符：

 - ``a`` - 除 ``pP`` 外的所有
 - ``A`` - 所有
 - ``N`` - 无，可用于不显示任何内容（因为 ``fE`` 是默认值）

可以使用多个字符，因此例如要仅查看失败和跳过的测试，可以执行：

.. code-block:: pytest

    $ pytest -rfs
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 6 items

    test_example.py .FEsxX                                               [100%]

    ================================== ERRORS ==================================
    _______________________ ERROR at setup of test_error _______________________

        @pytest.fixture
        def error_fixture():
    >       assert 0
    E       assert 0

    test_example.py:6: AssertionError
    ================================= FAILURES =================================
    ________________________________ test_fail _________________________________

        def test_fail():
    >       assert 0
    E       assert 0

    test_example.py:14: AssertionError
    ========================= short test summary info ==========================
    FAILED test_example.py::test_fail - assert 0
    SKIPPED [1] test_example.py:22: 跳过此测试
    == 1 failed, 1 passed, 1 skipped, 1 xfailed, 1 xpassed, 1 error in 0.12s ===

使用 ``p`` 列出通过的测试，而 ``P`` 添加一个额外的"PASSES"部分，其中包含那些有输出但通过了的测试：

.. code-block:: pytest

    $ pytest -rpP
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 6 items

    test_example.py .FEsxX                                               [100%]

    ================================== ERRORS ==================================
    _______________________ ERROR at setup of test_error _______________________

        @pytest.fixture
        def error_fixture():
    >       assert 0
    E       assert 0

    test_example.py:6: AssertionError
    ================================= FAILURES =================================
    ________________________________ test_fail _________________________________

        def test_fail():
    >       assert 0
    E       assert 0

    test_example.py:14: AssertionError
    ================================== PASSES ==================================
    _________________________________ test_ok __________________________________
    --------------------------- Captured stdout call ---------------------------
    ok
    ========================= short test summary info ==========================
    PASSED test_example.py::test_ok
    == 1 failed, 1 passed, 1 skipped, 1 xfailed, 1 xpassed, 1 error in 0.12s ===

.. note::

    默认情况下，如果跳过的测试的参数化变体共享相同的跳过原因，它们会被分组在一起。你可以使用 :option:`--no-fold-skipped` 来单独打印每个跳过的测试。


.. _truncation-params:

修改截断限制
--------------------------------------------------

.. versionadded: 8.4

默认截断限制是 8 行或 640 个字符，以先达到者为准。
要设置自定义截断限制，你可以使用以下配置文件选项：

.. tab:: toml

    .. code-block:: toml

        [pytest]
        truncation_limit_lines = 10
        truncation_limit_chars = 90

.. tab:: ini

    .. code-block:: ini

        [pytest]
        truncation_limit_lines = 10
        truncation_limit_chars = 90

这将导致 pytest 将断言截断为 10 行或 90 个字符，以先达到者为准。

将 :confval:`truncation_limit_lines` 和 :confval:`truncation_limit_chars` 都设置为 ``0`` 将禁用截断。
但是，只设置其中一个值将禁用一种截断模式，但保留另一种。


创建 JUnitXML 格式文件
----------------------------------------------------

要创建可被 Jenkins_ 或其他持续集成服务器读取的结果文件，请使用此调用：

.. code-block:: bash

    pytest --junit-xml=path

在 ``path`` 处创建 XML 文件。


要设置根测试套件 xml 项目的名称，可以在配置文件中配置 ``junit_suite_name`` 选项：

.. tab:: toml

    .. code-block:: toml

        [pytest]
        junit_suite_name = "my_suite"

.. tab:: ini

    .. code-block:: ini

        [pytest]
        junit_suite_name = my_suite

.. versionadded:: 4.0

JUnit XML 规范似乎表明 ``"time"`` 属性应报告总测试执行时间，包括设置和拆卸（`1 <http://windyroad.com.au/dl/Open%20Source/JUnit.xsd>`_，`2 <https://www.ibm.com/support/knowledgecenter/en/SSQ2R2_14.1.0/com.ibm.rsar.analysis.codereview.cobol.doc/topics/cac_useresults_junit.html>`_）。
这是 pytest 的默认行为。要仅报告调用持续时间，请像这样配置 ``junit_duration_report`` 选项：

.. tab:: toml

    .. code-block:: toml

        [pytest]
        junit_duration_report = "call"

.. tab:: ini

    .. code-block:: ini

        [pytest]
        junit_duration_report = call

.. _record_property example:

record_property
~~~~~~~~~~~~~~~~~

如果你想为测试记录额外信息，可以使用 ``record_property`` fixture：

.. code-block:: python

    def test_function(record_property):
        record_property("example_key", 1)
        assert True

这将为生成的 ``testcase`` 标签添加一个额外的属性 ``example_key="1"``：

.. code-block:: xml

    <testcase classname="test_function" file="test_function.py" line="0" name="test_function" time="0.0009">
      <properties>
        <property name="example_key" value="1" />
      </properties>
    </testcase>

或者，你可以将此功能与自定义标记集成：

.. code-block:: python

    # conftest.py 的内容


    def pytest_collection_modifyitems(session, config, items):
        for item in items:
            for marker in item.iter_markers(name="test_id"):
                test_id = marker.args[0]
                item.user_properties.append(("test_id", test_id))

在你的测试中：

.. code-block:: python

    # test_function.py 的内容
    import pytest


    @pytest.mark.test_id(1501)
    def test_function():
        assert True

将产生：

.. code-block:: xml

    <testcase classname="test_function" file="test_function.py" line="0" name="test_function" time="0.0009">
      <properties>
        <property name="test_id" value="1501" />
      </properties>
    </testcase>

.. warning::

    请注意，使用此功能将破坏最新 JUnitXML 模式的模式验证。
    当与某些 CI 服务器一起使用时，这可能是一个问题。


record_xml_attribute
~~~~~~~~~~~~~~~~~~~~~~

要向 testcase 元素添加额外的 xml 属性，你可以使用 ``record_xml_attribute`` fixture。这也可以用于覆盖现有值：

.. code-block:: python

    def test_function(record_xml_attribute):
        record_xml_attribute("assertions", "REQ-1234")
        record_xml_attribute("classname", "custom_classname")
        print("hello world")
        assert True

与 ``record_property`` 不同，这不会添加新的子元素。
相反，这将在生成的 ``testcase`` 标签内添加属性 ``assertions="REQ-1234"``，并将默认的 ``classname`` 覆盖为 ``"classname=custom_classname"``：

.. code-block:: xml

    <testcase classname="custom_classname" file="test_function.py" line="0" name="test_function" time="0.003" assertions="REQ-1234">
        <system-out>
            hello world
        </system-out>
    </testcase>

.. warning::

    ``record_xml_attribute`` 是一个实验性功能，其接口可能会被未来版本中更强大和通用的东西取代。
    然而，该功能本身将被保留。

    与 ``record_xml_property`` 相比，在 CI 工具解析 xml 报告时使用此功能会有所帮助。
    但是，某些解析器对所允许的元素和属性非常严格。
    许多工具使用 xsd 模式（如下例所示）来验证传入的 xml。
    确保你使用的属性名称被你的解析器允许。

    以下是 Jenkins 用于验证 XML 报告的模式：

    .. code-block:: xml

        <xs:element name="testcase">
            <xs:complexType>
                <xs:sequence>
                    <xs:element ref="skipped" minOccurs="0" maxOccurs="1"/>
                    <xs:element ref="error" minOccurs="0" maxOccurs="unbounded"/>
                    <xs:element ref="failure" minOccurs="0" maxOccurs="unbounded"/>
                    <xs:element ref="system-out" minOccurs="0" maxOccurs="unbounded"/>
                    <xs:element ref="system-err" minOccurs="0" maxOccurs="unbounded"/>
                </xs:sequence>
                <xs:attribute name="name" type="xs:string" use="required"/>
                <xs:attribute name="assertions" type="xs:string" use="optional"/>
                <xs:attribute name="time" type="xs:string" use="optional"/>
                <xs:attribute name="classname" type="xs:string" use="optional"/>
                <xs:attribute name="status" type="xs:string" use="optional"/>
            </xs:complexType>
        </xs:element>

.. warning::

    请注意，使用此功能将破坏最新 JUnitXML 模式的模式验证。
    当与某些 CI 服务器一起使用时，这可能是一个问题。

.. _record_testsuite_property example:

record_testsuite_property
^^^^^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: 4.5

如果你想在测试套件级别添加一个属性节点，该节点可能包含与所有测试相关的属性，你可以使用 ``record_testsuite_property`` 会话范围的 fixture：

``record_testsuite_property`` 会话范围的 fixture 可用于添加与所有测试相关的属性。

.. code-block:: python

    import pytest


    @pytest.fixture(scope="session", autouse=True)
    def log_global_env_facts(record_testsuite_property):
        record_testsuite_property("ARCH", "PPC")
        record_testsuite_property("STORAGE_TYPE", "CEPH")


    class TestMe:
        def test_foo(self):
            assert True

该 fixture 是一个可调用的，它接收在生成的 xml 的测试套件级别添加的 ``<property>`` 标签的 ``name`` 和 ``value``：

.. code-block:: xml

    <testsuite errors="0" failures="0" name="pytest" skipped="0" tests="1" time="0.006">
      <properties>
        <property name="ARCH" value="PPC"/>
        <property name="STORAGE_TYPE" value="CEPH"/>
      </properties>
      <testcase classname="test_me.TestMe" file="test_me.py" line="16" name="test_foo" time="0.000243663787842"/>
    </testsuite>

``name`` 必须是字符串，``value`` 将转换为字符串并正确进行 xml 转义。

生成的 XML 与最新的 ``xunit`` 标准兼容，这与 `record_property`_ 和 `record_xml_attribute`_ 相反。


将测试报告发送到在线 pastebin 服务
--------------------------------------------------

**为每个测试失败创建 URL**：

.. code-block:: bash

    pytest --pastebin=failed

这将把测试运行信息提交到远程 Paste 服务，并为每个失败提供一个 URL。你可以像往常一样选择测试，或添加例如 :option:`-x`，如果你只想发送一个特定的失败。

**为整个测试会话日志创建 URL**：

.. code-block:: bash

    pytest --pastebin=all

目前仅实现了粘贴到 https://bpaste.net/ 服务。

.. versionchanged:: 5.2

如果由于任何原因创建 URL 失败，将生成警告而不是使整个测试套件失败。

.. _jenkins: https://jenkins-ci.org
