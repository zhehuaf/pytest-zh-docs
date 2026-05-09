:orphan:

===================================
提案：使用 fixtures 进行参数化
===================================

.. warning::

    本文档概述了一个关于使用 fixtures 作为参数化测试或 fixtures 输入的提案。

问题
-------

作为用户，我有功能测试想要在多种场景下运行。

在这个特定示例中，我们想要基于 cookiecutter 模板生成一个新项目。我们想要测试默认值，同时也想要模拟用户输入的数据。

- 使用默认值

- 模拟用户输入

  - 指定 'author'

  - 指定 'project_slug'

  - 指定 'author' 和 'project_slug'

这是一个功能测试可能的样子：

.. code-block:: python

    import pytest


    @pytest.fixture
    def default_context():
        return {"extra_context": {}}


    @pytest.fixture(
        params=[
            {"author": "alice"},
            {"project_slug": "helloworld"},
            {"author": "bob", "project_slug": "foobar"},
        ]
    )
    def extra_context(request):
        return {"extra_context": request.param}


    @pytest.fixture(params=["default", "extra"])
    def context(request):
        if request.param == "default":
            return request.getfuncargvalue("default_context")
        else:
            return request.getfuncargvalue("extra_context")


    def test_generate_project(cookies, context):
        """调用 cookiecutter API 从模板生成新项目。
        """
        result = cookies.bake(extra_context=context)

        assert result.exit_code == 0
        assert result.exception is None
        assert result.project.isdir()


问题
------

* 通过使用 ``request.getfuncargvalue()``，我们依赖于实际的 fixture 函数执行来了解涉及哪些 fixtures，这是由于其动态特性
* 更重要的是，``request.getfuncargvalue()`` 不能与参数化 fixtures（如 ``extra_context``）结合使用
* 如果你想通过某些参数扩展现有测试套件，而这些参数用于已被测试使用的 fixtures，这非常不方便

pytest 3.0 版本报告错误，如果你尝试运行上述代码：

    Failed: The requested fixture has no parameter defined for the current
    test.

    Requested fixture 'extra_context'


建议解决方案
-----------------

模块中可以使用一个新函数来动态地从现有 fixtures 定义 fixtures。

.. code-block:: python

    pytest.define_combined_fixture(
        name="context", fixtures=["default_context", "extra_context"]
    )

新 fixture ``context`` 继承所用 fixtures 的作用域，并产生以下值。

- ``{}``

- ``{'author': 'alice'}``

- ``{'project_slug': 'helloworld'}``

- ``{'author': 'bob', 'project_slug': 'foobar'}``

替代方法
--------------------

一个名为 ``fixture_request`` 的新辅助函数会告诉 pytest 产生所有标记为 fixture 的参数。

.. note::

    :pypi:`pytest-lazy-fixture` 插件实现了一个与下面提案非常相似的解决方案，请确保查看它。

.. code-block:: python

    @pytest.fixture(
        params=[
            pytest.fixture_request("default_context"),
            pytest.fixture_request("extra_context"),
        ]
    )
    def context(request):
        """逐个返回 ``default_context`` 的所有值，然后逐个返回 ``extra_context`` 的所有值。

        request.param:
            - {}
            - {'author': 'alice'}
            - {'project_slug': 'helloworld'}
            - {'author': 'bob', 'project_slug': 'foobar'}
        """
        return request.param

同样的辅助函数可以与 ``pytest.mark.parametrize`` 结合使用。

.. code-block:: python


    @pytest.mark.parametrize(
        "context, expected_response_code",
        [
            (pytest.fixture_request("default_context"), 0),
            (pytest.fixture_request("extra_context"), 0),
        ],
    )
    def test_generate_project(cookies, context, exit_code):
        """调用 cookiecutter API 从模板生成新项目。
        """
        result = cookies.bake(extra_context=context)

        assert result.exit_code == exit_code
