
.. _naming20:

pytest 2.0 中的新名称（扁平优于嵌套）
----------------------------------------------------

如果你使用过旧版本的 ``py`` 分发版（包括
py.test 命令行工具和 Python 命名空间）
你通过 ``py.test`` Python 命名空间访问辅助工具
和可能的集合类。新的 ``pytest``
Python 模块以平面方式提供相同的对象，遵循
以下重命名规则：：

    py.test.XYZ          -> pytest.XYZ
    py.test.collect.XYZ  -> pytest.XYZ
    py.test.cmdline.main -> pytest.main

旧的 ``py.test.*`` 访问功能的方式仍然
有效，但鼓励你按照上述规则在你的测试代码中进行全局重命名。
