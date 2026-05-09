
Flaky 测试
-----------

"Flaky" 测试是指表现出间歇性或偶发性失败的测试，似乎具有非确定性行为。有时通过，有时失败，原因不明。本页面讨论可以帮助的 pytest 功能以及用于识别、修复或缓解它们的其他一般策略。

Flaky 测试为什么是个问题
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

当使用持续集成（CI）服务器时，Flaky 测试特别麻烦，因为所有测试必须在新的代码更改被合并之前通过。如果测试结果不是一个可靠的信号——即测试失败意味着代码更改破坏了测试——开发人员可能会对测试结果失去信任，这可能导致忽视真正的失败。这也是浪费时间的一个来源，因为开发人员必须重新运行测试套件并调查虚假失败。


潜在的根本原因
^^^^^^^^^^^^^^^^^^^^^

系统状态
~~~~~~~~~~~~

广义上讲，flaky 测试表明测试依赖于某个没有被适当控制的系统状态——测试环境没有得到充分隔离。高级别测试更可能是 flaky 的，因为它们依赖于更多状态。

当测试套件并行运行时（例如使用 `pytest-xdist`_），flaky 测试有时会出现。这可能表明测试依赖于测试顺序。

-  也许另一个测试未能清理自己并留下导致 flaky 测试失败的数据。
- flaky 测试依赖于前一个测试的数据，而那个测试没有清理自己，在并行运行中前一个测试并不总是存在
- 修改全局状态的测试通常不能并行运行。


过于严格的断言
~~~~~~~~~~~~~~~~~~~~~~~

过于严格的断言可能导致浮点数比较以及时序问题。:func:`pytest.approx` 在这里很有用。

线程安全
~~~~~~~~~~~~~

pytest 是单线程的，总是在同一线程中顺序执行其测试，从不自己生成任何线程。

即使在并行运行测试的插件的情况下，例如 `pytest-xdist`_，通常也是通过生成多个 *进程* 并分批运行测试，而不使用多线程。

当然，测试和 fixtures 可以自己生成线程作为其测试工作流的一部分（例如，一个在后台启动服务器线程的 fixture，或一个执行生成线程的生产代码的测试），但必须小心：

* 确保最终等待任何生成的线程——例如在测试结束时，或在 fixture 的拆卸期间。
* 避免从多个线程使用 pytest 提供的原语（:func:`pytest.warns`, :func:`pytest.raises` 等），因为它们不是线程安全的。

如果你的测试套件使用线程并且你看到 flaky 测试结果，不要忽视测试隐式使用 pytest 本身中的全局状态的可能性。

相关功能
^^^^^^^^^^^^^^^^

Xfail strict
~~~~~~~~~~~~

可以使用 ``strict=False`` 的 :ref:`pytest.mark.xfail ref` 来标记测试，使其失败不会导致整个构建中断。这可以被视为一种手动隔离，永久使用相当危险。


PYTEST_CURRENT_TEST
~~~~~~~~~~~~~~~~~~~

:envvar:`PYTEST_CURRENT_TEST` 可能有助于找出"哪个测试卡住了"。
更多详情请参见 :ref:`pytest current test env`。


插件
~~~~~~~

重新运行任何失败的测试可以通过给它们额外的通过机会来缓解 flaky 测试的负面影响，这样整体构建就不会失败。有几个 pytest 插件支持这一点：

* `pytest-rerunfailures <https://github.com/pytest-dev/pytest-rerunfailures>`_
* `pytest-replay <https://github.com/ESSS/pytest-replay>`_: 这个插件帮助在本地重现 CI 运行期间观察到的崩溃或 flaky 测试。
* `pytest-flakefinder <https://github.com/dropbox/pytest-flakefinder>`_ - `博客文章 <https://blogs.dropbox.com/tech/2016/03/open-sourcing-pytest-tools/>`_

故意随机化测试的插件可以帮助暴露有状态问题的测试：

* `pytest-random-order <https://github.com/jbasko/pytest-random-order>`_
* `pytest-randomly <https://github.com/pytest-dev/pytest-randomly>`_



其他一般策略
^^^^^^^^^^^^^^^^^^^^^^^^

拆分测试套件
~~~~~~~~~~~~~~~~~~~~

将单个测试套件拆分为两个（如单元测试 vs 集成测试）并仅使用单元测试套件作为 CI 门是很常见的。这也有助于保持构建时间可控，因为高级别测试往往较慢。然而，这意味着可能合并破坏构建的代码，因此需要格外警惕以监控集成测试结果。


失败时的视频/截图
~~~~~~~~~~~~~~~~~~~~~~~~~~~

对于 UI 测试，这些对于理解测试失败时 UI 的状态很重要。pytest-splinter 可以与 pytest-bdd 等插件一起使用，并能 `在测试失败时保存截图 <https://pytest-splinter.readthedocs.io/en/latest/#automatic-screenshots-on-test-failure>`_，这有助于隔离原因。


删除或重写测试
~~~~~~~~~~~~~~~~~~~~~~~~~~

如果功能被其他测试覆盖，也许可以删除该测试。如果没有，也许可以在较低级别重写它，这将消除 flakiness 或使其来源更明显。


隔离
~~~~~~~~~~

Mark Lapierre 在 2018 年的一篇文章中讨论了 `隔离测试的利与弊 <https://dev.to/mlapierre/pros-and-cons-of-quarantined-tests-2emj>`_。


