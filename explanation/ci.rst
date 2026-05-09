.. _`ci-pipelines`:

CI 流水线
==========

原理
---------

在 CI 流水线中测试的目标与本地测试不同。确实，
你可以在计算机上快速编辑一些代码并再次运行测试，但
在 CI 流水线中这是不可能的。它们运行在单独的服务器上，并由
特定操作触发。

基于这一观察，pytest 可以检测它是否在 CI 环境中，并
调整它的一些行为。

如何检测 CI
------------------

当以下任一环境变量被设置为非空值时，Pytest 就知道它在 CI 环境中：

* :envvar:`CI`: 被许多 CI 系统使用。
* :envvar:`BUILD_NUMBER`: 被 Jenkins 使用。

CI 的影响
-------------

目前，处于 CI 环境对 pytest 的影响是有限的。

当检测到 CI 环境时，简短测试摘要信息的输出不再被截断到终端大小，即整个消息将被显示。

  .. code-block:: python

        # test_ci.py 的内容
        import pytest


        def test_db_initialized():
            pytest.fail(
                "deliberately failing for demo purpose, Lorem ipsum dolor sit amet, "
                "consectetur adipiscing elit. Cras facilisis, massa in suscipit "
                "dignissim, mauris lacus molestie nisi, quis varius metus nulla ut ipsum."
            )


在本地运行此测试，不带任何额外选项，将输出：

  .. code-block:: pytest

     $ pytest test_ci.py
     ...
     ========================= short test summary info ==========================
     FAILED test_ci.py::test_db_initialized - Failed: deliberately f...

*(注意截断的文本)*


而在 CI 上运行将输出：

  .. code-block:: pytest

     $ export CI=true
     $ pytest test_ci.py
     ...
     ========================= short test summary info ==========================
     FAILED test_ci.py::test_db_initialized - Failed: deliberately failing
     for demo purpose, Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras
     facilisis, massa in suscipit dignissim, mauris lacus molestie nisi, quis varius
     metus nulla ut ipsum.
