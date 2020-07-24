# Calc Interpreter

This repo was created solely to learn more about processes of Lexical and Syntax Analysis
to tokenize, parse and evaluate input.

## How it works?

Given the input `(25 - 5) * 3` the lexer is able to produce tokens as follows:
```
Token(type='LPAREN', value='(')
Token(type='NUMBER', value=25)
Token(type='MINUS', value='-')
Token(type='NUMBER', value=5)
Token(type='RPAREN', value=')')
Token(type='MUL', value='*')
Token(type='NUMBER', value=3)
```

Parser then creates AST (Abstract Syntax Tree) out of tokens:

```   
    *
   / \
  -   3
 / \
25  5
```

And finally evaluator is able to traverse in post-order depth-first manner to 
evaluate the AST:
```
25 - 5
20 * 3
60
```

### Grammar

Interpreter is based on this set of rules (EBNF):

```
statement           =   command | expr | variable_assignment
command             =   string {string}
variable_assignment =   variable '=' expr
expr                =   term {('+'|'-') term}
term                =   unary {('*'|'/','//','%') unary}
unary               =   ('+'|'-'|'~') unary | power
power               =   factor ['**' power]
factor              =   number | lparen expr rparen | variable
variable            =   identifier
identifier          =   letter {digit | letter}
letter              =   A-Za-z
number              =   (sep integer | integer sep | integer) {integer} [exponent]
exponent            =   ('e'|'E') ['+'|'-'] integer
integer             =   digit {digit}
sep                 =   '.'
digit               =   0-9
```

### Features
* Wide range of number formats:
    * `1`, `2.2`, `2.5e4`, `.5e-2`, `1_000_000e-3` etc.
* Variables `a = 145`
* Different modes via `mode (rpn | tokens | default)`
    * `rpn` = prints input in Reverse-Polish Notation
    * `tokens` = prints tokens
    * `default` = switch back to normal evaluation
* Operations:
    * Parentheses `()`
    * Exponent `**`
    * Unary plus `+a`, Unary minus `-a`, Bitwise NOT `~a`
    * Multiplication `*`, Division `/`, Floor Division `//`, Modulus `%`
    * Addition `+`, Subtraction `-`
    
    
### Example
```
:: a = 90 - 38 * 2
:: b = a - 2
:: 12 * b
144
```

## Installation and Usage

Only requirement is Python 3.8.3 or higher.

```bash
git clone git@github.com:nedvedikd/calc-interpreter.git
python -m pip install ./calc-interpreter --user
```

```bash
python -m calc_interpreter
:: 8 ** (1/3)
2
```

---

**Credits:** [Excellent series of blog posts on this topic by Ruslan Spivak](https://ruslanspivak.com/lsbasi-part1/)