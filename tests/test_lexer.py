from calc_interpreter.lexer import Lexer, TokenType


def test_number():
    valid_numbers = open('tests/valid_numbers.txt').readlines()
    for number in valid_numbers:
        lexer = Lexer(number)
        token = lexer.next_token()
        print(token)
        assert token.type == TokenType.NUMBER
