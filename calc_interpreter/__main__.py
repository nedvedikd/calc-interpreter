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
            evaluator = Evaluator(parser)
            result = evaluator.interpret()
            print(result)
        except (EOFError, KeyboardInterrupt):
            break
        except InterpreterError as err:
            print(err)


main()