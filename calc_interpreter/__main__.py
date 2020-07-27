from calc_interpreter.evaluator import interpret


def main():  # pragma: no cover
    while True:
        try:
            data = input(':: ')
            if not data:
                continue
            interpret(data)
        except (EOFError, KeyboardInterrupt):
            break


if __name__ == '__main__':
    main()
