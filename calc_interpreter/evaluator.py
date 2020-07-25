import math
import operator as op_func
from typing import List, Optional
from calc_interpreter.lexer import Token
from calc_interpreter.traversal import NodeTraversal
from calc_interpreter.singleton import Singleton
from calc_interpreter.parser import *


def operator_func(operator):
    operations = {
        TokenType.BITWISE_OR: op_func.or_,
        TokenType.BITWISE_XOR: op_func.xor,
        TokenType.BITWISE_AND: op_func.and_,
        TokenType.BITWISE_RIGHT_SHIFT: op_func.rshift,
        TokenType.BITWISE_LEFT_SHIFT: op_func.lshift,
        TokenType.PLUS: op_func.add,
        TokenType.MINUS: op_func.sub,
        TokenType.MUL: op_func.mul,
        TokenType.DIV: op_func.truediv,
        TokenType.FLOOR_DIV: op_func.floordiv,
        TokenType.MODULUS: op_func.mod,
        TokenType.POW: op_func.pow
    }
    return operations[operator]


def strip_decimal(number):
    frac, whole = math.modf(number)
    if frac == 0:
        return int(whole)
    return number


class CommandRunner:
    def __init__(self, parent):
        self.parent = parent

    def execute(self, command, arguments=None):
        """
        :type command: Token
        :type arguments: Optional[List[Token]]
        """
        callback = f'command_{command.value}'
        if callback not in dir(self):
            self.unknown_command(command)
        method = getattr(self, callback)
        return method(arguments)

    def unknown_command(self, command):
        """
        :type command: Token
        """
        raise InterpreterError(f'unknown command: {command.value}')

    def command_mode(self, arguments):
        """
        :type arguments: List[Token]
        """
        modes_available = ['ast', 'rpn', 'tokens', 'default']
        usage = f'usage: mode (%s)' % ' | '.join(modes_available)
        if not arguments:
            raise InterpreterError(usage)
        mode = arguments[0].value
        if mode not in modes_available:
            raise InterpreterError(usage)
        print('switching to mode:', mode)
        self.parent.mode = mode


class Evaluator(NodeTraversal, metaclass=Singleton):
    tree: NodeAST
    mode: str
    runner: CommandRunner
    memory: dict

    def __init__(self, tree):
        self.tree = tree
        self.mode = 'default'
        self.runner = CommandRunner(self)
        self.memory = {}

    def traverse_number(self, node):
        """
        :type node: Number
        """
        return strip_decimal(node.value)

    def traverse_binary_operator(self, node):
        """
        :type node: BinaryOperator
        """
        left = self.traverse(node.left)
        right = self.traverse(node.right)
        if self.mode == 'default':
            try:
                operation = operator_func(node.operator.type)
                return strip_decimal(operation(left, right))
            except ZeroDivisionError:
                raise InterpreterError('zero division')
            except TypeError:
                raise InterpreterError('complex numbers are not supported')
        elif self.mode == 'rpn':
            return f'{left} {right} {node.operator.value}'

    def traverse_unary_operator(self, node):
        """
        :type node: UnaryOperator
        """
        right = self.traverse(node.expr)
        if self.mode == 'default':
            if node.operator.type == TokenType.PLUS:
                return +right
            elif node.operator.type == TokenType.MINUS:
                return -right
            elif node.operator.type == TokenType.BITWISE_NOT:
                return ~right
        elif self.mode == 'rpn':
            return f'{right} {node.operator.value}'

    def traverse_command(self, node):
        """
        :type node: Command
        """
        return self.runner.execute(node.operation, node.arguments)

    def traverse_variable_assignment(self, node):
        """
        :type node: VariableAssignment
        """
        self.memory[node.left.value] = self.traverse(node.right)

    def traverse_variable(self, node):
        """
        :type node: Variable
        """
        try:
            return self.memory[node.value]
        except KeyError:
            raise InterpreterError(f'undefined variable: {node.value}')

    def evaluate(self):
        tree = self.tree
        if not tree:
            return ''
        return self.traverse(tree)
