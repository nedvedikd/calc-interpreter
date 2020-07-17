"""
Syntax analysis

expr = term {('+'|'-') term}
term = factor {('*'|'/') factor}
factor = ('+'|'-') factor | number | lparen expr rparen
"""
from __future__ import annotations
from typing import Optional, Union
from calc_interpreter.lexer import Lexer, Token, TokenType
from calc_interpreter.exception import InterpreterError


class BinaryOperator:
    left: Optional[Union[BinaryOperator, Number]]
    token: Token
    operator: Token
    right: Optional[Union[BinaryOperator, Number]]

    def __init__(self, left, operator, right):
        self.left = left
        self.token = self.operator = operator
        self.right = right


class UnaryOperator:
    token: Token
    operator: Token

    def __init__(self, operator, expr):
        self.token = self.operator = operator
        self.expr = expr


class Number:
    token: Token

    def __init__(self, token):
        self.token = token
        self.value = token.value


class Parser:
    lexer: Lexer
    token: Token

    def __init__(self, lexer):
        self.lexer = lexer
        self.token = self.lexer.next_token()

    def error(self):
        return InterpreterError("syntax error", self.lexer.position)

    def expect(self, token_type):
        if self.token.type == token_type:
            self.token = self.lexer.next_token()
        else:
            self.error()

    def expr(self):
        node = self.term()
        while self.token.type in [TokenType.PLUS, TokenType.MINUS]:
            token = self.token
            self.expect(self.token.type)
            node = BinaryOperator(node, token, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.token.type in [TokenType.MUL, TokenType.DIV]:
            token = self.token
            self.expect(self.token.type)
            node = BinaryOperator(node, token, self.factor())
        return node

    def factor(self):
        token = self.token
        if token.type in [TokenType.PLUS, TokenType.MINUS]:
            self.expect(token.type)
            node = UnaryOperator(token, self.factor())
            return node
        elif token.type == TokenType.NUMBER:
            self.expect(token.type)
            return Number(token)
        elif token.type == TokenType.LPAREN:
            self.expect(token.type)
            node = self.expr()
            self.expect(TokenType.RPAREN)
            return node

    def parse(self):
        node = self.expr()
        if self.token.type != TokenType.EOF:
            self.error()
        return node
