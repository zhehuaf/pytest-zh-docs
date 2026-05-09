
.. _`accept example`:

示例：指定和选择验收测试
--------------------------------------------------------------

.. sourcecode:: python

    # ./conftest.py
    def pytest_option(parser):
        group = parser.getgroup("myproject")
        group.addoption(
            "-A", dest="acceptance", action="store_true", help="运行（慢的）验收测试"
        )


    def pytest_funcarg__accept(request):
        return AcceptFixture(request)


    class AcceptFixture:
        def __init__(self, request):
            if not request.config.getoption("acceptance"):
                pytest.skip("指定 -A 来运行验收测试")
            self.tmpdir = request.config.mktemp(request.function.__name__, numbered=True)

        def run(self, *cmd):
            """被测试代码调用来执行验收测试。"""
            self.tmpdir.chdir()
            return subprocess.check_output(cmd).decode()


实际的测试函数示例：

.. sourcecode:: python

    def test_some_acceptance_aspect(accept):
        accept.tmpdir.mkdir("somesub")
        result = accept.run("ls", "-la")
        assert "somesub" in result

如果你运行此测试而不指定命令行选项，测试将被跳过并显示适当的消息。否则你可以开始在你的 AcceptFixture 中添加便利和测试支持方法，并驱动工具或应用程序的运行，并提供对输出进行断言的方法。

.. _`decorate a funcarg`:

示例：在测试模块中装饰 funcarg
--------------------------------------------------------------

对于更大规模的设置，有时仅为特定测试模块装饰 funcarg 是有用的。我们可以通过在我们的测试模块中放置以下内容来扩展 `accept 示例`_：

.. sourcecode:: python

    def pytest_funcarg__accept(request):
        # 调用下一个工厂（位于我们的 conftest.py 中）
        arg = request.getfuncargvalue("accept")
        # 在我们的临时目录中创建特殊布局
        arg.tmpdir.mkdir("special")
        return arg


    class TestSpecialAcceptance:
        def test_sometest(self, accept):
            assert accept.tmpdir.join("special").check()

我们的模块级工厂将首先被调用，它可以要求其请求对象调用下一个工厂，然后装饰其结果。这个机制允许我们对函数参数是如何/在哪里提供的保持无知——在我们的例子中，来自 `conftest 插件`_。

旁注：这里使用的临时目录是 `py.path.local`_ 类的实例，它以便捷的方式提供了许多 os.path 方法。

.. _`py.path.local`: ../path.html#local
.. _`conftest plugin`: customize.html#conftestplugin