失败时重新运行的 CI 工具
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Azure Pipelines（Azure 云 CI/CD 工具，前身为 Visual Studio Team Services 或 VSTS）具有 `识别 flaky 测试 <https://docs.microsoft.com/en-us/previous-versions/azure/devops/2017/dec-11-vsts?view=tfs-2017#identify-flaky-tests>`_ 和重新运行失败测试的功能。



研究
^^^^^^^^

这是一个有限的列表，请提交 issue 或 pull request 来扩展它！

* Gao, Zebao, Yalan Liang, Myra B. Cohen, Atif M. Memon, and Zhen Wang. "Making system user interactive tests repeatable: When and what should we control?." In *Software Engineering (ICSE), 2015 IEEE/ACM 37th IEEE International Conference on*, vol. 1, pp. 55-65. IEEE, 2015.  `PDF <http://www.cs.umd.edu/~atif/pubs/gao-icse15.pdf>`__
* Palomba, Fabio, and Andy Zaidman. "Does refactoring of test smells induce fixing flaky tests?." In *Software Maintenance and Evolution (ICSME), 2017 IEEE International Conference on*, pp. 1-12. IEEE, 2017. `PDF in Google Drive <https://drive.google.com/file/d/10HdcCQiuQVgW3yYUJD-TSTq1NbYEprl0/view>`__
* Bell, Jonathan, Owolabi Legunsen, Michael Hilton, Lamyaa Eloussi, Tifany Yung, and Darko Marinov. "DeFlaker: Automatically detecting flaky tests." In *Proceedings of the 2018 International Conference on Software Engineering*. 2018. `PDF <https://www.jonbell.net/icse18-deflaker.pdf#section-Research>`__
* Dutta, Saikat and Shi, August and Choudhary, Rutvik and Zhang, Zhekun and Jain, Aryaman and Misailovic, Sasa. "Detecting flaky tests in probabilistic and machine learning applications." In *Proceedings of the 29th ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA)*, pp. 211-224. ACM, 2020. `PDF <https://www.cs.cornell.edu/~saikatd/papers/flash-issta20.pdf>`__
* Habchi, Sarra and Haben, Guillaume and Sohn, Jeongju and Franci, Adriano and Papadakis, Mike and Cordy, Maxime and Le Traon, Yves. "What Made This Test Flake? Pinpointing Classes Responsible for Test Flakiness." In Proceedings of the 38th IEEE International Conference on Software Maintenance and Evolution (ICSME), IEEE, 2022. `PDF <https://arxiv.org/abs/2207.10143>`__
* Lamprou, Sokrates. "Non-deterministic tests and where to find them: Empirically investigating the relationship between flaky tests and test smells by examining test order dependency." Bachelor thesis, Department of Computer and Information Science, Linköping University, 2022. LIU-IDA/LITH-EX-G–19/056–SE. `PDF <https://www.diva-portal.org/smash/get/diva2:1713691/FULLTEXT01.pdf>`__
* Leinen, Fabian and Elsner, Daniel and Pretschner, Alexander and Stahlbauer, Andreas and Sailer, Michael and Jürgens, Elmar. "Cost of Flaky Tests in Continuous Integration: An Industrial Case Study." Technical University of Munich and CQSE GmbH, Munich, Germany, 2023. `PDF <https://mediatum.ub.tum.de/doc/1730194/1730194.pdf>`__

资源
^^^^^^^^^

* `消除测试中的非确定性 <https://martinfowler.com/articles/nonDeterminism.html>`_ by Martin Fowler, 2011
* `Go 团队不再有 flaky 测试 <https://www.thoughtworks.com/insights/blog/no-more-flaky-tests-go-team>`_ by Pavan Sudarshan, 2012
* `哭泣的构建：在你的持续集成测试中建立信任 <https://www.youtube.com/embed/VotJqV4n8ig>`_ talk (video) by `Angie Jones <https://angiejones.tech/>`_ at SeleniumConf Austin 2017
* `Test and Code Podcast: Flaky Tests and How to Deal with Them <https://testandcode.com/50>`_ by Brian Okken and Anthony Shaw, 2018
* Microsoft:

  * `我们如何测试 VSTS 以实现持续交付 <https://blogs.msdn.microsoft.com/bharry/2017/06/28/testing-in-a-cloud-delivery-cadence/>`_ by Brian Harry MS, 2017
  * `消除 Flaky 测试 <https://docs.microsoft.com/en-us/azure/devops/learn/devops-at-microsoft/eliminating-flaky-tests>`_ blog and talk (video) by Munil Shah, 2017

* Google:

  * `Google 的 Flaky 测试及我们如何缓解它们 <https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html>`_ by John Micco, 2016
  * `Google 的 flaky 测试从何而来？ <https://testing.googleblog.com/2017/04/where-do-our-flaky-tests-come-from.html>`_  by Jeff Listfield, 2017

* Dropbox:
  * `Athena: 我们的自动化构建健康管理系统 <https://dropbox.tech/infrastructure/athena-our-automated-build-health-management-system>`_ by Utsav Shah, 2019
  * `如何管理 CI 工作流中的 Flaky 测试 <https://mill-build.org/blog/4-flaky-tests.html>`_ by Li Haoyi, 2025

* Uber:
  * `在 Java 中处理 Flaky 单元测试 <https://www.uber.com/blog/handling-flaky-tests-java/>`_ by Uber Engineering, 2021
  * `Uber 的 Flaky 测试大改革 <https://www.uber.com/blog/flaky-tests-overhaul/>`_ by Uber Engineering, 2024

.. _pytest-xdist: https://github.com/pytest-dev/pytest-xdist
