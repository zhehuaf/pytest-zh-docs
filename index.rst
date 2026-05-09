.. _features:

.. sidebar:: **即将举办的培训和活动**

    - `Python 专业测试 <https://python-academy.com/courses/python_course_testing.html>`_, 通过 `Python Academy <https://www.python-academy.com/>`_ (为期 3 天的深入培训), **2027年3月9日 -- 11日**, 莱比锡 (德国) / 远程

    另请参见 :doc:`以往的演讲和博客文章 <talks>`

.. note::

   本文档基于 **pytest 9.0.3** 英文文档翻译。

   **翻译完成度：**
   - ✅ 所有 ``how-to/``、``explanation/``、``example/`` 目录下的文档已全部翻译完成
   - ✅ ``builtin``、``backwards-compatibility``、``reference/exit-codes``、``talks``、``adopt``、``license`` 等参考文档已翻译完成
   - ⏳ ``changelog``（11796行）、``deprecations``（1513行）、``reference/reference``（API 参考, 3663行）等仍有待翻译
   - ⏳ ``reference/plugin_list``（自动生成的插件列表）待翻译
   - ⏳ ``announce/``（版本发布公告）待翻译

   欢迎通过 https://github.com/pytest-dev/pytest 贡献翻译。

pytest: 帮助你编写更好的程序
=======================================

.. toctree::
    :hidden:

    getting-started
    how-to/index
    reference/index
    explanation/index
    example/index

.. toctree::
    :caption: 关于项目
    :hidden:

    changelog
    contributing
    backwards-compatibility
    sponsor
    tidelift
    license
    contact

.. toctree::
    :caption: 有用链接
    :hidden:

    pytest @ PyPI <https://pypi.org/project/pytest/>
    pytest @ GitHub <https://github.com/pytest-dev/pytest/>
    Issue Tracker <https://github.com/pytest-dev/pytest/issues>
    PDF 文档 <https://media.readthedocs.org/pdf/pytest/latest/pytest.pdf>

.. module:: pytest

``pytest`` 框架使编写小型、可读的测试变得容易，并且可以扩展以支持应用程序和库的复杂功能测试。


**PyPI 包名称**: :pypi:`pytest`

快速示例
---------------

.. code-block:: python

    # test_sample.py 的内容
    def inc(x):
        return x + 1


    def test_answer():
        assert inc(3) == 5


执行它：

.. code-block:: pytest

    $ pytest
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 1 item

    test_sample.py F                                                     [100%]

    ================================= FAILURES =================================
    _______________________________ test_answer ________________________________

        def test_answer():
    >       assert inc(3) == 5
    E       assert 4 == 5
    E        +  where 4 = inc(3)

    test_sample.py:6: AssertionError
    ========================= short test summary info ==========================
    FAILED test_sample.py::test_answer - assert 4 == 5
    ============================ 1 failed in 0.12s =============================

由于 ``pytest`` 的详细断言内省，仅使用普通的 ``assert`` 语句。
参见 :ref:`开始使用 <getstarted>` 了解使用 pytest 的基本介绍。


特性
--------

- 关于失败的 :ref:`断言语句 <assert>` 的详细信息（无需记住 ``self.assert*`` 名称）

- :ref:`自动发现 <test discovery>` 测试模块和函数

- :ref:`模块化 fixtures <fixture>` 用于管理小型或参数化的长期测试资源

- 可以开箱即用地运行 :ref:`unittest <unittest>` （包括 trial）测试套件

- Python 3.10+ 或 PyPy 3

- 丰富的插件架构，拥有超过 1300+ :ref:`外部插件 <plugin-list>` 和蓬勃发展的社区


文档
-------------

* :ref:`开始使用 <get-started>` - 安装 pytest 并在二十分钟内掌握其基础知识
* :ref:`操作指南 <how-to>` - 分步指南，涵盖广泛的用例和需求
* :ref:`参考指南 <reference>` - 包括完整的 pytest API 参考、插件列表等
* :ref:`解释 <explanation>` - 背景、关键主题讨论、高层次问题的答案


错误/请求
-------------

请使用 `GitHub issue 跟踪器 <https://github.com/pytest-dev/pytest/issues>`_ 提交错误或请求功能。


支持 pytest
--------------

`Open Collective`_ 是一个为开放和透明社区提供的在线筹款平台。
它提供工具来筹集资金并完全透明地分享您的财务状况。

它是希望直接向项目进行一次性或月度捐赠的个人和公司的首选平台。

更多详情请参见 `pytest collective`_.

.. _Open Collective: https://opencollective.com
.. _pytest collective: https://opencollective.com/pytest


pytest 企业版
---------------------

可作为 Tidelift 订阅的一部分使用。

pytest 的维护者和数千个其他软件包的维护者正在与 Tidelift 合作，为您用于构建应用程序的开源依赖项提供商业支持和维护。
节省时间，降低风险，改善代码健康状况，同时为您使用的确切依赖项的维护者付费。

`了解更多。 <https://tidelift.com/subscription/pkg/pypi-pytest?utm_source=pypi-pytest&utm_medium=referral&utm_campaign=enterprise&utm_term=repo>`_

安全
~~~~~~~~

pytest 从未与安全漏洞相关联，但无论如何，要报告安全漏洞，请使用 `Tidelift 安全联系 <https://tidelift.com/security>`_.
Tidelift 将协调修复和披露。

