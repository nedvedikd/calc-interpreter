import re
import math
import operator as op_func
from calc_interpreter.lexer import TokenType
from calc_interpreter.singleton import Singleton
from calc_interpreter.exception import InterpreterError
from calc_interpreter.parser import Parser, Command, UnaryOperator, BinaryOperator, Number


def operator_func(operator):
    operations = {
        TokenType.PLUS: op_func.add,
        TokenType.MINUS: op_func.sub,
        TokenType.MUL: op_func.mul,
        TokenType.DIV: op_func.truediv,
    }
    return operations[operator]


def get_node_method_name(node):
    node_name = type(node).__name__
    name = re.sub(r'(?<!^)(?=[A-Z])', '_', node_name).lower()
    method = f'traverse_{name}'
    return method


def strip_decimal(number):
    frac, whole = math.modf(number)
    if frac == 0:
        return int(whole)
    return number


class CommandRunner:
    def __init__(self, parent):
        self.parent = parent

    def execute(self, command, arguments=None):
        callback = f'command_{command}'
        if callback not in dir(self):
            self.unknown_command(command)
        method = getattr(self, callback)
        return method(arguments)

    def unknown_command(self, command):
        raise InterpreterError(f'unknown command: {command}')

    def command_mode(self, arguments):
        modes_available = ['ast', 'rpn', 'default']
        usage = f'usage: mode (%s)' % ' | '.join(modes_available)
        if not arguments:
            raise InterpreterError(usage)
        mode = arguments[0]
        if mode not in modes_available:
            raise InterpreterError(usage)
        print('switching to mode', mode)
        self.parent.mode = mode


class NodeTraversal:
    def traverse(self, node):
        method = get_node_method_name(node)
        return getattr(self, method, self.default)(node)

    def default(self, node):
        method = get_node_method_name(node)
        raise ValueError(f'no method \'{method}\' defined!')


class Evaluator(NodeTraversal, metaclass=Singleton):
    parser: Parser
    mode: str
    runner: CommandRunner

    def __init__(self, parser):
        self.parser = parser
        self.mode = 'default'
        self.runner = CommandRunner(self)

    def set_parser(self, parser):
        self.parser = parser

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
        operation = operator_func(node.operator.type)
        return strip_decimal(operation(left, right))

    def traverse_unary_operator(self, node):
        """
        :type node: UnaryOperator
        """
        if node.operator.type == TokenType.PLUS:
            return +self.traverse(node.expr)
        elif node.operator.type == TokenType.MINUS:
            return -self.traverse(node.expr)

    def traverse_command(self, node):
        """
        :type node: Command
        """
        return self.runner.execute(node.operation, node.arguments)

    def evaluate(self):
        if not self.parser:
            raise ValueError('parser is not set! use set_parser method.')
        tree = self.parser.parse()
        if not tree:
            return ''
        return self.traverse(tree)
