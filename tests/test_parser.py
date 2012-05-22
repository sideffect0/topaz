from rupypy import ast

from .base import BaseRuPyPyTest


class TestParser(BaseRuPyPyTest):
    def test_int_constant(self, ec):
        assert ec.space.parse(ec, "1") == ast.Main(ast.Block([
            ast.Statement(ast.ConstantInt(1))
        ]))
        assert ec.space.parse(ec, "-1") == ast.Main(ast.Block([
            ast.Statement(ast.ConstantInt(-1))
        ]))

    def test_float(self, ec):
        assert ec.space.parse(ec, "0.2") == ast.Main(ast.Block([
            ast.Statement(ast.ConstantFloat(0.2))
        ]))

    def test_binary_expression(self, ec):
        assert ec.space.parse(ec, "1+1") == ast.Main(ast.Block([
            ast.Statement(ast.BinOp("+", ast.ConstantInt(1), ast.ConstantInt(1), 1))
        ]))
        assert ec.space.parse(ec, "1/1") == ast.Main(ast.Block([
            ast.Statement(ast.BinOp("/", ast.ConstantInt(1), ast.ConstantInt(1), 1))
        ]))
        assert ec.space.parse(ec, "1===1") == ast.Main(ast.Block([
            ast.Statement(ast.BinOp("===", ast.ConstantInt(1), ast.ConstantInt(1), 1))
        ]))

    def test_multi_term_expr(self, ec):
        assert ec.space.parse(ec, "1 + 2 * 3") == ast.Main(ast.Block([
            ast.Statement(ast.BinOp("+", ast.ConstantInt(1), ast.BinOp("*", ast.ConstantInt(2), ast.ConstantInt(3), 1), 1))
        ]))
        assert ec.space.parse(ec, "1 * 2 + 3") == ast.Main(ast.Block([
            ast.Statement(ast.BinOp("+", ast.BinOp("*", ast.ConstantInt(1), ast.ConstantInt(2), 1), ast.ConstantInt(3), 1))
        ]))
        assert ec.space.parse(ec, "2 << 3 * 4") == ast.Main(ast.Block([
            ast.Statement(ast.BinOp("<<", ast.ConstantInt(2), ast.BinOp("*", ast.ConstantInt(3), ast.ConstantInt(4), 1), 1))
        ]))

    def test_parens(self, ec):
        assert ec.space.parse(ec, "1 * (2 - 3)") == ast.Main(ast.Block([
            ast.Statement(ast.BinOp("*", ast.ConstantInt(1), ast.BinOp("-", ast.ConstantInt(2), ast.ConstantInt(3), 1), 1))
        ]))

    def test_multiple_statements_no_sep(self, ec):
        with self.raises("SyntaxError"):
            ec.space.parse(ec, "3 3")

    def test_multiple_statements(self, ec):
        r = ec.space.parse(ec, """
        1
        2
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.ConstantInt(1)),
            ast.Statement(ast.ConstantInt(2)),
        ]))

    def test_multiple_statements_semicolon(self, ec):
        assert ec.space.parse(ec, "1; 2") == ast.Main(ast.Block([
            ast.Statement(ast.ConstantInt(1)),
            ast.Statement(ast.ConstantInt(2)),
        ]))

        assert ec.space.parse(ec, "1; 2; 3") == ast.Main(ast.Block([
            ast.Statement(ast.ConstantInt(1)),
            ast.Statement(ast.ConstantInt(2)),
            ast.Statement(ast.ConstantInt(3)),
        ]))

    def test_send(self, ec):
        assert ec.space.parse(ec, "puts 2") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.Self(1), "puts", [ast.ConstantInt(2)], None, 1))
        ]))
        assert ec.space.parse(ec, "puts 1, 2") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.Self(1), "puts", [ast.ConstantInt(1), ast.ConstantInt(2)], None, 1))
        ]))
        assert ec.space.parse(ec, "puts(1, 2)") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.Self(1), "puts", [ast.ConstantInt(1), ast.ConstantInt(2)], None, 1))
        ]))
        assert ec.space.parse(ec, "2.to_s") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.ConstantInt(2), "to_s", [], None, 1))
        ]))
        assert ec.space.parse(ec, "2.to_s 10") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.ConstantInt(2), "to_s", [ast.ConstantInt(10)], None, 1))
        ]))
        assert ec.space.parse(ec, "2.to_s.to_i") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.Send(ast.ConstantInt(2), "to_s", [], None, 1), "to_i", [], None, 1))
        ]))
        assert ec.space.parse(ec, "2.to_s()") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.ConstantInt(2), "to_s", [], None, 1))
        ]))
        assert ec.space.parse(ec, "2.to_s(10)") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.ConstantInt(2), "to_s", [ast.ConstantInt(10)], None, 1))
        ]))
        assert ec.space.parse(ec, "2.to_s(*10)") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.ConstantInt(2), "to_s", [ast.Splat(ast.ConstantInt(10))], None, 1))
        ]))
        assert ec.space.parse(ec, "2.to_s(10, *x)") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.ConstantInt(2), "to_s", [ast.ConstantInt(10), ast.Splat(ast.Variable("x", 1))], None, 1))
        ]))

    def test_assignment(self, ec):
        assert ec.space.parse(ec, "a = 3") == ast.Main(ast.Block([
            ast.Statement(ast.Assignment("=", "a", ast.ConstantInt(3), 1))
        ]))
        assert ec.space.parse(ec, "a = b = 3") == ast.Main(ast.Block([
            ast.Statement(ast.Assignment("=", "a", ast.Assignment("=", "b", ast.ConstantInt(3), 1), 1))
        ]))

    def test_load_variable(self, ec):
        assert ec.space.parse(ec, "a") == ast.Main(ast.Block([
            ast.Statement(ast.Variable("a", 1))
        ]))

    def test_if_statement(self, ec):
        res = lambda lineno: ast.Main(ast.Block([
            ast.Statement(ast.If(ast.ConstantInt(3), ast.Block([
                ast.Statement(ast.Send(ast.Self(lineno), "puts", [ast.ConstantInt(2)], None, lineno))
            ]), ast.Block([])))
        ]))
        assert ec.space.parse(ec, "if 3 then puts 2 end") == res(1)
        assert ec.space.parse(ec, """
        if 3
            puts 2
        end
        """) == res(3)
        assert ec.space.parse(ec, "if 3; puts 2 end") == res(1)
        assert ec.space.parse(ec, "if 3; end") == ast.Main(ast.Block([
            ast.Statement(ast.If(ast.ConstantInt(3), ast.Block([]), ast.Block([])))
        ]))
        r = ec.space.parse(ec, """
        if 0
            puts 2
            puts 3
            puts 4
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.If(ast.ConstantInt(0), ast.Block([
                ast.Statement(ast.Send(ast.Self(3), "puts", [ast.ConstantInt(2)], None, 3)),
                ast.Statement(ast.Send(ast.Self(4), "puts", [ast.ConstantInt(3)], None, 4)),
                ast.Statement(ast.Send(ast.Self(5), "puts", [ast.ConstantInt(4)], None, 5)),
            ]), ast.Block([])))
        ]))

    def test_else(self, ec):
        r = ec.space.parse(ec, """if 3 then 5 else 4 end""")
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.If(ast.ConstantInt(3), ast.Block([
                ast.Statement(ast.ConstantInt(5))
            ]), ast.Block([
                ast.Statement(ast.ConstantInt(4))
            ])))
        ]))

    def test_elsif(self, ec):
        r = ec.space.parse(ec, """
        if 3
            5
        elsif 4 == 2
            3
        elsif 3 == 1
            2
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.If(ast.ConstantInt(3), ast.Block([
                ast.Statement(ast.ConstantInt(5))
            ]), ast.Block([
                ast.Statement(ast.If(ast.BinOp("==", ast.ConstantInt(4), ast.ConstantInt(2), 4), ast.Block([
                    ast.Statement(ast.ConstantInt(3))
                ]), ast.Block([
                    ast.Statement(ast.If(ast.BinOp("==", ast.ConstantInt(3), ast.ConstantInt(1), 6), ast.Block([
                        ast.Statement(ast.ConstantInt(2))
                    ]), ast.Block([ast.Statement(ast.Variable("nil", -1))])))
                ])))
            ])))
        ]))

    def test_comparison_ops(self, ec):
        assert ec.space.parse(ec, "1 == 2; 1 < 2; 1 > 2; 1 != 2; 1 <= 2; 1 >= 2") == ast.Main(ast.Block([
            ast.Statement(ast.BinOp("==", ast.ConstantInt(1), ast.ConstantInt(2), 1)),
            ast.Statement(ast.BinOp("<", ast.ConstantInt(1), ast.ConstantInt(2), 1)),
            ast.Statement(ast.BinOp(">", ast.ConstantInt(1), ast.ConstantInt(2), 1)),
            ast.Statement(ast.BinOp("!=", ast.ConstantInt(1), ast.ConstantInt(2), 1)),
            ast.Statement(ast.BinOp("<=", ast.ConstantInt(1), ast.ConstantInt(2), 1)),
            ast.Statement(ast.BinOp(">=", ast.ConstantInt(1), ast.ConstantInt(2), 1)),
        ]))

    def test_while(self, ec):
        expected = ast.Main(ast.Block([
            ast.Statement(ast.While(ast.Variable("true", 1), ast.Block([
                ast.Statement(ast.Send(ast.Self(1), "puts", [ast.ConstantInt(5)], None, 1))
            ])))
        ]))
        assert ec.space.parse(ec, "while true do puts 5 end") == expected
        assert ec.space.parse(ec, "while true do; puts 5 end") == expected
        assert ec.space.parse(ec, "while true; puts 5 end") == expected
        assert ec.space.parse(ec, "while true; end") == ast.Main(ast.Block([
            ast.Statement(ast.While(ast.Variable("true", 1), ast.Block([
                ast.Statement(ast.Variable("nil", -1))
            ])))
        ]))

        res = ec.space.parse(ec, """
        i = 0
        while i < 10 do
            puts i
            puts 1
            puts i
            puts true
        end
        """)
        assert res == ast.Main(ast.Block([
            ast.Statement(ast.Assignment("=", "i", ast.ConstantInt(0), 2)),
            ast.Statement(ast.While(ast.BinOp("<", ast.Variable("i", 3), ast.ConstantInt(10), 3), ast.Block([
                ast.Statement(ast.Send(ast.Self(4), "puts", [ast.Variable("i", 4)], None, 4)),
                ast.Statement(ast.Send(ast.Self(5), "puts", [ast.ConstantInt(1)], None, 5)),
                ast.Statement(ast.Send(ast.Self(6), "puts", [ast.Variable("i", 6)], None, 6)),
                ast.Statement(ast.Send(ast.Self(7), "puts", [ast.Variable("true", 7)], None, 7)),
            ])))
        ]))

    def test_until(self, ec):
        r = ec.space.parse(ec, """
        until 3
            5
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Until(ast.ConstantInt(3), ast.Block([
                ast.Statement(ast.ConstantInt(5))
            ])))
        ]))

    def test_return(self, ec):
        assert ec.space.parse(ec, "return 4") == ast.Main(ast.Block([
            ast.Return(ast.ConstantInt(4))
        ]))
        assert ec.space.parse(ec, "return") == ast.Main(ast.Block([
            ast.Return(ast.Variable("nil", 1))
        ]))

    def test_array(self, ec):
        assert ec.space.parse(ec, "[]") == ast.Main(ast.Block([
            ast.Statement(ast.Array([]))
        ]))

        assert ec.space.parse(ec, "[1, 2, 3]") == ast.Main(ast.Block([
            ast.Statement(ast.Array([
                ast.ConstantInt(1),
                ast.ConstantInt(2),
                ast.ConstantInt(3),
            ]))
        ]))

        assert ec.space.parse(ec, "[[1], [2], [3]]") == ast.Main(ast.Block([
            ast.Statement(ast.Array([
                ast.Array([ast.ConstantInt(1)]),
                ast.Array([ast.ConstantInt(2)]),
                ast.Array([ast.ConstantInt(3)]),
            ]))
        ]))

    def test_subscript(self, ec):
        assert ec.space.parse(ec, "[1][0]") == ast.Main(ast.Block([
            ast.Statement(ast.Subscript(ast.Array([ast.ConstantInt(1)]), [ast.ConstantInt(0)], 1))
        ]))

        assert ec.space.parse(ec, "self[i]") == ast.Main(ast.Block([
            ast.Statement(ast.Subscript(ast.Variable("self", 1), [ast.Variable("i", 1)], 1))
        ]))

        assert ec.space.parse(ec, "self[i].to_s") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.Subscript(ast.Variable("self", 1), [ast.Variable("i", 1)], 1), "to_s", [], None, 1))
        ]))

    def test_subscript_assginment(self, ec):
        assert ec.space.parse(ec, "x[0] = 5") == ast.Main(ast.Block([
            ast.Statement(ast.SubscriptAssignment("=", ast.Variable("x", 1), [ast.ConstantInt(0)], ast.ConstantInt(5), 1))
        ]))

    def test_def(self, ec):
        assert ec.space.parse(ec, "def f() end") == ast.Main(ast.Block([
            ast.Statement(ast.Function(None, "f", [], None, None, ast.Block([])))
        ]))

        assert ec.space.parse(ec, "def f(a, b) a + b end") == ast.Main(ast.Block([
            ast.Statement(ast.Function(None, "f", [ast.Argument("a"), ast.Argument("b")], None, None, ast.Block([
                ast.Statement(ast.BinOp("+", ast.Variable("a", 1), ast.Variable("b", 1), 1))
            ])))
        ]))

        r = ec.space.parse(ec, """
        def f(a)
            puts a
            puts a
            puts a
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Function(None, "f", [ast.Argument("a")], None, None, ast.Block([
                ast.Statement(ast.Send(ast.Self(3), "puts", [ast.Variable("a", 3)], None, 3)),
                ast.Statement(ast.Send(ast.Self(4), "puts", [ast.Variable("a", 4)], None, 4)),
                ast.Statement(ast.Send(ast.Self(5), "puts", [ast.Variable("a", 5)], None, 5)),
            ])))
        ]))

        assert ec.space.parse(ec, "x = def f() end") == ast.Main(ast.Block([
            ast.Statement(ast.Assignment("=", "x", ast.Function(None, "f", [], None, None, ast.Block([])), 1))
        ]))

        r = ec.space.parse(ec, """
        def f a, b
            a + b
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Function(None, "f", [ast.Argument("a"), ast.Argument("b")], None, None, ast.Block([
                ast.Statement(ast.BinOp("+", ast.Variable("a", 3), ast.Variable("b", 3), 3))
            ])))
        ]))

        r = ec.space.parse(ec, """
        def f(&b)
            b
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Function(None, "f", [], None, "b", ast.Block([
                ast.Statement(ast.Variable("b", 3))
            ])))
        ]))
        with self.raises("SyntaxError"):
            ec.space.parse(ec, """
            def f(&b, a)
                b
            end
            """)
        with self.raises("SyntaxError"):
            ec.space.parse(ec, """
            def f(&b, &c)
                b
            end
            """)

    def test_string(self, ec):
        assert ec.space.parse(ec, '"abc"') == ast.Main(ast.Block([
            ast.Statement(ast.ConstantString("abc"))
        ]))
        assert ec.space.parse(ec, '"abc".size') == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.ConstantString("abc"), "size", [], None, 1))
        ]))
        assert ec.space.parse(ec, "'abc'") == ast.Main(ast.Block([
            ast.Statement(ast.ConstantString("abc"))
        ]))
        assert ec.space.parse(ec, '"\n"') == ast.Main(ast.Block([
            ast.Statement(ast.ConstantString("\n"))
        ]))

    def test_class(self, ec):
        r = ec.space.parse(ec, """
        class X
        end""")
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Class("X", None, ast.Block([])))
        ]))

        r = ec.space.parse(ec, """
        class X
            def f()
                2
            end
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Class("X", None, ast.Block([
                ast.Statement(ast.Function(None, "f", [], None, None, ast.Block([
                    ast.Statement(ast.ConstantInt(2))
                ])))
            ])))
        ]))

        assert ec.space.parse(ec, "class X < Object; end") == ast.Main(ast.Block([
            ast.Statement(ast.Class("X", ast.LookupConstant(ast.Scope(1), "Object", 1), ast.Block([])))
        ]))

    def test_singleton_class(self, ec):
        r = ec.space.parse(ec, "class << self; end")
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.SingletonClass(ast.Variable("self", 1), ast.Block([]), 1))
        ]))

    def test_instance_variable(self, ec):
        assert ec.space.parse(ec, "@a") == ast.Main(ast.Block([
            ast.Statement(ast.InstanceVariable("a"))
        ]))
        assert ec.space.parse(ec, "@a = 3") == ast.Main(ast.Block([
            ast.Statement(ast.InstanceVariableAssignment("=", "a", ast.ConstantInt(3)))
        ]))

    def test_do_block(self, ec):
        r = ec.space.parse(ec, """
        x.each do
            puts 1
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.Variable("x", 2), "each", [], ast.SendBlock([], ast.Block([
                ast.Statement(ast.Send(ast.Self(3), "puts", [ast.ConstantInt(1)], None, 3))
            ])), 2))
        ]))
        r = ec.space.parse(ec, """
        x.each do ||
            puts 1
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.Variable("x", 2), "each", [], ast.SendBlock([], ast.Block([
                ast.Statement(ast.Send(ast.Self(3), "puts", [ast.ConstantInt(1)], None, 3))
            ])), 2))
        ]))
        r = ec.space.parse(ec, """
        x.each do |a|
            puts a
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.Variable("x", 2), "each", [], ast.SendBlock([ast.Argument("a")], ast.Block([
                ast.Statement(ast.Send(ast.Self(3), "puts", [ast.Variable("a", 3)], None, 3))
            ])), 2))
        ]))

    def test_block(self, ec):
        assert ec.space.parse(ec, "[].map { |x| x }") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.Array([]), "map", [], ast.SendBlock([ast.Argument("x")], ast.Block([
                ast.Statement(ast.Variable("x", 1))
            ])), 1))
        ]))
        assert ec.space.parse(ec, "[].inject(0) { |x, s| x + s }") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.Array([]), "inject", [ast.ConstantInt(0)], ast.SendBlock([ast.Argument("x"), ast.Argument("s")], ast.Block([
                ast.Statement(ast.BinOp("+", ast.Variable("x", 1), ast.Variable("s", 1), 1))
            ])), 1))
        ]))
        assert ec.space.parse(ec, "f { 5 }") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.Self(1), "f", [], ast.SendBlock([], ast.Block([
                ast.Statement(ast.ConstantInt(5))
            ])), 1))
        ]))
        assert ec.space.parse(ec, "f(3) { 5 }") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.Self(1), "f", [ast.ConstantInt(3)], ast.SendBlock([], ast.Block([
                ast.Statement(ast.ConstantInt(5))
            ])), 1))
        ]))

    def test_yield(self, ec):
        assert ec.space.parse(ec, "yield") == ast.Main(ast.Block([
            ast.Statement(ast.Yield([], 1))
        ]))
        assert ec.space.parse(ec, "yield 3, 4") == ast.Main(ast.Block([
            ast.Statement(ast.Yield([ast.ConstantInt(3), ast.ConstantInt(4)], 1))
        ]))
        assert ec.space.parse(ec, "yield 4") == ast.Main(ast.Block([
            ast.Statement(ast.Yield([ast.ConstantInt(4)], 1))
        ]))

    def test_symbol(self, ec):
        assert ec.space.parse(ec, ":abc") == ast.Main(ast.Block([
            ast.Statement(ast.ConstantSymbol("abc"))
        ]))

    def test_range(self, ec):
        assert ec.space.parse(ec, "2..3") == ast.Main(ast.Block([
            ast.Statement(ast.Range(ast.ConstantInt(2), ast.ConstantInt(3), False))
        ]))
        assert ec.space.parse(ec, "2...3") == ast.Main(ast.Block([
            ast.Statement(ast.Range(ast.ConstantInt(2), ast.ConstantInt(3), True))
        ]))
        assert ec.space.parse(ec, '"abc".."def"') == ast.Main(ast.Block([
            ast.Statement(ast.Range(ast.ConstantString("abc"), ast.ConstantString("def"), False))
        ]))

    def test_assign_method(self, ec):
        assert ec.space.parse(ec, "self.attribute = 3") == ast.Main(ast.Block([
            ast.Statement(ast.MethodAssignment("=", ast.Variable("self", 1), "attribute", ast.ConstantInt(3)))
        ]))

        assert ec.space.parse(ec, "self.attribute.other_attr.other = 12") == ast.Main(ast.Block([
            ast.Statement(ast.MethodAssignment("=", ast.Send(ast.Send(ast.Variable("self", 1), "attribute", [], None, 1), "other_attr", [], None, 1), "other", ast.ConstantInt(12)))
        ]))

    def test_augmented_assignment(self, ec):
        assert ec.space.parse(ec, "i += 1") == ast.Main(ast.Block([
            ast.Statement(ast.Assignment("+=", "i", ast.ConstantInt(1), 1))
        ]))
        assert ec.space.parse(ec, "i -= 1") == ast.Main(ast.Block([
            ast.Statement(ast.Assignment("-=", "i", ast.ConstantInt(1), 1))
        ]))

        assert ec.space.parse(ec, "self.x += 2") == ast.Main(ast.Block([
            ast.Statement(ast.MethodAssignment("+=", ast.Variable("self", 1), "x", ast.ConstantInt(2)))
        ]))

        assert ec.space.parse(ec, "@a += 3") == ast.Main(ast.Block([
            ast.Statement(ast.InstanceVariableAssignment("+=", "a", ast.ConstantInt(3)))
        ]))

    def test_block_result(self, ec):
        r = ec.space.parse(ec, """
        [].inject(0) do |s, x|
            s + x
        end * 5
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.BinOp("*", ast.Send(ast.Array([]), "inject", [ast.ConstantInt(0)], ast.SendBlock([ast.Argument("s"), ast.Argument("x")], ast.Block([
                ast.Statement(ast.BinOp("+", ast.Variable("s", 3), ast.Variable("x", 3), 3))
            ])), 2), ast.ConstantInt(5), 2))
        ]))

    def test_unary_neg(self, ec):
        assert ec.space.parse(ec, "-b") == ast.Main(ast.Block([
            ast.Statement(ast.UnaryOp("-", ast.Variable("b", 1), 1))
        ]))
        assert ec.space.parse(ec, "Math.exp(-a)") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.LookupConstant(ast.Scope(1), "Math", 1), "exp", [ast.UnaryOp("-", ast.Variable("a", 1), 1)], None, 1))
        ]))

    def test_unless(self, ec):
        r = ec.space.parse(ec, """
        unless 1 == 2 then
            return 4
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.If(ast.BinOp("==", ast.ConstantInt(1), ast.ConstantInt(2), 2), ast.Block([]), ast.Block([
                ast.Return(ast.ConstantInt(4))
            ])))
        ]))

    def test_constant_lookup(self, ec):
        assert ec.space.parse(ec, "Module::Constant") == ast.Main(ast.Block([
            ast.Statement(ast.LookupConstant(ast.LookupConstant(ast.Scope(1), "Module", 1), "Constant", 1))
        ]))
        assert ec.space.parse(ec, "abc::Constant = 5") == ast.Main(ast.Block([
            ast.Statement(ast.ConstantAssignment("=", ast.Variable("abc", 1), "Constant", ast.ConstantInt(5)))
        ]))

    def test___FILE__(self, ec):
        assert ec.space.parse(ec, "__FILE__") == ast.Main(ast.Block([
            ast.Statement(ast.Variable("__FILE__", 1))
        ]))
        with self.raises("SyntaxError"):
            ec.space.parse(ec, "__FILE__ = 5")

    def test_function_default_arguments(self, ec):
        function = lambda name, args: ast.Main(ast.Block([
            ast.Statement(ast.Function(None, name, args, None, None, ast.Block([])))
        ]))

        r = ec.space.parse(ec, """
        def f(a, b=3)
        end
        """)
        assert r == function("f", [ast.Argument("a"), ast.Argument("b", ast.ConstantInt(3))])

        r = ec.space.parse(ec, """
        def f(a, b, c=b)
        end
        """)
        assert r == function("f", [ast.Argument("a"), ast.Argument("b"), ast.Argument("c", ast.Variable("b", 2))])

        r = ec.space.parse(ec, """
        def f(a=3, b)
        end
        """)
        assert r == function("f", [ast.Argument("a", ast.ConstantInt(3)), ast.Argument("b")])

        r = ec.space.parse(ec, """
        def f(a, b=3, c)
        end
        """)
        assert r == function("f", [ast.Argument("a"), ast.Argument("b", ast.ConstantInt(3)), ast.Argument("c")])

        with self.raises("SyntaxError"):
            ec.space.parse(ec, """
            def f(a, b=3, c, d=5)
            end
            """)

    def test_exceptions(self, ec):
        r = ec.space.parse(ec, """
        begin
            1 + 1
        rescue ZeroDivisionError
            puts "zero"
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.TryExcept(
                ast.Block([
                    ast.Statement(ast.BinOp("+", ast.ConstantInt(1), ast.ConstantInt(1), 3))
                ]),
                [
                    ast.ExceptHandler(ast.LookupConstant(ast.Scope(4), "ZeroDivisionError", 4), None, ast.Block([
                        ast.Statement(ast.Send(ast.Self(5), "puts", [ast.ConstantString("zero")], None, 5))
                    ]))
                ]
            ))
        ]))

        r = ec.space.parse(ec, """
        begin
            1 / 0
        rescue ZeroDivisionError => e
            puts e
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.TryExcept(
                ast.Block([
                    ast.Statement(ast.BinOp("/", ast.ConstantInt(1), ast.ConstantInt(0), 3))
                ]),
                [
                    ast.ExceptHandler(ast.LookupConstant(ast.Scope(4), "ZeroDivisionError", 4), "e", ast.Block([
                        ast.Statement(ast.Send(ast.Self(5), "puts", [ast.Variable("e", 5)], None, 5))
                    ]))
                ]
            ))
        ]))

        r = ec.space.parse(ec, """
        begin
            1 / 0
        rescue ZeroDivisionError => e
            puts e
        rescue NoMethodError
            puts "?"
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.TryExcept(
                ast.Block([
                    ast.Statement(ast.BinOp("/", ast.ConstantInt(1), ast.ConstantInt(0), 3))
                ]),
                [
                    ast.ExceptHandler(ast.LookupConstant(ast.Scope(4), "ZeroDivisionError", 4), "e", ast.Block([
                        ast.Statement(ast.Send(ast.Self(5), "puts", [ast.Variable("e", 5)], None, 5))
                    ])),
                    ast.ExceptHandler(ast.LookupConstant(ast.Scope(6), "NoMethodError", 6), None, ast.Block([
                        ast.Statement(ast.Send(ast.Self(7), "puts", [ast.ConstantString("?")], None, 7))
                    ])),
                ]
            ))
        ]))

        r = ec.space.parse(ec, """
        begin
            1 / 0
        rescue
            5
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.TryExcept(
                ast.Block([
                    ast.Statement(ast.BinOp("/", ast.ConstantInt(1), ast.ConstantInt(0), 3))
                ]),
                [
                    ast.ExceptHandler(None, None, ast.Block([
                        ast.Statement(ast.ConstantInt(5))
                    ]))
                ]
            ))
        ]))

        r = ec.space.parse(ec, """
        begin
            1 / 0
        ensure
            puts "ensure"
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.TryFinally(
                ast.Block([
                    ast.Statement(ast.BinOp("/", ast.ConstantInt(1), ast.ConstantInt(0), 3))
                ]),
                ast.Block([
                    ast.Statement(ast.Send(ast.Self(5), "puts", [ast.ConstantString("ensure")], None, 5))
                ])
            ))
        ]))

        r = ec.space.parse(ec, """
        begin
            1 / 0
        rescue ZeroDivisionError
            puts "rescue"
        ensure
            puts "ensure"
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.TryFinally(
                ast.TryExcept(ast.Block([
                    ast.Statement(ast.BinOp("/", ast.ConstantInt(1), ast.ConstantInt(0), 3))
                ]), [
                    ast.ExceptHandler(ast.LookupConstant(ast.Scope(4), "ZeroDivisionError", 4), None, ast.Block([
                        ast.Statement(ast.Send(ast.Self(5), "puts", [ast.ConstantString("rescue")], None, 5))
                    ]))
                ]),
                ast.Block([
                    ast.Statement(ast.Send(ast.Self(7), "puts", [ast.ConstantString("ensure")], None, 7))
                ])
            ))
        ]))

        r = ec.space.parse(ec, """
        begin
            1 + 1
            1 / 0
        rescue
            puts "rescue"
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.TryExcept(
                ast.Block([
                    ast.Statement(ast.BinOp("+", ast.ConstantInt(1), ast.ConstantInt(1), 3)),
                    ast.Statement(ast.BinOp("/", ast.ConstantInt(1), ast.ConstantInt(0), 4)),
                ]), [
                    ast.ExceptHandler(None, None, ast.Block([
                        ast.Statement(ast.Send(ast.Self(6), "puts", [ast.ConstantString("rescue")], None, 6))
                    ]))
                ]
            ))
        ]))

    def test_module(self, ec):
        r = ec.space.parse(ec, """
        module M
            def method
            end
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Module("M", ast.Block([
                ast.Statement(ast.Function(None, "method", [], None, None, ast.Block([])))
            ])))
        ]))

    def test_question_mark(self, ec):
        assert ec.space.parse(ec, "obj.method?") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.Variable("obj", 1), "method?", [], None, 1))
        ]))
        assert ec.space.parse(ec, "def method?() end") == ast.Main(ast.Block([
            ast.Statement(ast.Function(None, "method?", [], None, None, ast.Block([])))
        ]))
        assert ec.space.parse(ec, "method?") == ast.Main(ast.Block([
            ast.Statement(ast.Variable("method?", 1))
        ]))
        with self.raises("SyntaxError"):
            ec.space.parse(ec, "method? = 4")

    def test_exclamation_point(self, ec):
        assert ec.space.parse(ec, "obj.method!") == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.Variable("obj", 1), "method!", [], None, 1))
        ]))
        assert ec.space.parse(ec, "def method!() end") == ast.Main(ast.Block([
            ast.Statement(ast.Function(None, "method!", [], None, None, ast.Block([])))
        ]))
        assert ec.space.parse(ec, "method!") == ast.Main(ast.Block([
            ast.Statement(ast.Variable("method!", 1))
        ]))
        with self.raises("SyntaxError"):
            ec.space.parse(ec, "method! = 4")

    def test_singleton_method(self, ec):
        r = ec.space.parse(ec, """
        def Array.hello
            "hello world"
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Function(ast.LookupConstant(ast.Scope(2), "Array", 2), "hello", [], None, None, ast.Block([
                ast.Statement(ast.ConstantString("hello world")),
            ])))
        ]))

    def test_global_var(self, ec):
        r = ec.space.parse(ec, """
        $abc = 3
        $abc
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.GlobalAssignment("=", "$abc", ast.ConstantInt(3))),
            ast.Statement(ast.Global("$abc")),
        ]))

    def test_comments(self, ec):
        r = ec.space.parse(ec, """
        #abc 123
        1 + 1 # more comment
        # another comment
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.BinOp("+", ast.ConstantInt(1), ast.ConstantInt(1), 3))
        ]))

    def test_send_block_argument(self, ec):
        r = ec.space.parse(ec, "f(&b)")
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.Self(1), "f", [], ast.BlockArgument(ast.Variable("b", 1)), 1))
        ]))

        r = ec.space.parse(ec, "f(3, 4, &a)")
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Send(ast.Self(1), "f", [ast.ConstantInt(3), ast.ConstantInt(4)], ast.BlockArgument(ast.Variable("a", 1)), 1))
        ]))

        with self.raises("SyntaxError"):
            ec.space.parse(ec, "f(&b, &b)")

        with self.raises("SyntaxError"):
            ec.space.parse(ec, "f(&b, a)")

        with self.raises("SyntaxError"):
            ec.space.parse(ec, "f(&b) {}")

        with self.raises("SyntaxError"):
            ec.space.parse(ec, """
            f(&b) do ||
            end
            """)

    def test_declare_splat_argument(self, ec):
        r = ec.space.parse(ec, "def f(*args) end")
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Function(None, "f", [], "args", None, ast.Block([])))
        ]))

        r = ec.space.parse(ec, "def f(*args, &g) end")
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Function(None, "f", [], "args", "g", ast.Block([])))
        ]))

        with self.raises("SyntaxError"):
            ec.space.parse(ec, "def f(*args, g)")

        with self.raises("SyntaxError"):
            ec.space.parse(ec, "def f(*args, g=5)")

    def test_regexp(self, ec):
        re = lambda re: ast.Main(ast.Block([
            ast.Statement(ast.ConstantRegexp(re))
        ]))

        assert ec.space.parse(ec, r"/a/") == re("a")
        assert ec.space.parse(ec, r"/\w/") == re(r"\w")

    def test_or(self, ec):
        assert ec.space.parse(ec, "3 || 4") == ast.Main(ast.Block([
            ast.Statement(ast.Or(ast.ConstantInt(3), ast.ConstantInt(4)))
        ]))
        assert ec.space.parse(ec, "3 + 4 || 4 * 5") == ast.Main(ast.Block([
            ast.Statement(ast.Or(
                ast.BinOp("+", ast.ConstantInt(3), ast.ConstantInt(4), 1),
                ast.BinOp("*", ast.ConstantInt(4), ast.ConstantInt(5), 1),
            ))
        ]))

    def test_and(self, ec):
        assert ec.space.parse(ec, "3 && 4") == ast.Main(ast.Block([
            ast.Statement(ast.And(ast.ConstantInt(3), ast.ConstantInt(4)))
        ]))
        assert ec.space.parse(ec, "4 || 5 && 6") == ast.Main(ast.Block([
            ast.Statement(ast.Or(
                ast.ConstantInt(4),
                ast.And(ast.ConstantInt(5), ast.ConstantInt(6))
            ))
        ]))

    def test_not(self, ec):
        assert ec.space.parse(ec, "!3") == ast.Main(ast.Block([
            ast.Statement(ast.Not(ast.ConstantInt(3)))
        ]))

    def test_inline_if(self, ec):
        assert ec.space.parse(ec, "return 5 if 3") == ast.Main(ast.Block([
            ast.Statement(ast.If(ast.ConstantInt(3), ast.Block([
                ast.Return(ast.ConstantInt(5))
            ]), ast.Block([])))
        ]))

    def test_inline_unless(self, ec):
        assert ec.space.parse(ec, "return 5 unless 3") == ast.Main(ast.Block([
            ast.Statement(ast.If(ast.ConstantInt(3),
                ast.Block([]),
                ast.Block([ast.Return(ast.ConstantInt(5))]),
            ))
        ]))

    def test_inline_until(self, ec):
        assert ec.space.parse(ec, "i += 1 until 3") == ast.Main(ast.Block([
            ast.Statement(ast.Until(ast.ConstantInt(3), ast.Block([
                ast.Statement(ast.Assignment("+=", "i", ast.ConstantInt(1), 1))
            ])))
        ]))

    def test_inline_precedence(self, ec):
        assert ec.space.parse(ec, "return unless x = 3") == ast.Main(ast.Block([
            ast.Statement(ast.If(ast.Assignment("=", "x", ast.ConstantInt(3), 1),
                ast.Block([]),
                ast.Block([
                    ast.Return(ast.Variable("nil", 1)),
                ])
            ))
        ]))
        r = ec.space.parse(ec, """
        def f
            return unless x = 3
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Function(None, "f", [], None, None, ast.Block([
                ast.Statement(ast.If(ast.Assignment("=", "x", ast.ConstantInt(3), 3),
                    ast.Block([]),
                    ast.Block([
                        ast.Return(ast.Variable("nil", 3))
                    ])
                ))
            ])))
        ]))

    def test_ternary_operator(self, ec):
        assert ec.space.parse(ec, "3 ? 2 : 5") == ast.Main(ast.Block([
            ast.Statement(ast.If(ast.ConstantInt(3),
                ast.Block([ast.Statement(ast.ConstantInt(2))]),
                ast.Block([ast.Statement(ast.ConstantInt(5))]),
            ))
        ]))

    def test_case(self, ec):
        r = ec.space.parse(ec, """
        case 3
        when 5 then
            6
        when 4
            7
        else
            9
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Case(ast.ConstantInt(3), [
                (ast.ConstantInt(5), ast.Block([ast.Statement(ast.ConstantInt(6))])),
                (ast.ConstantInt(4), ast.Block([ast.Statement(ast.ConstantInt(7))]))
            ], ast.Block([ast.Statement(ast.ConstantInt(9))])))
        ]))

    def test_case_regexp(self, ec):
        r = ec.space.parse(ec, """
        case 0
        when /a/
        end
        """)
        assert r == ast.Main(ast.Block([
            ast.Statement(ast.Case(ast.ConstantInt(0), [
                (ast.ConstantRegexp("a"), ast.Block([]))
            ], ast.Block([])))
        ]))