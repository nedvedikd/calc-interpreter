"""
Syntax Analysis

statement = command | expr
command = string {string}
expr = term {('+'|'-') term}
term = unary {('*'|'/') unary}
unary = ('+'|'-') unary | power
power = factor ['**' power]
factor = number | lparen expr rparen
"""
from __future__ import annotations
from typing import Optional, Union, List
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


class Command:
    operation: Token
    arguments: List[Token]

    def __init__(self, operation, arguments):
        self.operation = operation
        self.arguments = arguments


class Parser:
    lexer: Lexer
    token: Token

    def __init__(self, lexer):
        self.lexer = lexer
        self.token = self.lexer.next_token()

    def error(self):
        raise InterpreterError(f'syntax error at {self.lexer.position+1}')

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
        node = self.unary()
        while self.token.type in [TokenType.MUL, TokenType.DIV]:
            token = self.token
            self.expect(self.token.type)
            node = BinaryOperator(node, token, self.unary())
        return node

    def unary(self):
        token = self.token
        if token.type in [TokenType.PLUS, TokenType.MINUS]:
            self.expect(token.type)
            node = UnaryOperator(token, self.unary())
        else:
            node = self.power()
        return node

    def power(self):
        node = self.factor()
        token = self.token
        if token.type == TokenType.POW:
            self.expect(token.type)
            node = BinaryOperator(node, token, self.power())
        return node

    def factor(self):
        token = self.token
        if token.type == TokenType.NUMBER:
            self.expect(token.type)
            return Number(token)
        elif token.type == TokenType.LPAREN:
            self.expect(token.type)
            node = self.expr()
            self.expect(TokenType.RPAREN)
            return node
        self.error()

    def command(self):
        token = self.token
        operation = self.token
        arguments = []
        if token.type == TokenType.STRING:
            self.expect(token.type)
            while self.token.type != TokenType.EOF:
                arguments.append(self.token)
                self.expect(TokenType.STRING)
            return Command(operation, arguments)

    def statement(self):
        node = self.command()
        if not node:
            node = self.expr()
            if self.token.type != TokenType.EOF:
                self.error()
        return node

    def parse(self):
        node = self.statement()
        return node
