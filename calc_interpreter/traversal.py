import re


def get_node_method_name(node):
    node_name = type(node).__name__
    name = re.sub(r'(?<!^)(?=[A-Z])', '_', node_name).lower()
    method = f'traverse_{name}'
    return method


class NodeTraversal:
    def traverse(self, node):
        method = get_node_method_name(node)
        return getattr(self, method, self.default)(node)

    def default(self, node):
        method = get_node_method_name(node)
        raise ValueError(f'no method \'{method}\' defined!')
