历史
=======

pytest 有着悠久而有趣的历史。这个仓库中的 `第一次提交
<https://github.com/pytest-dev/pytest/commit/5992a8ef21424d7571305a8d7e2a3431ee7e1e23>`__
是在 2007 年 1 月，即使这一次提交本身就说明了问题：该仓库最初来自 :pypi:`py`
库（后来拆分为 pytest），它
最初是 SVN 修订版，迁移到 Mercurial，最后迁移到
git。

然而，该提交说"创建新的开发主干"，而且
已经相当庞大：*435 个文件更改，58640 次插入(+)*。这是因为
pytest 最初是作为 `PyPy <https://www.pypy.org/>`__ 的一部分诞生的，目的是让编写测试变得更简单。以下是从它到成为自己项目的演变过程：


- 2002 年末 / 2003 年初，`PyPy 诞生 <https://morepypy.blogspot.com/2018/09/the-first-15-years-of-pypy.html>`__。
- 正如那篇博客文章提到的，从很早开始就有很大的
  测试重点。在 unittest.py 之上有各种 ``testsupport`` 文件，早在 2003 年 6 月，Holger Krekel (:user:`hpk42`)
  `重构 <https://mail.python.org/pipermail/pypy-dev/2003-June/000787.html>`__
  其测试框架以清理（``pypy.tool.test``，但仍然是
  在 ``unittest.py`` 之上，还没有 pytest 相关的东西）。
- 2003 年 12 月，有 `另一次
  迭代 <https://foss.heptapod.net/pypy/pypy/-/commit/02752373e1b29d89c6bb0a97e5f940caa22bdd63>`__
  在改进他们的测试情况，由 Stefan Schwarzer 完成，称为
  ``pypy.tool.newtest``。
- 然而，它似乎并没有存在多久，因为大约在 2004 年 6 月/7 月
  开始了一项名为 ``utest`` 的工作，提供普通断言。这似乎是类似 pytest 事物的开始，但
  不幸的是，不清楚当时测试运行器的代码在哪里。
  最接近的仍然存在的是 `这个
  文件 <https://foss.heptapod.net/pypy/pypy/-/commit/0735f9ed287ec20950a7dd0a16fc10810d4f6847>`__，
  但那似乎根本不是一个完整的测试运行器。可以看到的是，有 `各种
  努力 <https://foss.heptapod.net/pypy/pypy/-/commits/branch/default?utf8=%E2%9C%93&search=utest>`__
  由 Laura Creighton 和 Samuele Pedroni (:user:`pedronis`) 自动
  将现有测试转换为新的 ``utest`` 框架。
- 大约在同一时间，为 Europython 2004，@hpk42 `开始了一个
  项目 <http://web.archive.org/web/20041020215353/http://codespeak.net/svn/user/hpk/talks/std-talk.txt>`__
  最初称为"std"，旨在成为"互补标准库" - 已经奠定了后来成为
  pytest 的原则：

      - 当前的"电池包含"非常有用，但是

         - 其中一些以非常类似 Java 的风格编写，
            特别是 unittest 框架
         - […]
         - 最好的 API 是不存在的 API

      […]

      - 测试包应该需要尽可能少的样板代码
         并提供很大的灵活性
      - 它应该提供高质量追溯和调试帮助

      […]

      - 首先……忘记有限的"assertXYZ API"，使用
         真实的东西，例如：：

             assert x == y

      - 这在普通 Python 中有效，但你会得到毫无帮助的"断言
         失败"错误，没有任何信息

      - std.utest（魔法！）实际上重新解释断言表达式
         并提供关于底层值的详细信息

- 2004 年 9 月，``py-dev`` 邮件列表诞生，`现在 <https://mail.python.org/pipermail/pytest-dev/>`__ 是 ``pytest-dev``，
  但值得庆幸的是所有原始存档仍然完好无损。

- 大约在 2004 年 9 月/10 月，``std`` 项目 `被重命名
  <https://mail.python.org/pipermail/pypy-dev/2004-September/001565.html>`__ 为
  ``py``，``std.utest`` 变成了 ``py.test``。这也是第一次
  `完整源代码
  <https://foss.heptapod.net/pypy/pypy/-/commit/42cf50c412026028e20acd23d518bd92e623ac11>`__
  似乎可用，大部分 API 今天仍然存在：

   - ``py.path.local``，它正在逐步被淘汰出 pytest（转向
     pathlib），大约在 16-17 年后
   - 集合树的概念，包括 ``Collector``、
     ``FSCollector``、``Directory``、``PyCollector``、``Module``、
     ``Class``
   - 参数如 ``-x`` / ``--exitfirst``、``-l`` /
     ``--showlocals``、``--fulltrace``、``--pdb``、``-S`` /
     ``--nocapture``（今天是 ``-s`` / ``--capture=off``）、
     ``--collectonly``（今天是 ``--collect-only``）

- 同月，``py`` 库 `从 ``PyPy`` 分离
  <https://foss.heptapod.net/pypy/pypy/-/commit/6bdafe9203ad92eb259270b267189141c53bce33>`__

- 有一段时间似乎相当安静，在 2004 年 10 月（将 ``py`` 从 PyPy 移除）到 2007 年 1 月（现在-pytest 仓库中的第一次提交）之间似乎并没有发生太多事情。然而，在邮件列表上有关于功能/想法的各种讨论，并且每
  几个月有一次 :pypi:`几个发布 <py/0.8.0-alpha2/#history>`：

   - 2006 年 3 月：py 0.8.0-alpha2
   - 2007 年 5 月：py 0.9.0
   - 2008 年 3 月：py 0.9.1（在 pytest `中找到的第一个发布
     变更日志 <https://github.com/pytest-dev/pytest/blob/main/doc/en/changelog.rst#091>`__！）
   - 2008 年 8 月：py 0.9.2

- 2009 年 8 月，py 1.0.0 发布，`引入了很多
  基本
  功能 <https://holgerkrekel.net/2009/08/04/pylib-1-0-0-released-the-testing-with-python-innovations-continue/>`__：

   - funcargs/fixtures
   - `插件
     架构 <http://web.archive.org/web/20090629032718/https://codespeak.net/py/dist/test/extend.html>`__
     今天看起来仍然非常相似！
   - 各种 `默认
     插件 <http://web.archive.org/web/20091005181132/https://codespeak.net/py/dist/test/plugin/index.html>`__，
     包括
     `monkeypatch <http://web.archive.org/web/20091012022829/http://codespeak.net/py/dist/test/plugin/how-to/monkeypatch.html>`__

- 甚至在那时，
  `FAQ <http://web.archive.org/web/20091005222413/http://codespeak.net/py/dist/faq.html>`__
  就说：

      显然，[第二个标准库]雄心勃勃，命名可能
      困扰了项目而不是帮助了它。将来某个时候可能会有
      项目名称更改，可能会拆分成不同的项目。

  最终在 2010 年 11 月实现了这一点，当时 pytest 2.0.0 `被
  发布 <https://mail.python.org/pipermail/pytest-dev/2010-November/001687.html>`__
  作为独立于 ``py`` 的包（但仍然称为 ``py.test``）。

- 2016 年 8 月，pytest 3.0.0 :std:ref:`被发布 <release-3.0.0>`，
  将 ``pytest``（而不是 ``py.test``）添加为推荐的
  命令行入口点

由于这段历史，很难回答 pytest 是什么时候开始的。
这取决于什么点应该真正被视为一切的起点。一种
可能的解释是选择 Europython 2004，即大约 2004 年 6 月/7 月。
