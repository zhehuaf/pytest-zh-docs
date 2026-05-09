.. _how-to-fixtures:

如何使用 fixtures
====================

.. seealso:: :ref:`about-fixtures`
.. seealso:: :ref:`Fixtures reference <reference-fixtures>`


"请求" fixtures
---------------------

在基本层面上，测试函数通过将它们声明为参数来请求所需的 fixtures。

当 pytest 运行测试时，它会查看该测试函数签名中的参数，然后搜索与这些参数同名的 fixtures。一旦 pytest 找到它们，它会运行这些 fixtures，捕获它们返回的内容（如果有），然后将这些对象作为参数传递给测试函数。


快速示例
^^^^^^^^^^^^^

.. code-block:: python

    import pytest


    class Fruit:
        def __init__(self, name):
            self.name = name
            self.cubed = False

        def cube(self):
            self.cubed = True


    class FruitSalad:
        def __init__(self, *fruit_bowl):
            self.fruit = fruit_bowl
            self._cube_fruit()

        def _cube_fruit(self):
            for fruit in self.fruit:
                fruit.cube()


    # Arrange
    @pytest.fixture
    def fruit_bowl():
        return [Fruit("apple"), Fruit("banana")]


    def test_fruit_salad(fruit_bowl):
        # Act
        fruit_salad = FruitSalad(*fruit_bowl)

        # Assert
        assert all(fruit.cubed for fruit in fruit_salad.fruit)

在这个例子中，``test_fruit_salad`` "**请求**" ``fruit_bowl``（即 ``def test_fruit_salad(fruit_bowl):``），当 pytest 看到这个时，它会执行 ``fruit_bowl`` fixture 函数，并将它返回的对象作为 ``fruit_bowl`` 参数传递给 ``test_fruit_salad``。

如果我们手动操作，大致会发生以下情况：

.. code-block:: python

    def fruit_bowl():
        return [Fruit("apple"), Fruit("banana")]


    def test_fruit_salad(fruit_bowl):
        # Act
        fruit_salad = FruitSalad(*fruit_bowl)

        # Assert
        assert all(fruit.cubed for fruit in fruit_salad.fruit)


    # Arrange
    bowl = fruit_bowl()
    test_fruit_salad(fruit_bowl=bowl)


Fixtures 可以**请求**其他 fixtures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

pytest 的最大优势之一是其极其灵活的 fixture 系统。它允许我们将测试的复杂需求简化为更简单和有组织的函数，我们只需要让每个函数描述它们所依赖的东西。我们将在后面更详细地讨论这一点，但现在，这里有一个快速示例来演示 fixtures 如何使用其他 fixtures：

.. code-block:: python

    # test_append.py 的内容
    import pytest


    # Arrange
    @pytest.fixture
    def first_entry():
        return "a"


    # Arrange
    @pytest.fixture
    def order(first_entry):
        return [first_entry]


    def test_string(order):
        # Act
        order.append("b")

        # Assert
        assert order == ["a", "b"]


注意这是与上面相同的例子，但变化很小。pytest 中的 fixtures **请求** fixtures 就像测试一样。所有相同的**请求**规则适用于 fixtures，就像适用于测试一样。如果我们手动操作，这个例子会是这样：

.. code-block:: python

    def first_entry():
        return "a"


    def order(first_entry):
        return [first_entry]


    def test_string(order):
        # Act
        order.append("b")

        # Assert
        assert order == ["a", "b"]


    entry = first_entry()
    the_list = order(first_entry=entry)
    test_string(order=the_list)

Fixtures 是可重用的
^^^^^^^^^^^^^^^^^^^^^

使 pytest 的 fixture 系统如此强大的原因之一是，它使我们能够定义一个可以重复使用的通用设置步骤，就像使用普通函数一样。两个不同的测试可以请求相同的 fixture，pytest 会为每个测试提供该 fixture 的自己的结果。

这对于确保测试不受彼此影响非常有用。我们可以使用这个系统来确保每个测试获得自己的新鲜数据批次，并从干净状态开始，从而提供一致、可重复的结果。

这是一个如何派上用场的例子：

.. code-block:: python

    # test_append.py 的内容
    import pytest


    # Arrange
    @pytest.fixture
    def first_entry():
        return "a"


    # Arrange
    @pytest.fixture
    def order(first_entry):
        return [first_entry]


    def test_string(order):
        # Act
        order.append("b")

        # Assert
        assert order == ["a", "b"]


    def test_int(order):
        # Act
        order.append(2)

        # Assert
        assert order == ["a", 2]


这里的每个测试都被给予该 ``list`` 对象的自己的副本，这意味着 ``order`` fixture 被执行两次（``first_entry`` fixture 也是如此）。如果我们手动操作，它会是这样的：

.. code-block:: python

    def first_entry():
        return "a"


    def order(first_entry):
        return [first_entry]


    def test_string(order):
        # Act
        order.append("b")

        # Assert
        assert order == ["a", "b"]


    def test_int(order):
        # Act
        order.append(2)

        # Assert
        assert order == ["a", 2]


    entry = first_entry()
    the_list = order(first_entry=entry)
    test_string(order=the_list)

    entry = first_entry()
    the_list = order(first_entry=entry)
    test_int(order=the_list)

测试/fixture 可以一次**请求**多个 fixture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

测试和 fixtures 不限于一次**请求**单个 fixture。它们可以请求任意多个。这是另一个快速示例来演示：

.. code-block:: python

    # test_append.py 的内容
    import pytest


    # Arrange
    @pytest.fixture
    def first_entry():
        return "a"


    # Arrange
    @pytest.fixture
    def second_entry():
        return 2


    # Arrange
    @pytest.fixture
    def order(first_entry, second_entry):
        return [first_entry, second_entry]


    # Arrange
    @pytest.fixture
    def expected_list():
        return ["a", 2, 3.0]


    def test_string(order, expected_list):
        # Act
        order.append(3.0)

        # Assert
        assert order == expected_list

Fixtures 可以在每个测试中被**请求**多次（返回值被缓存）
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Fixtures 也可以在同一测试期间被**请求**多次，pytest 不会为该测试再次执行它们。这意味着我们可以在依赖它们的多个 fixtures 中**请求**fixtures（甚至在测试本身中再次请求），而这些 fixtures 不会被执行多次。

.. code-block:: python

    # test_append.py 的内容
    import pytest


    # Arrange
    @pytest.fixture
    def first_entry():
        return "a"


    # Arrange
    @pytest.fixture
    def order():
        return []


    # Act
    @pytest.fixture
    def append_first(order, first_entry):
        return order.append(first_entry)


    def test_string_only(append_first, order, first_entry):
        # Assert
        assert order == [first_entry]

