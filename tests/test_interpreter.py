import pytest
from calc_interpreter.exception import InterpreterError
from calc_interpreter.lexer import Lexer, TokenType
from calc_interpreter.parser import Parser
from calc_interpreter.evaluator import Evaluator


def test_number():
    valid_numbers = open('tests/valid_numbers.txt').readlines()
    valid_numbers = [number.split() for number in valid_numbers]
    for number, calculated in valid_numbers:
        try:
            calculated = int(calculated)
        except ValueError:
            calculated = float(calculated)
        lexer = Lexer(number)
        token = lexer.next_token()
        assert token.type == TokenType.NUMBER
        assert token.value == calculated


def test_expressions():
    expressions = open('tests/expressions.txt').readlines()
    expressions = [expression.split('=') for expression in expressions]
    for expression, result in expressions:
        lexer = Lexer(expression)
        parser = Parser(lexer)
        tree = parser.parse()
        evaluator = Evaluator(tree)
        assert str(evaluator.evaluate()) == result.strip()


def test_variables():
    expressions = ['a = 52e-2', 'b = a * 10', 'b']
    results = [None, None, 5.2]
    for expression, result in zip(expressions, results):
        lexer = Lexer(expression)
        parser = Parser(lexer)
        tree = parser.parse()
        evaluator = Evaluator(tree)
        assert evaluator.evaluate() == result


def test_invalid_variables():
    lexer = Lexer('1a = 5')
    parser = Parser(lexer)
    with pytest.raises(InterpreterError):
        tree = parser.parse()
        evaluator = Evaluator(tree)
        evaluator.evaluate()
