"""
Lexical Analyzer

number = (sep integer | integer sep | integer) {integer} [('e'|'E') ['+'|'-'] {integer}]
integer = digit {digit}*
sep = '.'
digit = 0-9
"""

import re
from enum import Enum, auto
from typing import Optional
from dataclasses import dataclass
from calc_interpreter.exception import InterpreterError


class TokenType(Enum):
    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()
    POW = auto()
    LPAREN = auto()
    RPAREN = auto()
    STRING = auto()
    NUMBER = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: [float, int, str]


class Grammar:
    NUMBER = r'[0-9.\+-]'
    OPERATOR = r'[\+\-/\*()]'
    STRING = r'[A-Za-z]'
    IGNORE = r'[\s_]'
    EXPONENT = r'[eE]'

    @staticmethod
    def is_number(char):
        return re.match(Grammar.NUMBER, char) or Grammar.is_exponent(char)

    @staticmethod
    def is_string(char):
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

    @staticmethod
    def operator_type(operator):
        operator_dict = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MUL,
            '/': TokenType.DIV,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN
        }
        return operator_dict[operator]


class Lexer:
    text: str
    current_char: Optional[str]
    position: int

    def __init__(self, text):
        self.text = text
        self.position = 0
        self.current_char = self.text[self.position]

    def forward(self):
        self.position += 1
        if self.position <= len(self.text) - 1:
            self.current_char = self.text[self.position]
        else:
            self.current_char = None

    def error(self):
        raise InterpreterError('lexer error', self.position+1)

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
        number = ''
        while self.current_char and Grammar.is_number(self.current_char) or self.current_char == '_':
            if self.current_char == '_':
                self.forward()
                continue
            if Grammar.is_exponent(self.current_char):
                if number in ['', '.'] or self.last_char() or self.current_char in number:
                    self.error()
            if self.current_char in ['+', '-']:
                if not Grammar.is_exponent(number[-1]):
                    return Lexer.convert_number(number)
            if self.current_char == '.':
                if self.current_char in number or 'e' in number or 'E' in number:
                    self.error()

            number += self.current_char
            self.forward()

        if number[-1] in ['E', 'e', '+', '-'] or number == '.':
            self.error()

        return Lexer.convert_number(number)

    def string(self):
        string = ''
        while self.current_char and Grammar.is_string(self.current_char):
            string += self.current_char
            self.forward()
        return string

    def next_token(self):
        while self.current_char:
            if Grammar.is_ignored(self.current_char):
                self.forward()
                continue

            if Grammar.is_operator(self.current_char):
                operator_type = Grammar.operator_type(self.current_char)
                token = Token(operator_type, self.current_char)
                self.forward()
                return token

            if Grammar.is_number(self.current_char):
                return Token(TokenType.NUMBER, self.number())

            if Grammar.is_string(self.current_char):
                return Token(TokenType.STRING, self.string())

            self.error()

        return Token(TokenType.EOF, 'EOF')