如果一个**请求的** fixture 在测试期间每次被**请求**时都会执行一次，那么这个测试将失败，因为 ``append_first`` 和 ``test_string_only`` 都会看到 ``order`` 是一个空列表（即 ``[]``），但是由于 ``order`` 的返回值被缓存（以及执行它可能产生的任何副作用），在第一次调用之后，测试和 ``append_first`` 都引用同一个对象，测试看到了 ``append_first`` 对该对象的影响。

.. _`autouse`:
.. _`autouse fixtures`:

Autouse fixtures（你不必请求的 fixtures）
-----------------------------------------------------

有时你可能希望有一个 fixture（或甚至几个），你知道你所有的测试都会依赖它。"Autouse" fixtures 是一种方便的方式，使所有测试自动**请求**它们。这可以省去很多冗余的**请求**，甚至可以提供更高级的 fixture 用法（稍后会详细介绍）。

我们可以通过向 fixture 的装饰器传递 ``autouse=True`` 来使其成为 autouse fixture。以下是它们如何使用的简单示例：

.. code-block:: python

    # test_append.py 的内容
    import pytest


    @pytest.fixture
    def first_entry():
        return "a"


    @pytest.fixture
    def order(first_entry):
        return []


    @pytest.fixture(autouse=True)
    def append_first(order, first_entry):
        return order.append(first_entry)


    def test_string_only(order, first_entry):
        assert order == [first_entry]


    def test_string_and_int(order, first_entry):
        order.append(2)
        assert order == [first_entry, 2]

在这个例子中，``append_first`` fixture 是一个 autouse fixture。因为它自动发生，两个测试都受它影响，即使两个测试都没有**请求**它。但这并不意味着它们 *不能* 被**请求**；只是它*不是必需的*。

.. _smtpshared:

作用域：在类、模块、包或会话之间共享 fixtures
--------------------------------------------------------------------

.. regendoc:wipe

需要网络访问的 fixtures 依赖于连接性，通常创建起来很耗时。扩展前面的例子，我们可以向 :py:func:`@pytest.fixture <pytest.fixture>` 调用添加 ``scope="module"`` 参数，以使 ``smtp_connection`` fixture 函数（负责创建与预先存在的 SMTP 服务器的连接）仅在每个测试*模块*中调用一次（默认是每个测试*函数*调用一次）。测试模块中的多个测试函数将因此各自收到相同的 ``smtp_connection`` fixture 实例，从而节省时间。``scope`` 的可能值为：``function``、``class``、``module``、``package`` 或 ``session``。

下一个示例将 fixture 函数放入单独的 ``conftest.py`` 文件中，以便目录中的多个测试模块可以访问该 fixture 函数：

.. code-block:: python

    # conftest.py 的内容
    import smtplib

    import pytest


    @pytest.fixture(scope="module")
    def smtp_connection():
        return smtplib.SMTP("smtp.gmail.com", 587, timeout=5)


.. code-block:: python

    # test_module.py 的内容


    def test_ehlo(smtp_connection):
        response, msg = smtp_connection.ehlo()
        assert response == 250
        assert b"smtp.gmail.com" in msg
        assert 0  # for demo purposes


    def test_noop(smtp_connection):
        response, msg = smtp_connection.noop()
        assert response == 250
        assert 0  # for demo purposes

这里，``test_ehlo`` 需要 ``smtp_connection`` fixture 值。pytest 将发现并调用标记为 :py:func:`@pytest.fixture <pytest.fixture>` 的 ``smtp_connection`` fixture 函数。运行测试如下所示：

.. code-block:: pytest

    $ pytest test_module.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 2 items

    test_module.py FF                                                    [100%]

    ================================= FAILURES =================================
    ________________________________ test_ehlo _________________________________

    smtp_connection = <smtplib.SMTP object at 0xdeadbeef0001>

        def test_ehlo(smtp_connection):
            response, msg = smtp_connection.ehlo()
            assert response == 250
            assert b"smtp.gmail.com" in msg
    >       assert 0  # for demo purposes
            ^^^^^^^^
    E       assert 0

    test_module.py:7: AssertionError
    ________________________________ test_noop _________________________________

    smtp_connection = <smtplib.SMTP object at 0xdeadbeef0001>

        def test_noop(smtp_connection):
            response, msg = smtp_connection.noop()
            assert response == 250
    >       assert 0  # for demo purposes
            ^^^^^^^^
    E       assert 0

    test_module.py:13: AssertionError
    ========================= short test summary info ==========================
    FAILED test_module.py::test_ehlo - assert 0
    FAILED test_module.py::test_noop - assert 0
    ============================ 2 failed in 0.12s =============================

你可以看到两个 ``assert 0`` 失败，更重要的是你还可以看到**完全相同的** ``smtp_connection`` 对象被传递到两个测试函数中，因为 pytest 在回溯中显示了传入的参数值。因此，两个使用 ``smtp_connection`` 的测试函数运行起来就像单个测试一样快，因为它们重用相同的实例。

如果你决定想要一个会话范围的 ``smtp_connection`` 实例，你可以简单地声明它：

.. code-block:: python

    @pytest.fixture(scope="session")
    def smtp_connection():
        # 返回的 fixture 值将被共享给所有请求它的测试
        ...


Fixture 作用域
^^^^^^^^^^^^^^

Fixtures 在第一次被测试请求时创建，并根据其 ``scope`` 被销毁：

* ``function``：默认作用域，fixture 在测试结束时销毁。
* ``class``：fixture 在类中最后一个测试的拆卸期间销毁。
* ``module``：fixture 在模块中最后一个测试的拆卸期间销毁。
* ``package``：fixture 在定义 fixture 的包中最后一个测试的拆卸期间销毁，包括其中的子包和子目录。
* ``session``：fixture 在测试会话结束时销毁。

.. note::

    pytest 一次只缓存一个 fixture 实例，这意味着当使用参数化 fixture 时，pytest 可能会在给定作用域内多次调用 fixture。

.. _dynamic scope:

动态作用域
^^^^^^^^^^^^^

.. versionadded:: 5.2

在某些情况下，你可能想要在不更改代码的情况下更改 fixture 的作用域。为此，将一个可调用对象传递给 ``scope``。该可调用对象必须返回一个带有有效作用域的字符串，并且只执行一次 - 在 fixture 定义期间。它将使用两个关键字参数调用 - ``fixture_name`` 作为字符串，``config`` 作为配置对象。

这在处理需要时间来设置的 fixtures（如生成 docker 容器）时特别有用。你可以使用命令行参数来控制生成容器的作用域，以适应不同的环境。请参见下面的示例。

.. code-block:: python

    def determine_scope(fixture_name, config):
        if config.getoption("--keep-containers", None):
            return "session"
        return "function"


    @pytest.fixture(scope=determine_scope)
    def docker_container():
        yield spawn_container()



.. _`finalization`:

拆卸/清理（又称 Fixture 终结）
-------------------------------------------

当我们运行测试时，我们希望确保它们在之后自行清理，这样它们就不会干扰任何其他测试（也这样我们就不会留下一堆测试数据来膨胀系统）。pytest 中的 fixtures 提供了一个非常有用的拆卸系统，允许我们为每个 fixture 定义清理自身所需的特定步骤。

