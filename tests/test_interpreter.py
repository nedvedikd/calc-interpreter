import pytest
from calc_interpreter.exception import InterpreterError
from calc_interpreter.lexer import Lexer, Token, TokenType
from calc_interpreter.parser import Parser
from calc_interpreter.evaluator import Evaluator, interpret


@pytest.fixture(autouse=True)
def clear_evaluator():
    Evaluator.clear()


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
    for operation, result in zip(operations, results):
        lexer = Lexer(operation)
        parser = Parser(lexer)
        tree = parser.parse()
        evaluator = Evaluator(tree)
        output = evaluator.evaluate()
        assert output == result


def test_command_mode_usage(capsys):
    operations = ['mode', 'mode __idk__']
    usage = 'usage: mode (ast | rpn | tokens | default)\n'
    for operation in operations:
        interpret(operation)
        output, _ = capsys.readouterr()
        assert output == usage


def test_command_mode_rpn(capsys):
    operations = ['mode rpn', '(5+3) * 2']
    results = ['switching to mode: rpn\n', '5 3 + 2 *\n']
    for operation, result in zip(operations, results):
        interpret(operation)
        output, _ = capsys.readouterr()
        assert output == result


def test_mode_tokens(capsys):
    operations = ['mode tokens', '5+3']
    tokens = [Token(TokenType.NUMBER, 5), Token(TokenType.PLUS, '+'), Token(TokenType.NUMBER, 3), '']
    tokens = [str(token) for token in tokens]
    tokens = '\n'.join(tokens)
    results = ['switching to mode: tokens\n', tokens]
    for operation, result in zip(operations, results):
        interpret(operation)
        output, _ = capsys.readouterr()
        assert output == result


def test_interpret(capsys):
    interpret('25 + 5')
    output, _ = capsys.readouterr()
    assert output == '30\n'
