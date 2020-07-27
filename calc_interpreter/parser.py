"""
Syntax Analysis

statement = command | bitwise_or | variable_assignment
variable_assignment = variable '=' bitwise_or
command = identifier {identifier}
bitwise_or = bitwise_xor {'|' bitwise_xor}
bitwise_xor = bitwise_and {'^' bitwise_and}
bitwise_and = bitwise_shift {'&' bitwise_shift}
bitwise_shift = expr {('<<'|'>>') expr}
expr = term {('+'|'-') term}
term = unary {('*'|'/'|'//'|'%') unary}
unary = ('+'|'-'|'~') unary | power
power = factor ['**' power]
factor = number | lparen bitwise_or rparen | variable
variable = identifier
"""
from __future__ import annotations
from typing import Optional, Union, List
from calc_interpreter.lexer import Lexer, Token, TokenType
from calc_interpreter.exception import InterpreterError


class NodeAST:
    pass


class BinaryOperator(NodeAST):
    left: Optional[NodeAST]
    token: Token
    operator: Token
    right: Optional[NodeAST]

    def __init__(self, left, operator, right):
        self.left = left
        self.token = self.operator = operator
        self.right = right


class UnaryOperator(NodeAST):
    token: Token
    operator: Token
    expr: NodeAST

    def __init__(self, operator, expr):
        self.token = self.operator = operator
        self.expr = expr


class Number(NodeAST):
    token: Token
    value: Union[int, float]

    def __init__(self, token):
        self.token = token
        self.value = token.value


class Command(NodeAST):
    operation: Token
    arguments: List[Token]

    def __init__(self, operation, arguments):
        self.operation = operation
        self.arguments = arguments


class VariableAssignment(NodeAST):
    left: Variable
    right: NodeAST

    def __init__(self, left, right):
        self.left = left
        self.right = right


class Variable(NodeAST):
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

    def error(self, error=None):
        if not error:
            error = f'syntax error at {self.lexer.position+1}'
        raise InterpreterError(error)

    def expect(self, token_type):
        if self.token.type == token_type:
            self.token = self.lexer.next_token()
        else:
            self.error()

    def variable(self):
        node = Variable(self.token)
        self.expect(TokenType.IDENTIFIER)
        return node

    def variable_assignment(self, left):
        self.expect(TokenType.ASSIGN)
        node = VariableAssignment(left, self.bitwise_or())
        return node

    def _bitwise_boilerplate(self, operation, tokens):
        """
        :type operation: Callable[NodeAST]
        :param tokens: List[Token]
        :rtype: NodeAST
        """
        node = operation()
        if self.token.type in tokens:
            token = self.token
            self.expect(token.type)
            return BinaryOperator(node, token, operation())
        return node

    def bitwise_or(self):
        return self._bitwise_boilerplate(self.bitwise_xor, [TokenType.BITWISE_OR])

    def bitwise_xor(self):
        return self._bitwise_boilerplate(self.bitwise_and, [TokenType.BITWISE_XOR])

    def bitwise_and(self):
        return self._bitwise_boilerplate(self.bitwise_shift, [TokenType.BITWISE_AND])

    def bitwise_shift(self):
        return self._bitwise_boilerplate(self.expr, [TokenType.BITWISE_LEFT_SHIFT, TokenType.BITWISE_RIGHT_SHIFT])

    def expr(self):
        node = self.term()
        while self.token.type in [TokenType.PLUS, TokenType.MINUS]:
            token = self.token
            self.expect(self.token.type)
            node = BinaryOperator(node, token, self.term())
        return node

    def term(self):
        node = self.unary()
        while self.token.type in [TokenType.MUL, TokenType.DIV, TokenType.FLOOR_DIV, TokenType.MODULUS]:
            token = self.token
            self.expect(self.token.type)
            node = BinaryOperator(node, token, self.unary())
        return node

    def unary(self):
        token = self.token
        if token.type in [TokenType.PLUS, TokenType.MINUS, TokenType.BITWISE_NOT]:
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
            node = self.bitwise_or()
            self.expect(TokenType.RPAREN)
            return node
        else:
            return self.variable()

    def command(self):
        command = self.token
        arguments = []
        if TokenType.get(command.value):
            self.expect(command.type)
            while self.token.type != TokenType.EOF:
                arguments.append(self.token)
                self.expect(TokenType.IDENTIFIER)
            return Command(command, arguments)

    def statement(self):
        if self.token.type == TokenType.IDENTIFIER and TokenType.get(self.token.value):
            node = self.command()
        else:
            prev = self.token.type
            node = self.bitwise_or()
            if len(self.lexer.tokens) == 2 and self.token.type == TokenType.ASSIGN:
                if prev != TokenType.IDENTIFIER:
                    self.error('syntax error: cannot assign to literal')
                else:
                    node = self.variable_assignment(node)
        if self.token.type != TokenType.EOF:
            self.error()
        return node

    def parse(self):
        node = self.statement()
        return node