这个系统可以通过两种方式利用。

.. _`yield fixtures`:

1. ``yield`` fixtures（推荐）
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. regendoc: wipe

"Yield" fixtures 使用 ``yield`` 而不是 ``return``。有了这些 fixtures，我们可以运行一些代码并将对象传递回请求的 fixture/测试，就像使用其他 fixtures 一样。唯一的区别是：

1. ``return`` 被替换为 ``yield``。
2. 该 fixture 的任何拆卸代码都放在 ``yield`` *之后*。

一旦 pytest 确定了 fixtures 的线性顺序，它将运行每个 fixture，直到它返回或产生，然后转到列表中的下一个 fixture 执行相同的操作。

测试完成后，pytest 将返回 fixtures 列表，但以*相反的顺序*，对每个产生的 fixture，运行 ``yield`` 语句*之后*的代码。

作为一个简单的例子，考虑这个基本的电子邮件模块：

.. code-block:: python

    # emaillib.py 的内容
    class MailAdminClient:
        def create_user(self):
            return MailUser()

        def delete_user(self, user):
            # do some cleanup
            pass


    class MailUser:
        def __init__(self):
            self.inbox = []

        def send_email(self, email, other):
            other.inbox.append(email)

        def clear_mailbox(self):
            self.inbox.clear()


    class Email:
        def __init__(self, subject, body):
            self.subject = subject
            self.body = body

假设我们想要测试从一个用户向另一个用户发送电子邮件。我们必须首先创建每个用户，然后将电子邮件从一个用户发送到另一个用户，最后断言另一个用户在其收件箱中收到了该消息。如果我们想在测试运行后进行清理，我们可能需要确保在删除该用户之前清空另一个用户的邮箱，否则系统可能会抱怨。

那可能是这样的：

.. code-block:: python

    # test_emaillib.py 的内容
    from emaillib import Email, MailAdminClient

    import pytest


    @pytest.fixture
    def mail_admin():
        return MailAdminClient()


    @pytest.fixture
    def sending_user(mail_admin):
        user = mail_admin.create_user()
        yield user
        mail_admin.delete_user(user)


    @pytest.fixture
    def receiving_user(mail_admin):
        user = mail_admin.create_user()
        yield user
        user.clear_mailbox()
        mail_admin.delete_user(user)


    def test_email_received(sending_user, receiving_user):
        email = Email(subject="Hey!", body="How's it going?")
        sending_user.send_email(email, receiving_user)
        assert email in receiving_user.inbox

因为 ``receiving_user`` 是设置期间最后一个运行的 fixture，所以它是拆卸期间第一个运行的。

即使拆卸端的顺序正确，也不能保证安全清理的风险。这在 :ref:`safe teardowns` 中有更详细的介绍。

.. code-block:: pytest

   $ pytest -q test_emaillib.py
   .                                                                    [100%]
   1 passed in 0.12s

处理 yield fixture 的错误
""""""""""""""""""""""""""""""""""""

如果 yield fixture 在产生之前引发异常，pytest 不会尝试在该 yield fixture 的 ``yield`` 语句之后运行拆卸代码。但是，对于该测试已经成功运行的每个 fixture，pytest 仍将尝试像平常一样拆卸它们。

2. 直接添加终结器
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

虽然 yield fixtures 被认为是更简洁和更直接的选择，但还有另一种选择，那就是直接向测试的 `request-context`_ 对象添加 "finalizer" 函数。它带来了与 yield fixtures 类似的结果，但需要更多的冗长。

为了使用这种方法，我们必须在需要为其添加拆卸代码的 fixture 中请求 `request-context`_ 对象（就像我们请求另一个 fixture 一样），然后将包含该拆卸代码的可调用对象传递给它的 ``addfinalizer`` 方法。

我们必须小心，因为一旦添加了终结器，pytest 就会运行它，即使该 fixture 在添加终结器后引发异常。因此，为了确保我们只在需要时才运行终结器代码，我们只有在 fixture 完成了需要拆卸的操作后才会添加终结器。

以下是使用 ``addfinalizer`` 方法的前一个示例：

.. code-block:: python

    # test_emaillib.py 的内容
    from emaillib import Email, MailAdminClient

    import pytest


    @pytest.fixture
    def mail_admin():
        return MailAdminClient()


    @pytest.fixture
    def sending_user(mail_admin):
        user = mail_admin.create_user()
        yield user
        mail_admin.delete_user(user)


    @pytest.fixture
    def receiving_user(mail_admin, request):
        user = mail_admin.create_user()

        def delete_user():
            mail_admin.delete_user(user)

        request.addfinalizer(delete_user)
        return user


    @pytest.fixture
    def email(sending_user, receiving_user, request):
        _email = Email(subject="Hey!", body="How's it going?")
        sending_user.send_email(_email, receiving_user)

        def empty_mailbox():
            receiving_user.clear_mailbox()

        request.addfinalizer(empty_mailbox)
        return _email


    def test_email_received(receiving_user, email):
        assert email in receiving_user.inbox


它比 yield fixtures 长一点，也更复杂一点，但当你陷入困境时，它确实提供了一些细微差别。

.. code-block:: pytest

   $ pytest -q test_emaillib.py
   .                                                                    [100%]
   1 passed in 0.12s

