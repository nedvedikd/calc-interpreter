from calc_interpreter.lexer import Lexer
from calc_interpreter.parser import Parser
from calc_interpreter.evaluator import Evaluator
from calc_interpreter.exception import InterpreterError


def main():
    prompt = ':: '
    while True:
        try:
            data = input(prompt)
            lexer = Lexer(data)
            parser = Parser(lexer)
            tree = parser.parse()
            evaluator = Evaluator(tree)
            result = evaluator.evaluate()
            if evaluator.mode == 'tokens':
                for token in lexer.tokens:
                    if token.value == 'mode':
                        break
                    print(token)
            elif result:
                print(result)
        except (EOFError, KeyboardInterrupt):
            break
        except InterpreterError as err:
            print(err)


if __name__ == '__main__':
    main()
