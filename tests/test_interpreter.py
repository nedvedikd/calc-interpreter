import pytest
from calc_interpreter.exception import InterpreterError
from calc_interpreter.lexer import Lexer, Token, TokenType
from calc_interpreter.parser import Parser
from calc_interpreter.evaluator import Evaluator


def test_number():
    valid_numbers = open('tests/data/valid_numbers.txt').readlines()
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
    expressions = open('tests/data/expressions.txt').readlines()
    expressions = [expression.split('=') for expression in expressions]
    for expression, result in expressions:
        print(expression, result)
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


def test_invalid_numbers():
    numbers = open('tests/data/invalid_numbers.txt').readlines()
    for number in numbers:
        exceptions = InterpreterError, ValueError
        with pytest.raises(exceptions):
            lexer = Lexer(number)
            parser = Parser(lexer)
            tree = parser.parse()
            evaluator = Evaluator(tree)
            evaluator.evaluate()


def test_bitwise_error():
    expressions = open('tests/data/invalid_operations.txt').readlines()
    for expression in expressions:
        with pytest.raises(InterpreterError):
            lexer = Lexer(expression)
            parser = Parser(lexer)
            tree = parser.parse()
            evaluator = Evaluator(tree)
            evaluator.evaluate()


def test_ans():
    operations = ['ans', '45 / 9', 'ans ** 2']
    results = [None, 5, 25]
    Evaluator.clear()
    for operation, result in zip(operations, results):
        lexer = Lexer(operation)
        parser = Parser(lexer)
        tree = parser.parse()
        evaluator = Evaluator(tree)
        output = evaluator.evaluate()
        assert output == result
