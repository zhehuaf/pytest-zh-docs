
.. _bash_completion:

如何设置 bash 补全
=============================

当使用 bash 作为你的 shell 时，``pytest`` 可以使用 argcomplete
(https://kislyuk.github.io/argcomplete/) 进行自动补全。
为此，``argcomplete`` 需要被安装 **并** 启用。

使用以下命令安装 argcomplete：

.. code-block:: bash

    sudo pip install 'argcomplete>=0.5.7'

要全局激活所有启用了 argcomplete 的 Python 应用程序，请运行：

.. code-block:: bash

    sudo activate-global-python-argcomplete

要进行永久（但不是全局）的 ``pytest`` 激活，请使用：

.. code-block:: bash

    register-python-argcomplete pytest >> ~/.bashrc

要仅对 ``pytest`` 进行一次性激活，请使用：

.. code-block:: bash

    eval "$(register-python-argcomplete pytest)"
