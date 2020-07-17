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
        evaluator = Evaluator(parser)
        assert str(evaluator.evaluate()) == result.strip()
