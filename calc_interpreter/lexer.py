"""
Lexical Analysis

identifier = letter {digit | letter}
letter = A-Za-z
number = (sep integer | integer sep | integer) {integer} [exponent]
exponent = ('e'|'E') ['+'|'-'] integer
integer = digit {digit}
sep = '.'
digit = 0-9
"""
import re
from enum import Enum, auto, unique
from typing import Optional
from dataclasses import dataclass
from calc_interpreter.exception import InterpreterError


@unique
class TokenType(Enum):
    PLUS = '+'
    MINUS = '-'
    MUL = '*'
    DIV = '/'
    FLOOR_DIV = '//'
    MODULUS = '%'
    POW = '**'
    BITWISE_NOT = '~'
    BITWISE_AND = '&'
    BITWISE_XOR = '^'
    BITWISE_OR = '|'
    BITWISE_LEFT_SHIFT = '<<'
    BITWISE_RIGHT_SHIFT = '>>'
    LPAREN = '('
    RPAREN = ')'
    ASSIGN = '='
    IDENTIFIER = auto()
    MODE = 'mode'
    NUMBER = auto()
    EOF = auto()

    @staticmethod
    def get(string, default=None):
        """
        Get TokenType based on value
        """
        if type(string) is not str:
            return default
        try:
            return TokenType(string)
        except ValueError:
            return default


@dataclass
class Token:
    type: TokenType
    value: [float, int, str]

    def __repr__(self):
        return f'Token(type={self.type.name!r}, value={self.value!r})'


class Grammar:
    NUMBER = r'[0-9.\+-]'
    OPERATOR = r'[\+\-/\*()~%\^&<>\|=]'
    STRING = r'[A-Za-z\_]'
    IGNORE = r'[\s]'
    EXPONENT = r'[eE]'

    @staticmethod
    def is_number(char):
        return re.match(Grammar.NUMBER, char) or Grammar.is_exponent(char)

    @staticmethod
    def is_identifier(char):
        return re.match(Grammar.STRING, char)

    @staticmethod
    def is_exponent(char):
        return re.match(Grammar.EXPONENT, char)

    @staticmethod
    def is_ignored(char):
        return re.match(Grammar.IGNORE, char)

    @staticmethod
    def is_operator(char):
        return re.match(Grammar.OPERATOR, char)


class Lexer:
    text: str
    current_char: Optional[str]
    position: int

    def __init__(self, text):
        self.text = text
        self.position = 0
        self.current_char = self.text[self.position]
        self.tokens = []

    def forward(self):
        self.position += 1
        if self.position < len(self.text):
            self.current_char = self.text[self.position]
        else:
            self.current_char = None

    def peek(self):
        pos = self.position + 1
        if pos < len(self.text):
            return self.text[pos]

    def error(self, message=None):
        if not message:
            message = f'unexpected character at {self.position+1}'
        raise InterpreterError(message)

    def last_char(self):
        return self.position == len(self.text) - 1

    @staticmethod
    def convert_number(number):
        try:
            number = int(number)
        except ValueError:
            number = float(number)
        return number

    def number(self):
        _num = ''
        while self.current_char and Grammar.is_number(self.current_char) or self.current_char == '_':
            if self.current_char == '_':
                self.forward()
                continue
            if Grammar.is_exponent(self.current_char):
                if _num in ['', '.'] or self.last_char() or self.current_char in _num:
                    self.error()
            if self.current_char in ['+', '-']:
                if not Grammar.is_exponent(_num[-1]):
                    return Lexer.convert_number(_num)
            if self.current_char == '.':
                if self.current_char in _num or 'e' in _num or 'E' in _num:
                    self.error()

            _num += self.current_char
            self.forward()

        if _num[-1] in ['E', 'e', '+', '-'] or _num == '.':
            self.error()

        return Lexer.convert_number(_num)

    def identifier(self):
        _id = ''
        while self.current_char and (Grammar.is_identifier(self.current_char) or self.current_char.isdigit()):
            _id += self.current_char
            self.forward()
        token_type = TokenType.get(_id, TokenType.IDENTIFIER)
        return Token(token_type, _id)

    def operator(self):
        _op = ''
        while self.current_char and Grammar.is_operator(self.current_char):
            _op += self.current_char
            peek = self.peek()
            if peek and Grammar.is_operator(peek):
                peek_op = _op + peek
                if not TokenType.get(peek_op):
                    self.forward()
                    return _op
            self.forward()
        return _op

    def next_token(self):
        while self.current_char:
            if Grammar.is_ignored(self.current_char):
                self.forward()
                continue
            if Grammar.is_operator(self.current_char):
                operator = self.operator()
                token = Token(TokenType.get(operator), operator)
                self.tokens.append(token)
                return token
            if Grammar.is_identifier(self.current_char):
                token = self.identifier()
                self.tokens.append(token)
                return token
            if Grammar.is_number(self.current_char):
                token = Token(TokenType.NUMBER, self.number())
                self.tokens.append(token)
                return token
            self.error()
        return Token(TokenType.EOF, 'EOF')
