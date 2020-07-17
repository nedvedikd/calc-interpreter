import re
import math
import operator as op_func
from calc_interpreter.lexer import TokenType
from calc_interpreter.parser import Parser


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


class NodeTraversal:
    def traverse(self, node):
        method = get_node_method_name(node)
        return getattr(self, method, self.default)(node)

    def default(self, node):
        method = get_node_method_name(node)
        raise ValueError(f'no method \'{method}\' defined!')


class Evaluator(NodeTraversal):
    parser: Parser

    def __init__(self, parser):
        self.parser = parser

    def traverse_number(self, node):
        return strip_decimal(node.value)

    def traverse_binary_operator(self, node):
        left = self.traverse(node.left)
        right = self.traverse(node.right)
        operation = operator_func(node.operator.type)
        return strip_decimal(operation(left, right))

    def traverse_unary_operator(self, node):
        if node.operator.type == TokenType.PLUS:
            return +self.traverse(node.expr)
        elif node.operator.type == TokenType.MINUS:
            return -self.traverse(node.expr)

    def interpret(self):
        tree = self.parser.parse()
        if not tree:
            return ''
        return self.traverse(tree)
