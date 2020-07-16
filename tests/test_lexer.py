from calc_interpreter.lexer import Lexer, TokenType


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