关于终结器顺序的说明
""""""""""""""""""""""""""""

终结器以先进后出的顺序执行。
对于 yield fixtures，第一个运行的拆卸代码来自最右边的 fixture，即最后一个测试参数。


.. code-block:: python

    # test_finalizers.py 的内容
    import pytest


    def test_bar(fix_w_yield1, fix_w_yield2):
        print("test_bar")


    @pytest.fixture
    def fix_w_yield1():
        yield
        print("after_yield_1")


    @pytest.fixture
    def fix_w_yield2():
        yield
        print("after_yield_2")


.. code-block:: pytest

    $ pytest -s test_finalizers.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 1 item

    test_finalizers.py test_bar
    .after_yield_2
    after_yield_1


    ============================ 1 passed in 0.12s =============================

对于终结器，第一个运行的 fixture 是对 `request.addfinalizer` 的最后一次调用。

.. code-block:: python

    # test_finalizers.py 的内容
    from functools import partial
    import pytest


    @pytest.fixture
    def fix_w_finalizers(request):
        request.addfinalizer(partial(print, "finalizer_2"))
        request.addfinalizer(partial(print, "finalizer_1"))


    def test_bar(fix_w_finalizers):
        print("test_bar")


.. code-block:: pytest

    $ pytest -s test_finalizers.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 1 item

    test_finalizers.py test_bar
    .finalizer_1
    finalizer_2


    ============================ 1 passed in 0.12s =============================

这是因为 yield fixtures 在幕后使用 `addfinalizer`：当 fixture 执行时，`addfinalizer` 注册一个恢复生成器的函数，后者又调用拆卸代码。


.. _`safe teardowns`:

安全拆卸
--------------

pytest 的 fixture 系统*非常*强大，但它仍然由计算机运行，所以它无法弄清楚如何安全地拆卸我们扔给它的所有东西。如果我们不小心，在错误位置的异常可能会留下我们测试中的东西，这可能会导致进一步的问题。

例如，考虑以下测试（基于上面的邮件示例）：

.. code-block:: python

    # test_emaillib.py 的内容
    from emaillib import Email, MailAdminClient

    import pytest


    @pytest.fixture
    def setup():
        mail_admin = MailAdminClient()
        sending_user = mail_admin.create_user()
        receiving_user = mail_admin.create_user()
        email = Email(subject="Hey!", body="How's it going?")
        sending_user.send_email(email, receiving_user)
        yield receiving_user, email
        receiving_user.clear_mailbox()
        mail_admin.delete_user(sending_user)
        mail_admin.delete_user(receiving_user)


    def test_email_received(setup):
        receiving_user, email = setup
        assert email in receiving_user.inbox

这个版本更加紧凑，但也更难阅读，没有非常有描述性的 fixture 名称，而且没有一个 fixtures 可以很容易地重用。

还有一个更严重的问题，那就是如果设置中的任何步骤引发异常，没有一个拆卸代码会运行。

一个选项可能是使用 ``addfinalizer`` 方法而不是 yield fixtures，但这可能会变得相当复杂和难以维护（而且它也不再紧凑了）。

.. code-block:: pytest

   $ pytest -q test_emaillib.py
   .                                                                    [100%]
   1 passed in 0.12s

.. _`safe fixture structure`:

安全的 fixture 结构
^^^^^^^^^^^^^^^^^^^^^^

最安全、最简单的 fixture 结构要求将 fixtures 限制为每个只做一个改变状态的操作，然后将它们与其拆卸代码捆绑在一起，如 :ref:`上面的电子邮件示例 <yield fixtures>` 所示。

状态改变操作失败但仍修改状态的可能性微乎其微，因为大多数这些操作往往是基于`事务 <https://en.wikipedia.org/wiki/Transaction_processing>`_ 的（至少在测试可能留下状态的那个级别）。因此，如果我们确保任何成功的状态改变操作都通过将其移动到单独的 fixture 函数并将其与其他可能失败的状态改变操作分离来进行拆卸，那么我们的测试将最有机会保持它们发现测试环境时的样子。

例如，假设我们有一个带有登录页面的网站，我们可以访问一个可以生成用户的管理 API。对于我们的测试，我们想要：

1. 通过该管理 API 创建用户
2. 使用 Selenium 启动浏览器
3. 转到我们网站的登录页面
4. 以我们创建的用户身份登录
5. 断言他们的名字在着陆页的标题中

我们不希望在系统中留下那个用户，也不希望留下那个浏览器会话运行，所以我们将确保创建这些内容的 fixtures 在之后自行清理。

那可能是这样的：

.. note::

    对于这个示例，某些 fixtures（即 ``base_url`` 和 ``admin_credentials``）暗示存在于其他地方。所以现在，让我们假设它们存在，我们只是没有看它们。

.. code-block:: python

    from uuid import uuid4
    from urllib.parse import urljoin

    from selenium.webdriver import Chrome
    import pytest

    from src.utils.pages import LoginPage, LandingPage
    from src.utils import AdminApiClient
    from src.utils.data_types import User


    @pytest.fixture
    def admin_client(base_url, admin_credentials):
        return AdminApiClient(base_url, **admin_credentials)


    @pytest.fixture
    def user(admin_client):
        _user = User(name="Susan", username=f"testuser-{uuid4()}", password="P4$$word")
        admin_client.create_user(_user)
        yield _user
        admin_client.delete_user(_user)


    @pytest.fixture
    def driver():
        _driver = Chrome()
        yield _driver
        _driver.quit()


    @pytest.fixture
    def login(driver, base_url, user):
        driver.get(urljoin(base_url, "/login"))
        page = LoginPage(driver)
        page.login(user)


    @pytest.fixture
    def landing_page(driver, login):
        return LandingPage(driver)


    def test_name_on_landing_page_after_login(landing_page, user):
        assert landing_page.header == f"Welcome, {user.name}!"

依赖项的排列方式意味着不清楚 ``user`` fixture 是否会在 ``driver`` fixture 之前执行。但没关系，因为那些是原子操作，所以哪个先运行并不重要，因为测试的事件序列仍然是`线性化 <https://en.wikipedia.org/wiki/Linearizability>`_ 的。但*重要的是*，无论哪个先运行，如果其中一个引发异常而另一个不会，都不会留下任何东西。如果 ``driver`` 在 ``user`` 之前执行，而 ``user`` 引发异常，driver 仍会退出，用户从未被创建。如果 ``driver`` 是那个引发异常的，那么 driver 将永远不会启动，用户也永远不会被创建。

.. note:

    虽然 ``user`` fixture 实际上不需要在 ``driver`` fixture 之前发生，但如果我们让 ``driver`` 请求 ``user``，它可能会节省一些时间，以防创建用户引发异常，因为它不会费心尝试启动 driver，这是一个相当昂贵的操作。


安全地运行多个 ``assert`` 语句
---------------------------------------------

有时你可能希望在完成所有这些设置后运行多个断言，这是有意义的，因为在更复杂的系统中，单个操作可以启动多个行为。pytest 有一种方便的方法来处理这个问题，它结合了我们到目前为止所讨论的很多内容。

所需要的只是提升到更大的作用域，然后将 **act** 步骤定义为 autouse fixture，最后确保所有 fixtures 都针对该更高级别的作用域。

让我们从 :ref:`上面的示例 <safe fixture structure>` 中提取一个例子，并对其进行一些调整。假设除了检查标题中的欢迎消息外，我们还想要检查注销按钮和用户个人资料链接。

让我们看看如何构建它，这样我们就可以运行多个断言而不必重复所有这些步骤。

.. note::

    对于这个示例，某些 fixtures（即 ``base_url`` 和 ``admin_credentials``）暗示存在于其他地方。所以现在，让我们假设它们存在，我们只是没有看它们。

.. code-block:: python

    # tests/end_to_end/test_login.py 的内容
    from uuid import uuid4
    from urllib.parse import urljoin

    from selenium.webdriver import Chrome
    import pytest

    from src.utils.pages import LoginPage, LandingPage
    from src.utils import AdminApiClient
    from src.utils.data_types import User


    @pytest.fixture(scope="class")
    def admin_client(base_url, admin_credentials):
        return AdminApiClient(base_url, **admin_credentials)


    @pytest.fixture(scope="class")
    def user(admin_client):
        _user = User(name="Susan", username=f"testuser-{uuid4()}", password="P4$$word")
        admin_client.create_user(_user)
        yield _user
        admin_client.delete_user(_user)


    @pytest.fixture(scope="class")
    def driver():
        _driver = Chrome()
        yield _driver
        _driver.quit()


    @pytest.fixture(scope="class")
    def landing_page(driver, login):
        return LandingPage(driver)


    class TestLandingPageSuccess:
        @pytest.fixture(scope="class", autouse=True)
        def login(self, driver, base_url, user):
            driver.get(urljoin(base_url, "/login"))
            page = LoginPage(driver)
            page.login(user)

        def test_name_in_header(self, landing_page, user):
            assert landing_page.header == f"Welcome, {user.name}!"

        def test_sign_out_button(self, landing_page):
            assert landing_page.sign_out_button.is_displayed()

        def test_profile_link(self, landing_page, user):
            profile_href = urljoin(base_url, f"/profile?id={user.profile_id}")
            assert landing_page.profile_link.get_attribute("href") == profile_href

请注意，这些方法仅在签名中引用 ``self`` 作为一种形式。没有状态绑定到实际的测试类，就像在 ``unittest.TestCase`` 框架中那样。一切都由 pytest fixture 系统管理。

每个方法只需要请求它实际需要的 fixtures，而不必担心顺序。这是因为 **act** fixture 是一个 autouse fixture，它确保所有其他 fixtures 在它之前执行。不需要再进行状态改变，因此测试可以自由地进行尽可能多的非状态改变查询，而不会冒着踩到其他测试脚趾的风险。

``login`` fixture 也在类内部定义，因为模块中的其他测试不都会期望成功登录，而且 **act** 可能需要为另一个测试类稍微不同地处理。例如，如果我们想要围绕提交错误凭据编写另一个测试场景，我们可以通过向测试文件添加如下内容来处理：

.. note:

    假设这个页面对象（即 ``LoginPage``）在尝试登录后识别登录表单上的文本时引发自定义异常 ``BadCredentialsException``。

.. code-block:: python

    class TestLandingPageBadCredentials:
        @pytest.fixture(scope="class")
        def faux_user(self, user):
            _user = deepcopy(user)
            _user.password = "badpass"
            return _user

        def test_raises_bad_credentials_exception(self, login_page, faux_user):
            with pytest.raises(BadCredentialsException):
                login_page.login(faux_user)


.. _`request-context`:

Fixtures 可以内省请求测试上下文
-------------------------------------------------------------

Fixture 函数可以接受 :py:class:`request <_pytest.fixtures.FixtureRequest>` 对象来内省"请求"测试函数、类或模块上下文。进一步扩展前面的 ``smtp_connection`` fixture 示例，让我们从使用我们 fixture 的测试模块中读取一个可选的服务器 URL：

.. code-block:: python

    # conftest.py 的内容
    import smtplib

    import pytest


    @pytest.fixture(scope="module")
    def smtp_connection(request):
        server = getattr(request.module, "smtpserver", "smtp.gmail.com")
        smtp_connection = smtplib.SMTP(server, 587, timeout=5)
        yield smtp_connection
        print(f"finalizing {smtp_connection} ({server})")
        smtp_connection.close()

我们使用 ``request.module`` 属性可选地从测试模块获取 ``smtpserver`` 属性。如果我们只是再次执行，变化不大：

.. code-block:: pytest

    $ pytest -s -q --tb=no test_module.py
    FFfinalizing <smtplib.SMTP object at 0xdeadbeef0002> (smtp.gmail.com)

    ========================= short test summary info ==========================
    FAILED test_module.py::test_ehlo - assert 0
    FAILED test_module.py::test_noop - assert 0
    2 failed in 0.12s

让我们快速创建另一个在其模块命名空间中设置服务器 URL 的测试模块：

.. code-block:: python

    # test_anothersmtp.py 的内容

    smtpserver = "mail.python.org"  # will be read by smtp fixture


    def test_showhelo(smtp_connection):
        assert 0, smtp_connection.helo()

运行它：

.. code-block:: pytest

    $ pytest -qq --tb=short test_anothersmtp.py
    F                                                                    [100%]
    ================================= FAILURES =================================
    ______________________________ test_showhelo _______________________________
    test_anothersmtp.py:6: in test_showhelo
        assert 0, smtp_connection.helo()
    E   AssertionError: (250, b'mail.python.org')
    E   assert 0
    ------------------------- Captured stdout teardown -------------------------
    finalizing <smtplib.SMTP object at 0xdeadbeef0003> (mail.python.org)
    ========================= short test summary info ==========================
    FAILED test_anothersmtp.py::test_showhelo - AssertionError: (250, b'mail....

瞧！``smtp_connection`` fixture 函数从模块命名空间中获取了我们的邮件服务器名称。

.. _`using-markers`:

使用标记将数据传递给 fixtures
-------------------------------------------------------------

使用 :py:class:`request <_pytest.fixtures.FixtureRequest>` 对象，fixture 还可以访问应用于测试函数的标记。这对于将数据从测试传递到 fixture 很有用：

.. code-block:: python

    import pytest


    @pytest.fixture
    def fixt(request):
        marker = request.node.get_closest_marker("fixt_data")
        if marker is None:
            # 以某种方式处理缺失的标记...
            data = None
        else:
            data = marker.args[0]

        # 用数据做一些事情
        return data


    @pytest.mark.fixt_data(42)
    def test_fixt(fixt):
        assert fixt == 42

.. _`fixture-factory`:

Factories as fixtures
-------------------------------------------------------------

"factory as fixture" 模式可以在单个测试中需要多次 fixture 结果的情况下提供帮助。fixture 不直接返回数据，而是返回一个生成数据的函数。然后可以在测试中多次调用此函数。

Factories 可以根据需要有参数：

.. code-block:: python

    @pytest.fixture
    def make_customer_record():
        def _make_customer_record(name):
            return {"name": name, "orders": []}

        return _make_customer_record


    def test_customer_records(make_customer_record):
        customer_1 = make_customer_record("Lisa")
        customer_2 = make_customer_record("Mike")
        customer_3 = make_customer_record("Meredith")

如果 factory 创建的数据需要管理，fixture 可以处理：

.. code-block:: python

    @pytest.fixture
    def make_customer_record():
        created_records = []

        def _make_customer_record(name):
            record = models.Customer(name=name, orders=[])
            created_records.append(record)
            return record

        yield _make_customer_record

        for record in created_records:
            record.destroy()


    def test_customer_records(make_customer_record):
        customer_1 = make_customer_record("Lisa")
        customer_2 = make_customer_record("Mike")
        customer_3 = make_customer_record("Meredith")


.. _`fixture-parametrize`:

参数化 fixtures
-----------------------------------------------------------------

Fixture 函数可以被参数化，在这种情况下它们将被多次调用，每次执行一组依赖测试，即依赖此 fixture 的测试。测试函数通常不需要意识到它们的重新运行。Fixture 参数化有助于为本身可以以多种方式配置的组件编写详尽的功能测试。

扩展前面的示例，我们可以标记 fixture 以创建两个 ``smtp_connection`` fixture 实例，这将导致所有使用该 fixture 的测试运行两次。fixture 函数通过特殊的 :py:class:`request <pytest.FixtureRequest>` 对象访问每个参数：

.. code-block:: python

    # conftest.py 的内容
    import smtplib

    import pytest


    @pytest.fixture(scope="module", params=["smtp.gmail.com", "mail.python.org"])
    def smtp_connection(request):
        smtp_connection = smtplib.SMTP(request.param, 587, timeout=5)
        yield smtp_connection
        print(f"finalizing {smtp_connection}")
        smtp_connection.close()

主要的变化是 ``params`` 的声明与 :py:func:`@pytest.fixture <pytest.fixture>`，一个值的列表，对于每个值，fixture 函数将执行并可以通过 ``request.param`` 访问值。不需要更改测试函数代码。所以让我们再做一次运行：

.. code-block:: pytest

    $ pytest -q test_module.py
    FFFF                                                                 [100%]
    ================================= FAILURES =================================
    ________________________ test_ehlo[smtp.gmail.com] _________________________

    smtp_connection = <smtplib.SMTP object at 0xdeadbeef0004>

        def test_ehlo(smtp_connection):
            response, msg = smtp_connection.ehlo()
            assert response == 250
            assert b"smtp.gmail.com" in msg
    >       assert 0  # for demo purposes
            ^^^^^^^^
    E       assert 0

    test_module.py:7: AssertionError
    ________________________ test_noop[smtp.gmail.com] _________________________

    smtp_connection = <smtplib.SMTP object at 0xdeadbeef0004>

        def test_noop(smtp_connection):
            response, msg = smtp_connection.noop()
            assert response == 250
    >       assert 0  # for demo purposes
            ^^^^^^^^
    E       assert 0

    test_module.py:13: AssertionError
    ________________________ test_ehlo[mail.python.org] ________________________

    smtp_connection = <smtplib.SMTP object at 0xdeadbeef0005>

        def test_ehlo(smtp_connection):
            response, msg = smtp_connection.ehlo()
            assert response == 250
    >       assert b"smtp.gmail.com" in msg
    E       AssertionError: assert b'smtp.gmail.com' in b'mail.python.org\nPIPELINING\nSIZE 51200000\nETRN\nSTARTTLS\nAUTH DIGEST-MD5 NTLM CRAM-MD5\nENHANCEDSTATUSCODES\n8BITMIME\nDSN\nSMTPUTF8\nCHUNKING'

    test_module.py:6: AssertionError
    -------------------------- Captured stdout setup ---------------------------
    finalizing <smtplib.SMTP object at 0xdeadbeef0004>
    ________________________ test_noop[mail.python.org] ________________________

    smtp_connection = <smtplib.SMTP object at 0xdeadbeef0005>

        def test_noop(smtp_connection):
            response, msg = smtp_connection.noop()
            assert response == 250
    >       assert 0  # for demo purposes
            ^^^^^^^^
    E       assert 0

    test_module.py:13: AssertionError
    ------------------------- Captured stdout teardown -------------------------
    finalizing <smtplib.SMTP object at 0xdeadbeef0005>
    ========================= short test summary info ==========================
    FAILED test_module.py::test_ehlo[smtp.gmail.com] - assert 0
    FAILED test_module.py::test_noop[smtp.gmail.com] - assert 0
    FAILED test_module.py::test_ehlo[mail.python.org] - AssertionError: asser...
    FAILED test_module.py::test_noop[mail.python.org] - assert 0
    4 failed in 0.12s

我们看到两个测试函数各自运行了两次，针对不同的 ``smtp_connection`` 实例。还要注意，使用 ``mail.python.org`` 连接时，第二个测试在 ``test_ehlo`` 中失败，因为预期的服务器字符串与实际到达的不同。

pytest 将构建一个字符串，作为参数化 fixture 中每个 fixture 值的测试 ID，例如上面的示例中的 ``test_ehlo[smtp.gmail.com]`` 和 ``test_ehlo[mail.python.org]``。这些 ID 可以与 :option:`-k` 一起使用来选择要运行的特定情况，当一个失败时它们也会识别特定情况。使用 :option:`--collect-only` 运行 pytest 将显示生成的 ID。

数字、字符串、布尔值和 ``None`` 将使用它们在测试 ID 中的通常字符串表示。对于其他对象，pytest 将根据参数名称创建字符串。可以使用 ``ids`` 关键字参数自定义某个 fixture 值的测试 ID 中使用的字符串：

.. code-block:: python

   # test_ids.py 的内容
   import pytest


   @pytest.fixture(params=[0, 1], ids=["spam", "ham"])
   def a(request):
       return request.param


   def test_a(a):
       pass


   def idfn(fixture_value):
       if fixture_value == 0:
           return "eggs"
       else:
           return None


   @pytest.fixture(params=[0, 1], ids=idfn)
   def b(request):
       return request.param


   def test_b(b):
       pass

上面显示了 ``ids`` 如何可以是字符串列表，也可以是函数，该函数将使用 fixture 值调用，然后必须返回要使用的字符串。在后一种情况下，如果函数返回 ``None``，则将使用 pytest 自动生成的 ID。

运行上述测试会产生以下测试 ID：

.. code-block:: pytest

   $ pytest --collect-only
   =========================== test session starts ============================
   platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
   rootdir: /home/sweet/project
   collected 12 items

   <Dir fixtures.rst-234>
     <Module test_anothersmtp.py>
       <Function test_showhelo[smtp.gmail.com]>
       <Function test_showhelo[mail.python.org]>
     <Module test_emaillib.py>
       <Function test_email_received>
     <Module test_finalizers.py>
       <Function test_bar>
     <Module test_ids.py>
       <Function test_a[spam]>
       <Function test_a[ham]>
       <Function test_b[eggs]>
       <Function test_b[1]>
     <Module test_module.py>
       <Function test_ehlo[smtp.gmail.com]>
       <Function test_noop[smtp.gmail.com]>
       <Function test_ehlo[mail.python.org]>
       <Function test_noop[mail.python.org]>

   ======================= 12 tests collected in 0.12s ========================

.. _`fixture-parametrize-marks`:

在参数化 fixtures 中使用标记
--------------------------------------

:func:`pytest.param` 可用于在参数化 fixtures 的值集中应用标记，方式与 :ref:`@pytest.mark.parametrize <@pytest.mark.parametrize>` 中使用的相同。

示例：

.. code-block:: python

    # test_fixture_marks.py 的内容
    import pytest


    @pytest.fixture(params=[0, 1, pytest.param(2, marks=pytest.mark.skip)])
    def data_set(request):
        return request.param


    def test_data(data_set):
        pass

运行此测试将跳过值为 ``2`` 的 ``data_set`` 调用：

.. code-block:: pytest

    $ pytest test_fixture_marks.py -v
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y -- $PYTHON_PREFIX/bin/python
    cachedir: .pytest_cache
    rootdir: /home/sweet/project
    collecting ... collected 3 items

    test_fixture_marks.py::test_data[0] PASSED                           [ 33%]
    test_fixture_marks.py::test_data[1] PASSED                           [ 66%]
    test_fixture_marks.py::test_data[2] SKIPPED (unconditional skip)     [100%]

    ======================= 2 passed, 1 skipped in 0.12s =======================

.. _`interdependent fixtures`:

模块化：在 fixture 函数中使用 fixtures
----------------------------------------------------------

除了在测试函数中使用 fixtures，fixture 函数本身也可以使用其他 fixtures。这有助于 fixtures 的模块化设计，并允许在许多项目中重用框架特定的 fixtures。作为一个简单的例子，我们可以扩展前面的示例，并实例化一个 ``app`` 对象，将已定义的 ``smtp_connection`` 资源放入其中：

.. code-block:: python

    # test_appsetup.py 的内容

    import pytest


    class App:
        def __init__(self, smtp_connection):
            self.smtp_connection = smtp_connection


    @pytest.fixture(scope="module")
    def app(smtp_connection):
        return App(smtp_connection)


    def test_smtp_connection_exists(app):
        assert app.smtp_connection

这里我们声明了一个接收先前定义的 ``smtp_connection`` fixture 并实例化一个带有它的 ``App`` 对象的 ``app`` fixture。让我们运行它：

.. code-block:: pytest

    $ pytest -v test_appsetup.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y -- $PYTHON_PREFIX/bin/python
    cachedir: .pytest_cache
    rootdir: /home/sweet/project
    collecting ... collected 2 items

    test_appsetup.py::test_smtp_connection_exists[smtp.gmail.com] PASSED [ 50%]
    test_appsetup.py::test_smtp_connection_exists[mail.python.org] PASSED [100%]

    ============================ 2 passed in 0.12s =============================

由于 ``smtp_connection`` 的参数化，测试将使用两个不同的 ``App`` 实例和各自的 smtp 服务器运行两次。``app`` fixture 不需要知道 ``smtp_connection`` 参数化，因为 pytest 将完全分析 fixture 依赖图。

请注意，``app`` fixture 的作用域为 ``module``，并使用模块范围的 ``smtp_connection`` fixture。如果 ``smtp_connection`` 在 ``session`` 范围内缓存，示例仍然可以工作：fixtures 可以使用"更广泛"作用域的 fixtures，但反过来不行：会话范围的 fixture 不能以有意义的方式使用模块范围的 fixture。


.. _`automatic per-resource grouping`:

按 fixture 实例自动分组测试
----------------------------------------------------------

.. regendoc: wipe

pytest 在测试运行期间最小化活动 fixtures 的数量。如果你有一个参数化 fixture，那么所有使用它的测试将首先用一个实例执行，然后在创建下一个 fixture 实例之前调用终结器。除其他事项外，这简化了创建和使用全局状态的应用程序的测试。

以下示例使用两个参数化 fixtures，其中一个基于每个模块的范围，所有函数都执行 ``print`` 调用来显示设置/拆卸流程：

.. code-block:: python

    # test_module.py 的内容
    import pytest


    @pytest.fixture(scope="module", params=["mod1", "mod2"])
    def modarg(request):
        param = request.param
        print("  SETUP modarg", param)
        yield param
        print("  TEARDOWN modarg", param)


    @pytest.fixture(scope="function", params=[1, 2])
    def otherarg(request):
        param = request.param
        print("  SETUP otherarg", param)
        yield param
        print("  TEARDOWN otherarg", param)


    def test_0(otherarg):
        print("  RUN test0 with otherarg", otherarg)


    def test_1(modarg):
        print("  RUN test1 with modarg", modarg)


    def test_2(otherarg, modarg):
        print(f"  RUN test2 with otherarg {otherarg} and modarg {modarg}")

让我们在详细模式下运行测试，并查看 print 输出：

.. code-block:: pytest

    $ pytest -v -s test_module.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y -- $PYTHON_PREFIX/bin/python
    cachedir: .pytest_cache
    rootdir: /home/sweet/project
    collecting ... collected 8 items

    test_module.py::test_0[1]   SETUP otherarg 1
      RUN test0 with otherarg 1
    PASSED  TEARDOWN otherarg 1

    test_module.py::test_0[2]   SETUP otherarg 2
      RUN test0 with otherarg 2
    PASSED  TEARDOWN otherarg 2

    test_module.py::test_1[mod1]   SETUP modarg mod1
      RUN test1 with modarg mod1
    PASSED
    test_module.py::test_2[mod1-1]   SETUP otherarg 1
      RUN test2 with otherarg 1 and modarg mod1
    PASSED  TEARDOWN otherarg 1

    test_module.py::test_2[mod1-2]   SETUP otherarg 2
      RUN test2 with otherarg 2 and modarg mod1
    PASSED  TEARDOWN otherarg 2

    test_module.py::test_1[mod2]   TEARDOWN modarg mod1
      SETUP modarg mod2
      RUN test1 with modarg mod2
    PASSED
    test_module.py::test_2[mod2-1]   SETUP otherarg 1
      RUN test2 with otherarg 1 and modarg mod2
    PASSED  TEARDOWN otherarg 1

    test_module.py::test_2[mod2-2]   SETUP otherarg 2
      RUN test2 with otherarg 2 and modarg mod2
    PASSED  TEARDOWN otherarg 2
      TEARDOWN modarg mod2


    ============================ 8 passed in 0.12s =============================

你可以看到，参数化的模块范围 ``modarg`` 资源导致了测试执行的排序，从而导致了尽可能少的"活动"资源。``mod1`` 参数化资源的终结器在 ``mod2`` 资源设置之前执行。

特别注意，test_0 完全独立，首先完成。然后 test_1 使用 ``mod1`` 执行，然后 test_2 使用 ``mod1``，然后 test_1 使用 ``mod2``，最后 test_2 使用 ``mod2``。

``otherarg`` 参数化资源（具有函数作用域）在每个使用它的测试之前设置，之后拆卸。


.. _`usefixtures`:

在类和模块中使用 fixtures，使用 ``usefixtures``
--------------------------------------------------------

.. regendoc:wipe

有时测试函数不需要直接访问 fixture 对象。例如，测试可能需要以空目录作为当前工作目录运行，但除此之外不关心具体的目录。以下是如何使用标准 :mod:`tempfile` 和 pytest fixtures 来实现它。我们将 fixture 的创建分离到 :file:`conftest.py` 文件中：

.. code-block:: python

    # conftest.py 的内容

    import os
    import tempfile

    import pytest


    @pytest.fixture
    def cleandir():
        with tempfile.TemporaryDirectory() as newpath:
            old_cwd = os.getcwd()
            os.chdir(newpath)
            yield
            os.chdir(old_cwd)

并通过 ``usefixtures`` 标记在测试模块中声明其使用：

.. code-block:: python

    # test_setenv.py 的内容
    import os

    import pytest


    @pytest.mark.usefixtures("cleandir")
    class TestDirectoryInit:
        def test_cwd_starts_empty(self):
            assert os.listdir(os.getcwd()) == []
            with open("myfile", "w", encoding="utf-8") as f:
                f.write("hello")

        def test_cwd_again_starts_empty(self):
            assert os.listdir(os.getcwd()) == []

由于 ``usefixtures`` 标记，``cleandir`` fixture 将为每个测试方法的执行而请求，就像你向每个方法指定了 "cleandir" 函数参数一样。让我们运行它以验证我们的 fixture 已激活并且测试通过：

.. code-block:: pytest

    $ pytest -q
    ..                                                                   [100%]
    2 passed in 0.12s

你可以像这样指定多个 fixtures：

.. code-block:: python

    @pytest.mark.usefixtures("cleandir", "anotherfixture")
    def test(): ...

你也可以使用 :globalvar:`pytestmark` 在测试模块级别指定 fixture 用法：

.. code-block:: python

    pytestmark = pytest.mark.usefixtures("cleandir")


也可以将项目中所有测试所需的 fixtures 放入配置文件中：

.. code-block:: toml

    # pytest.toml 的内容
    [pytest]
    usefixtures = ["cleandir"]

.. warning::

    ``@pytest.mark.usefixtures`` 不能在 **fixture 函数**\上使用。例如，这是一个错误：

    .. code-block:: python

        @pytest.mark.usefixtures("my_other_fixture")
        @pytest.fixture
        def my_fixture_that_sadly_wont_use_my_other_fixture(): ...

.. _`override fixtures`:

在各个级别覆盖 fixtures
-------------------------------------

在相对较大的测试套件中，你可能想要*覆盖*一个 fixture，以在特定测试模块或目录内增强或更改其行为。

在目录（conftest）级别覆盖 fixture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

给定测试文件结构如下：

::

    tests/
        conftest.py
            # tests/conftest.py 的内容
            import pytest

            @pytest.fixture
            def username():
                return 'username'

        test_something.py
            # tests/test_something.py 的内容
            def test_username(username):
                assert username == 'username'

        subdir/
            conftest.py
                # tests/subdir/conftest.py 的内容
                import pytest

                @pytest.fixture
                def username(username):
                    return 'overridden-' + username

            test_something_else.py
                # tests/subdir/test_something_else.py 的内容
                def test_username(username):
                    assert username == 'overridden-username'

正如你所见，可以在特定测试目录级别覆盖具有相同名称的 fixture。请注意，可以在 ``覆盖`` fixture 中轻松访问 ``基础`` 或 ``超级`` fixture - 在上面的示例中使用。

在测试模块级别覆盖 fixture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

给定测试文件结构如下：

::

    tests/
        conftest.py
            # tests/conftest.py 的内容
            import pytest

            @pytest.fixture
            def username():
                return 'username'

        test_something.py
            # tests/test_something.py 的内容
            import pytest

            @pytest.fixture
            def username(username):
                return 'overridden-' + username

            def test_username(username):
                assert username == 'overridden-username'

        test_something_else.py
            # tests/test_something_else.py 的内容
            import pytest

            @pytest.fixture
            def username(username):
                return 'overridden-else-' + username

            def test_username(username):
                assert username == 'overridden-else-username'

在上面的示例中，可以在特定测试模块中覆盖具有相同名称的 fixture。

使用直接测试参数化覆盖 fixture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

给定测试文件结构如下：

::

    tests/
        conftest.py
            # tests/conftest.py 的内容
            import pytest

            @pytest.fixture
            def username():
                return 'username'

            @pytest.fixture
            def other_username(username):
                return 'other-' + username

        test_something.py
            # tests/test_something.py 的内容
            import pytest

            @pytest.mark.parametrize('username', ['directly-overridden-username'])
            def test_username(username):
                assert username == 'directly-overridden-username'

            @pytest.mark.parametrize('username', ['directly-overridden-username-other'])
            def test_username_other(other_username):
                assert other_username == 'other-directly-overridden-username-other'

在上面的示例中，fixture 值被测试参数值覆盖。请注意，即使测试没有直接使用它（在函数原型中没有提到它），也可以用这种方式覆盖 fixture 的值。

使用非参数化 fixture 覆盖参数化 fixture，反之亦然
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

给定测试文件结构如下：

::

    tests/
        conftest.py
            # tests/conftest.py 的内容
            import pytest

            @pytest.fixture(params=['one', 'two', 'three'])
            def parametrized_username(request):
                return request.param

            @pytest.fixture
            def non_parametrized_username(request):
                return 'username'

        test_something.py
            # tests/test_something.py 的内容
            import pytest

            @pytest.fixture
            def parametrized_username():
                return 'overridden-username'

            @pytest.fixture(params=['one', 'two', 'three'])
            def non_parametrized_username(request):
                return request.param

            def test_username(parametrized_username):
                assert parametrized_username == 'overridden-username'

            def test_parametrized_username(non_parametrized_username):
                assert non_parametrized_username in ['one', 'two', 'three']

        test_something_else.py
            # tests/test_something_else.py 的内容
            def test_username(parametrized_username):
                assert parametrized_username in ['one', 'two', 'three']

            def test_username(non_parametrized_username):
                assert non_parametrized_username == 'username'

在上面的示例中，参数化 fixture 被非参数化版本覆盖，非参数化 fixture 被特定测试模块的参数化版本覆盖。显然，这也适用于测试目录级别。


使用其他项目的 fixtures
----------------------------------

通常提供 pytest 支持的项目将使用 :ref:`entry points <pip-installable plugins>`，因此只需将这些项目安装到环境中就会使这些 fixtures 可供使用。

如果你想使用不使用 entry points 的项目的 fixtures，你可以在你的顶层 ``conftest.py`` 文件中定义 :globalvar:`pytest_plugins` 以将该模块注册为插件。

假设你有一些 fixtures 在 ``mylibrary.fixtures`` 中，你想要在你的 ``app/tests`` 目录中重用它们。

你所需要做的就是在 ``app/tests/conftest.py`` 中定义 :globalvar:`pytest_plugins`，指向该模块。

.. code-block:: python

    pytest_plugins = "mylibrary.fixtures"

这有效地将 ``mylibrary.fixtures`` 注册为插件，使其所有 fixtures 和 hooks 在 ``app/tests`` 中的测试中可用。

.. note::

    有时用户会从其他项目*导入* fixtures 以供使用，但这不是推荐的：将 fixtures 导入模块会将它们在 pytest 中注册为在该模块中*定义*。

    这会产生轻微的后果，例如在 ``pytest --help`` 中多次出现，但**不推荐**是因为此行为可能会在未来的版本中更改/停止工作。
