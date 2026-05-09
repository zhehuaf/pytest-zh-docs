
故障演示和 pytest 报告示例
=================================================

以下是一些失败的测试函数及其相应报告输出的示例，帮助你了解 pytest 报告失败的多种方式。

.. code-block:: pytest

    $ pytest failure_demo.py
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-9.x.y, pluggy-1.x.y
    rootdir: /home/sweet/project
    collected 44 items

    failure_demo.py test_generative[3-6] F
    failure_demo.py test_generative[0-0] .
    failure_demo.py test_generative[1-3] .
    failure_demo.py test_generative[2-6] .
    failure_demo.py TestFailing::test_simple F
    failure_demo.py TestFailing::test_simple_multiline F
    failure_demo.py TestFailing::test_not F
    failure_demo.py TestSpecialisedExplanations::test_eq_text F
    failure_demo.py TestSpecialisedExplanations::test_eq_similar_text F
    failure_demo.py TestSpecialisedExplanations::test_eq_multiline_text F
    failure_demo.py TestSpecialisedExplanations::test_eq_long_text F
    failure_demo.py TestSpecialisedExplanations::test_eq_long_text_multiline F
    failure_demo.py TestSpecialisedExplanations::test_eq_list F
    failure_demo.py TestSpecialisedExplanations::test_eq_list_long F
    failure_demo.py TestSpecialisedExplanations::test_eq_dict F
    failure_demo.py TestSpecialisedExplanations::test_eq_set F
    failure_demo.py TestSpecialisedExplanations::test_eq_longer_list F
    failure_demo.py TestSpecialisedExplanations::test_in_list F
    failure_demo.py TestSpecialisedExplanations::test_not_in_text_multiline F
    failure_demo.py TestSpecialisedExplanations::test_not_in_text_single F
    failure_demo.py TestSpecialisedExplanations::test_not_in_text_single_long F
    failure_demo.py TestSpecialisedExplanations::test_not_in_text_single_long_term F
    failure_demo.py TestSpecialisedExplanations::test_eq_dataclass F
    failure_demo.py TestSpecialisedExplanations::test_eq_attrs F
    failure_demo.py test_attribute F
    failure_demo.py test_attribute_instance F
    failure_demo.py test_attribute_failure F
    failure_demo.py test_attribute_multiple F
    failure_demo.py TestRaises::test_raises F
    failure_demo.py TestRaises::test_raises_doesnt F
    failure_demo.py TestRaises::test_raise F
    failure_demo.py TestRaises::test_tupleerror F
    failure_demo.py TestRaises::test_reinterpret_fails_with_print_for_the_fun_of_it F
    failure_demo.py TestRaises::test_some_error F
    failure_demo.py test_dynamic_compile_shows_nicely F
    failure_demo.py TestMoreErrors::test_complex_error F
    failure_demo.py TestMoreErrors::test_z1_unpack_error F
    failure_demo.py TestMoreErrors::test_z2_type_error F
    failure_demo.py TestMoreErrors::test_startswith F
    failure_demo.py TestMoreErrors::test_startswith_nested F
    failure_demo.py TestMoreErrors::test_global_func F
    failure_demo.py TestMoreErrors::test_instance F
    failure_demo.py TestMoreErrors::test_compare F
    failure_demo.py TestMoreErrors::test_try_finally F
    failure_demo.py TestCustomAssertMsg::test_single_line F
    failure_demo.py TestCustomAssertMsg::test_multiline F
    failure_demo.py TestCustomAssertMsg::test_custom_repr F
    [100%]

    ================================= FAILURES =================================
    ____________________________ test_generative[3-6] ____________________________

        def test_generative(param1):
    >       assert param1 * 2 < 6
    E       assert (3 * 2) < 6

    failure_demo.py:7: AssertionError
    _____________________________ TestFailing.test_simple ___________________________

    self = <failure_demo.TestFailing object at 0xdeadbeef0001>

        def test_simple(self):
    >       assert 42 == 43
    E       assert 42 == 43

    failure_demo.py:14: AssertionError
    _________________________ TestFailing.test_simple_multiline _________________________

    self = <failure_demo.TestFailing object at 0xdeadbeef0002>

        def test_simple_multiline(self):
    >       assert 42 == 43
    E       assert 42 == 43

    failure_demo.py:18: AssertionError
    _______________________________ TestFailing.test_not _______________________________

    self = <failure_demo.TestFailing object at 0xdeadbeef0003>

        def test_not(self):
    >       assert not 42
    E       assert not 42

    failure_demo.py:21: AssertionError
    _______________________ TestSpecialisedExplanations.test_eq_text _______________________

    self = <failure_demo.TestSpecialisedExplanations object at 0xdeadbeef0004>

        def test_eq_text(self):
    >       assert "spam" == "eggs"
    E       AssertionError: assert 'spam' == 'eggs'
    E         - eggs
    E         + spam

    failure_demo.py:24: AssertionError
    _____________________ TestSpecialisedExplanations.test_eq_similar_text _____________________

    self = <failure_demo.TestSpecialisedExplanations object at 0xdeadbeef0005>

        def test_eq_similar_text(self):
    >       assert "foo 1 bar" == "foo 2 bar"
    E       AssertionError: assert 'foo 1 bar' == 'foo 2 bar'
    E         - foo 2 bar
    E         + foo 1 bar
    E         ?     ^

    failure_demo.py:27: AssertionError
    _____________________ TestSpecialisedExplanations.test_eq_multiline_text _____________________

    self = <failure_demo.TestSpecialisedExplanations object at 0xdeadbeef0006>

        def test_eq_multiline_text(self):
    >       assert "foo\nspam\nbar" == "foo\neggs\nbar"
    E       AssertionError: assert 'foo\nspam\nbar' == 'foo\neggs\nbar'
    E         - foo
    E         - eggs
    E         + spam
    E           bar

    failure_demo.py:30: AssertionError
    ______________________ TestSpecialisedExplanations.test_eq_long_text ______________________

    self = <failure_demo.TestSpecialisedExplanations object at 0xdeadbeef0007>

        def test_eq_long_text(self):
            a = "1" * 100 + "a" + "2" * 100
            b = "1" * 100 + "b" + "2" * 100
    >       assert a == b
    E       AssertionError: assert '111111111111...222222222222' == '111111111111...222222222222'
    E         Skipping 90 identical leading characters in diff, use -v to show
    E         Skipping 91 identical trailing characters in diff, use -v to show
    E         - 12
    E         ?  ^
    E         + 1a2
    E         ?  ^

    failure_demo.py:35: AssertionError
    ___________________ TestSpecialisedExplanations.test_eq_long_text_multiline ___________________

    self = <failure_demo.TestSpecialisedExplanations object at 0xdeadbeef0008>

        def test_eq_long_text_multiline(self):
    >       assert "foo\n" + "a" * 60 + "\na\nbar" == "foo\n" + "b" * 60 + "\nb\nbar"
    E       AssertionError: assert 'foo\naaaaaaaa...aa\na\nbar' == 'foo\nbbbbbbbb...bb\nb\nbar'
    E         Common items:
    E           foo
    E         Differing items:
    E         aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    E         bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
    E         Left contains one more item:
    E           a
    E         Right contains one more item:
    E           b
    E         Full diff:
    E           foo
    E         - aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    E         ? ^
    E         + bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
    E         ? ^
    E         - a
    E         + b
    E           bar

    failure_demo.py:38: AssertionError
    ________________________ TestSpecialisedExplanations.test_eq_list ________________________

    self = <failure_demo.TestSpecialisedExplanations object at 0xdeadbeef0009>

        def test_eq_list(self):
    >       assert [0, 1, 2] == [0, 1, 3]
    E       assert [0, 1, 2] == [0, 1, 3]
    E         At index 2 diff: 2 != 3
    E         Use -v to get more diff

    failure_demo.py:41: AssertionError
    ______________________ TestSpecialisedExplanations.test_eq_list_long ______________________

    self = <failure_demo.TestSpecialisedExplanations object at 0xdeadbeef000a>

        def test_eq_list_long(self):
            a = [0] * 100 + [1] + [3] * 100
            b = [0] * 100 + [2] + [3] * 100
    >       assert a == b
    E       assert [0, 0, 0, 0, 0, 0, ...] == [0, 0, 0, 0, 0, 0, ...]
    E         At index 100 diff: 1 != 2
    E         Use -v to get more diff

    failure_demo.py:45: AssertionError
    _______________________ TestSpecialisedExplanations.test_eq_dict _______________________

    self = <failure_demo.TestSpecialisedExplanations object at 0xdeadbeef000b>

        def test_eq_dict(self):
    >       assert {"a": 0, "b": 1} == {"a": 0, "b": 2}
    E       AssertionError: assert {'a': 0, 'b': 1} == {'a': 0, 'b': 2}
    E         Omitting 1 identical items, use -vv to show
    E         Differing items:
    E         {'b': 1} != {'b': 2}
    E         Full diff:
    E         - {'a': 0, 'b': 2}
    E         ?              ^
    E         + {'a': 0, 'b': 1}
    E         ?              ^

    failure_demo.py:48: AssertionError
    _______________________ TestSpecialisedExplanations.test_eq_set _______________________

    self = <failure_demo.TestSpecialisedExplanations object at 0xdeadbeef000c>

        def test_eq_set(self):
    >       assert {0, 10, 11, 12} == {0, 20, 21}
    E       assert {0, 10, 11, 12} == {0, 20, 21}
    E         Extra items in the left set:
    E         10
    E         11
    E         12
    E         Extra items in the right set:
    E         20
    E         21
    E         Use -v to get more diff

    failure_demo.py:51: AssertionError
    ______________________ TestSpecialisedExplanations.test_eq_longer_list ______________________

    self = <failure_demo.TestSpecialisedExplanations object at 0xdeadbeef000d>

        def test_eq_longer_list(self):
    >       assert [1, 2] == [1, 2, 3]
    E       assert [1, 2] == [1, 2, 3]
    E         Right contains one more item: 3
    E         Use -v to get more diff

    failure_demo.py:54: AssertionError
    ________________________ TestSpecialisedExplanations.test_in_list ________________________

    self = <failure_demo.TestSpecialisedExplanations object at 0xdeadbeef000e>

        def test_in_list(self):
    >       assert 1 in [0, 2, 3, 4, 5]
    E       assert 1 in [0, 2, 3, 4, 5]

    failure_demo.py:57: AssertionError
    _____________________ TestSpecialisedExplanations.test_not_in_text_multiline _____________________

    self = <failure_demo.TestSpecialisedExplanations object at 0xdeadbeef000f>

        def test_not_in_text_multiline(self):
            text = "some multiline\ntext\nwhich\nincludes foo\nand a\ntail"
    >       assert "foo" not in text
    E       AssertionError: assert 'foo' not in 'some multil...nand a\ntail'
    E
    E         'foo' is contained here:
    E           some multiline
    E           text
    E           which
    E           includes foo
    E         ?          +++
    E           and a
    E           tail

    failure_demo.py:61: AssertionError
    ______________________ TestSpecialisedExplanations.test_not_in_text_single ______________________

    self = <failure_demo.TestSpecialisedExplanations object at 0xdeadbeef0010>

        def test_not_in_text_single(self):
            text = "single foo line"
    >       assert "foo" not in text
    E       AssertionError: assert 'foo' not in 'single foo line'
    E
    E         'foo' is contained here:
    E           single foo line
    E         ?        +++

    failure_demo.py:65: AssertionError
    ____________________ TestSpecialisedExplanations.test_not_in_text_single_long ____________________

    self = <failure_demo.TestSpecialisedExplanations object at 0xdeadbeef0011>

        def test_not_in_text_single_long(self):
            text = "head " * 50 + "foo " + "tail " * 20
    >       assert "foo" not in text
    E       AssertionError: assert 'foo' not in 'head head h...l tail tail '
    E
    E         'foo' is contained here:
    E           head head foo tail tail tail tail tail tail tail tail tail tail tail tail tail tail tail tail tail tail tail tail
    E         ?           +++

    failure_demo.py:69: AssertionError
    __________________ TestSpecialisedExplanations.test_not_in_text_single_long_term __________________

    self = <failure_demo.TestSpecialisedExplanations object at 0xdeadbeef0012>

        def test_not_in_text_single_long_term(self):
            text = "head " * 50 + "f" * 70 + "tail " * 20
    >       assert "f" * 70 not in text
    E       AssertionError: assert 'fffffffffff...ffffffffffff' not in 'head head h...l tail tail '
    E
    E         'ffffffffffffffffff...fffffffffffffffffff' is contained here:
    E           head head fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffftail tail tail tail tail tail tail tail tail tail tail tail tail tail tail tail tail tail tail tail
    E         ?           ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    failure_demo.py:73: AssertionError
    ________________________ TestSpecialisedExplanations.test_eq_dataclass ________________________

    self = <failure_demo.TestSpecialisedExplanations object at 0xdeadbeef0013>

        def test_eq_dataclass(self):
            from dataclasses import dataclass

            @dataclass
            class Foo:
                a: int
                b: str

            left = Foo(1, "b")
            right = Foo(1, "c")
    >       assert left == right
    E       AssertionError: assert TestSpecialis...oo(a=1, b='b') == TestSpecialis...oo(a=1, b='c')
    E
    E         Omitting 1 identical items, use -vv to show
    E         Differing attributes:
    E         ['b']
    E
    E         Drill down into differing attribute b:
    E           b: 'b' != 'c'
    E           - c
    E           + b

    failure_demo.py:84: AssertionError
    __________________________ TestSpecialisedExplanations.test_eq_attrs __________________________

    self = <failure_demo.TestSpecialisedExplanations object at 0xdeadbeef0014>

        def test_eq_attrs(self):
            import attr

            @attr.s
            class Foo:
                a = attr.ib()
                b = attr.ib()

            left = Foo(1, "b")
            right = Foo(1, "c")
    >       assert left == right
    E       AssertionError: assert Foo(a=1, b='b') == Foo(a=1, b='c')
    E
    E         Omitting 1 identical items, use -vv to show
    E         Differing attributes:
    E         ['b']
    E
    E         Drill down into differing attribute b:
    E           b: 'b' != 'c'
    E           - c
    E           + b

    failure_demo.py:96: AssertionError
    ________________________________ test_attribute ________________________________

        def test_attribute(self):
            class Foo:
                b = 1

            i = Foo()
    >       assert i.b == 2
    E       assert 1 == 2
    E        +  where 1 = <failure_demo.test_attribute.<locals>.Foo object at 0xdeadbeef0015>.b

    failure_demo.py:104: AssertionError
    ____________________________ test_attribute_instance ____________________________

        def test_attribute_instance(self):
            class Foo:
                b = 1

    >       assert Foo().b == 2
    E       AssertionError: assert 1 == 2
    E        +  where 1 = <failure_demo.test_attribute_instance.<locals>.Foo object at 0xdeadbeef0016>.b
    E        +    where <failure_demo.test_attribute_instance.<locals>.Foo object at 0xdeadbeef0016> = <class 'failure_demo.test_attribute_instance.<locals>.Foo'>()

    failure_demo.py:111: AssertionError
    ____________________________ test_attribute_failure ____________________________

        def test_attribute_failure(self):
            class Foo:
                def _get_b(self):
                    raise Exception("Failed to get attrib")

                b = property(_get_b)

            i = Foo()
    >       assert i.b == 2
    E       AssertionError: assert 1 == 2
    E        +  where 1 = <failure_demo.test_attribute_instance.<locals>.Foo object at 0xdeadbeef0016>.b

    failure_demo.py:111: AssertionError
    __________________________ test_attribute_failure __________________________

        def test_attribute_failure(self):
            class Foo:
                def _get_b(self):
                    raise Exception("Failed to get attrib")

                b = property(_get_b)

            i = Foo()
    >       assert i.b == 2
                   ^^^

    failure_demo.py:122:
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    self = <failure_demo.test_attribute_failure.<locals>.Foo object at 0xdeadbeef0017>

        def _get_b(self):
    >       raise Exception("Failed to get attrib")
    E       Exception: Failed to get attrib

    failure_demo.py:117: Exception
    ___________________________ test_attribute_multiple ___________________________

        def test_attribute_multiple(self):
            class Foo:
                b = 1

            class Bar:
                b = 2

    >       assert Foo().b == Bar().b
    E       AssertionError: assert 1 == 2
    E        +  where 1 = <failure_demo.test_attribute_multiple.<locals>.Foo object at 0xdeadbeef0018>.b
    E        +    where <failure_demo.test_attribute_multiple.<locals>.Foo object at 0xdeadbeef0018> = <class 'failure_demo.test_attribute_multiple.<locals>.Foo'>()
    E        +  and   2 = <failure_demo.test_attribute_multiple.<locals>.Bar object at 0xdeadbeef0019>.b
    E        +    where <failure_demo.test_attribute_multiple.<locals>.Bar object at 0xdeadbeef0019> = <class 'failure_demo.test_attribute_multiple.<locals>.Bar'>()

    failure_demo.py:132: AssertionError
    ______________________________ TestRaises.test_raises ______________________________

    self = <failure_demo.TestRaises object at 0xdeadbeef001a>

        def test_raises(self):
            s = "qwe"
    >       raises(TypeError, int, s)
    E       ValueError: invalid literal for int() with base 10: 'qwe'

    failure_demo.py:142: ValueError
    ____________________________ TestRaises.test_raises_doesnt ____________________________

    self = <failure_demo.TestRaises object at 0xdeadbeef001b>

        def test_raises_doesnt(self):
    >       raises(OSError, int, "3")
    E       Failed: DID NOT RAISE <class 'OSError'>

    failure_demo.py:145: Failed
    ______________________________ TestRaises.test_raise ______________________________

    self = <failure_demo.TestRaises object at 0xdeadbeef001c>

        def test_raise(self):
    >       raise ValueError("demo error")
    E       ValueError: demo error

    failure_demo.py:148: ValueError
    ____________________________ TestRaises.test_tupleerror ____________________________

    self = <failure_demo.TestRaises object at 0xdeadbeef001d>

        def test_tupleerror(self):
    >       a, b = [1]  # noqa: F841
    E       ValueError: not enough values to unpack (expected 2, got 1)

    failure_demo.py:151: ValueError
    ________ TestRaises.test_reinterpret_fails_with_print_for_the_fun_of_it ________

    self = <failure_demo.TestRaises object at 0xdeadbeef001e>

        def test_reinterpret_fails_with_print_for_the_fun_of_it(self):
            items = [1, 2, 3]
            print(f"items is {items!r}")
    >       a, b = items.pop()
    E       TypeError: cannot unpack non-iterable int object

    failure_demo.py:156: TypeError
    --------------------------- Captured stdout call ---------------------------
    items is [1, 2, 3]
    ____________________________ TestRaises.test_some_error ____________________________

    self = <failure_demo.TestRaises object at 0xdeadbeef001f>

        def test_some_error(self):
    >       if namenotexi:  # noqa: F821
    E       NameError: name 'namenotexi' is not defined

    failure_demo.py:159: NameError
    ___________________________ test_dynamic_compile_shows_nicely ___________________________

        def test_dynamic_compile_shows_nicely():
            import importlib.util
            import sys

            src = "def foo():\n assert 1 == 0\n"
            name = "abc-123"
            spec = importlib.util.spec_from_loader(name, loader=None)
            module = importlib.util.module_from_spec(spec)
            code = compile(src, name, "exec")
            exec(code, module.__dict__)
            sys.modules[name] = module
    >       module.foo()

    failure_demo.py:178:
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    >   ???
    E   AssertionError

    abc-123:2: AssertionError
    ____________________________ TestMoreErrors.test_complex_error ____________________________

    self = <failure_demo.TestMoreErrors object at 0xdeadbeef0020>

        def test_complex_error(self):
            def f():
                return 44

            def g():
                return 43

    >       somefunc(f(), g())

    failure_demo.py:189:
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
    failure_demo.py:12: in somefunc
        otherfunc(x, y)
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    a = 44, b = 43

        def otherfunc(a, b):
    >       assert a == b
    E       assert 44 == 43

    failure_demo.py:8: AssertionError
    ___________________________ TestMoreErrors.test_z1_unpack_error ___________________________

    self = <failure_demo.TestMoreErrors object at 0xdeadbeef0021>

        def test_z1_unpack_error(self):
            items = []
    >       a, b = items
    E       ValueError: not enough values to unpack (expected 2, got 0)

    failure_demo.py:193: ValueError
    ____________________________ TestMoreErrors.test_z2_type_error ____________________________

    self = <failure_demo.TestMoreErrors object at 0xdeadbeef0022>

        def test_z2_type_error(self):
            items = 3
    >       a, b = items
    E       TypeError: cannot unpack non-iterable int object

    failure_demo.py:197: TypeError
    _____________________________ TestMoreErrors.test_startswith _____________________________

    self = <failure_demo.TestMoreErrors object at 0xdeadbeef0023>

        def test_startswith(self):
            s = "123"
            g = "456"
    >       assert s.startswith(g)
    E       AssertionError: assert False
    E        +  where False = <built-in method startswith of str object at 0xdeadbeef0024>('456')
    E        +    where <built-in method startswith of str object at 0xdeadbeef0024> = '123'.startswith

    failure_demo.py:202: AssertionError
    __________________________ TestMoreErrors.test_startswith_nested __________________________

    self = <failure_demo.TestMoreErrors object at 0xdeadbeef0025>

        def test_startswith_nested(self):
            def f():
                return "123"

            def g():
                return "456"

    >       assert f().startswith(g())
    E       AssertionError: assert False
    E        +  where False = <built-in method startswith of str object at 0xdeadbeef0024>('456')
    E        +    where <built-in method startswith of str object at 0xdeadbeef0024> = '123'.startswith
    E        +      where '123' = <function TestMoreErrors.test_startswith_nested.<locals>.f at 0xdeadbeef0026>()
    E        +    and   '456' = <function TestMoreErrors.test_startswith_nested.<locals>.g at 0xdeadbeef0027>()

    failure_demo.py:211: AssertionError
    _____________________________ TestMoreErrors.test_global_func _____________________________

    self = <failure_demo.TestMoreErrors object at 0xdeadbeef0028>

        def test_global_func(self):
    >       assert isinstance(globf(42), float)
    E       assert False
    E        +  where False = isinstance(43, float)
    E        +    where 43 = globf(42)

    failure_demo.py:214: AssertionError
    ______________________________ TestMoreErrors.test_instance ______________________________

    self = <failure_demo.TestMoreErrors object at 0xdeadbeef0029>

        def test_instance(self):
            self.x = 6 * 7
    >       assert self.x != 42
    E       assert 42 != 42
    E        +  where 42 = <failure_demo.TestMoreErrors object at 0xdeadbeef0029>.x

    failure_demo.py:218: AssertionError
    ______________________________ TestMoreErrors.test_compare ______________________________

    self = <failure_demo.TestMoreErrors object at 0xdeadbeef002a>

        def test_compare(self):
    >       assert globf(10) < 5
    E       assert 11 < 5
    E        +  where 11 = globf(10)

    failure_demo.py:221: AssertionError
    _____________________________ TestMoreErrors.test_try_finally _____________________________

    self = <failure_demo.TestMoreErrors object at 0xdeadbeef002b>

        def test_try_finally(self):
            x = 1
            try:
    >           assert x == 0
    E           assert 1 == 0

    failure_demo.py:226: AssertionError
    __________________________ TestCustomAssertMsg.test_single_line __________________________

    self = <failure_demo.TestCustomAssertMsg object at 0xdeadbeef002c>

        def test_single_line(self):
            class A:
                a = 1

            b = 2
    >       assert A.a == b, "A.a appears not to be b"
    E       AssertionError: A.a appears not to be b
    E       assert 1 == 2
    E        +  where 1 = <class 'failure_demo.TestCustomAssertMsg.test_single_line.<locals>.A'>.a

    failure_demo.py:237: AssertionError
    ___________________________ TestCustomAssertMsg.test_multiline ___________________________

    self = <failure_demo.TestCustomAssertMsg object at 0xdeadbeef002d>

        def test_multiline(self):
            class A:
                a = 1

            b = 2
    >       assert A.a == b, (
                "A.a appears not to be b\nor does not appear to be b\none of those"
            )
    E       AssertionError: A.a appears not to be b
    E         or does not appear to be b
    E         one of those
    E       assert 1 == 2
    E        +  where 1 = <class 'failure_demo.TestCustomAssertMsg.test_multiline.<locals>.A'>.a

    failure_demo.py:244: AssertionError
    __________________________ TestCustomAssertMsg.test_custom_repr __________________________

    self = <failure_demo.TestCustomAssertMsg object at 0xdeadbeef002e>

        def test_custom_repr(self):
            class JSON:
                a = 1

                def __repr__(self):
                    return "This is JSON\n{\n  'foo': 'bar'\n}"

            a = JSON()
            b = 2
    >       assert a.a == b, a
    E       AssertionError: This is JSON
    E         {
    E           'foo': 'bar'
    E         }
    E       assert 1 == 2
    E        +  where 1 = This is JSON\n{\n  'foo': 'bar'\n}.a

    failure_demo.py:257: AssertionError
    ========================= short test summary info ==========================
    FAILED failure_demo.py::test_generative[3-6] - assert (3 * 2) < 6
    FAILED failure_demo.py::TestFailing::test_simple - assert 42 == 43
    FAILED failure_demo.py::TestFailing::test_simple_multiline - assert 42 == 54
    FAILED failure_demo.py::TestFailing::test_not - assert not 42
    FAILED failure_demo.py::TestSpecialisedExplanations::test_eq_text - Asser...
    FAILED failure_demo.py::TestSpecialisedExplanations::test_eq_similar_text
    FAILED failure_demo.py::TestSpecialisedExplanations::test_eq_multiline_text
    FAILED failure_demo.py::TestSpecialisedExplanations::test_eq_long_text - ...
    FAILED failure_demo.py::TestSpecialisedExplanations::test_eq_long_text_multiline
    FAILED failure_demo.py::TestSpecialisedExplanations::test_eq_list - asser...
    FAILED failure_demo.py::TestSpecialisedExplanations::test_eq_list_long - ...
    FAILED failure_demo.py::TestSpecialisedExplanations::test_eq_dict - Asser...
    FAILED failure_demo.py::TestSpecialisedExplanations::test_eq_set - assert...
    FAILED failure_demo.py::TestSpecialisedExplanations::test_eq_longer_list
    FAILED failure_demo.py::TestSpecialisedExplanations::test_in_list - asser...
    FAILED failure_demo.py::TestSpecialisedExplanations::test_not_in_text_multiline
    FAILED failure_demo.py::TestSpecialisedExplanations::test_not_in_text_single
    FAILED failure_demo.py::TestSpecialisedExplanations::test_not_in_text_single_long
    FAILED failure_demo.py::TestSpecialisedExplanations::test_not_in_text_single_long_term
    FAILED failure_demo.py::TestSpecialisedExplanations::test_eq_dataclass - ...
    FAILED failure_demo.py::TestSpecialisedExplanations::test_eq_attrs - Asse...
    FAILED failure_demo.py::test_attribute - assert 1 == 2
    FAILED failure_demo.py::test_attribute_instance - AssertionError: assert ...
    FAILED failure_demo.py::test_attribute_failure - Exception: Failed to get...
    FAILED failure_demo.py::test_attribute_multiple - AssertionError: assert ...
    FAILED failure_demo.py::TestRaises::test_raises - ValueError: invalid lit...
    FAILED failure_demo.py::TestRaises::test_raises_doesnt - Failed: DID NOT ...
    FAILED failure_demo.py::TestRaises::test_raise - ValueError: demo error
    FAILED failure_demo.py::TestRaises::test_tupleerror - ValueError: not eno...
    FAILED failure_demo.py::TestRaises::test_reinterpret_fails_with_print_for_the_fun_of_it
    FAILED failure_demo.py::TestRaises::test_some_error - NameError: name 'na...
    FAILED failure_demo.py::test_dynamic_compile_shows_nicely - AssertionError
    FAILED failure_demo.py::TestMoreErrors::test_complex_error - assert 44 == 43
    FAILED failure_demo.py::TestMoreErrors::test_z1_unpack_error - ValueError...
    FAILED failure_demo.py::TestMoreErrors::test_z2_type_error - TypeError: c...
    FAILED failure_demo.py::TestMoreErrors::test_startswith - AssertionError:...
    FAILED failure_demo.py::TestMoreErrors::test_startswith_nested - Assertio...
    FAILED failure_demo.py::TestMoreErrors::test_global_func - assert False
    FAILED failure_demo.py::TestMoreErrors::test_instance - assert 42 != 42
    FAILED failure_demo.py::TestMoreErrors::test_compare - assert 11 < 5
    FAILED failure_demo.py::TestMoreErrors::test_try_finally - assert 1 == 0
    FAILED failure_demo.py::TestCustomAssertMsg::test_single_line - Assertion...
    FAILED failure_demo.py::TestCustomAssertMsg::test_multiline - AssertionEr...
    FAILED failure_demo.py::TestCustomAssertMsg::test_custom_repr - Assertion...
    ============================ 44 failed in 0.12s ============================

你可以使用 :func:`pytest.raises` 创建一个 :ref:`快速指南 <assertraises>` 来解释异常断言。
