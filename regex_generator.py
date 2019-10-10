# generate simple regexes (length roughly 3 to 6, alphabet 2-3 chars)
# these regexes may be used to:
#  give user problems to solve, allow me to generate automata

# todo: consider lengthening strings when brackets are present
# todo: consider implementing '+'
# todo: consider providing weights for grammar vs alphabet selection (i.e. allow grammar frequency to be tweaked)

# decided against simplifying with exrex because output confusing: "a*a|cb" -> "(?:a*a|cb)"
import random


def generateRegex(difficulty):
    # difficulty is a string, one of the 3 options seen below

    # length is an int, usually between 3-6
    # alphabet_count is an int 2-3
    if difficulty == 'easy':
        length = 3
        alphabet_count = 2
    elif difficulty == 'medium':
        length = 5
        alphabet_count = 2
    elif difficulty == 'hard':
        length = 6
        alphabet_count = 3
    else:
        raise ValueError(f'invalid \'difficulty\' argument given to generateRegex: \'{difficulty}\'')

    # legacy, but provide useful indicators on appropriate sizes
    # if alphabet_count != 2 and alphabet_count != 3:
    #     alphabet_count = 2
    #     print(f'generateRegex given too large or too small an alphabet. Defaulting to {alphabet_count}')
    #
    # if length < 3 or length > 6:
    #     length = 5
    #     print(f'generateRegex given too large or too small a length. Defaulting to {length}')

    tmp = ['a', 'b', 'c']
    valid_alphabet = tmp[:alphabet_count]
    grammar_symbols = ['*', '|', '(', ')']
    all_symbols = valid_alphabet + grammar_symbols

    # while True is here to keep program re-generating regexes until a valid one is found
    # prevents it from returning None
    while True:
        retstr = ''
        while len(retstr) < length:
            # candidate character for retstr
            random_choice = random.choice(all_symbols)

            # choose another symbol if the first would be a grammar symbol
            if len(retstr) == 0 and random_choice in grammar_symbols:
                continue

            # prevent 2 grammar symbols from following each other
            # unless they form ')*'
            if len(retstr) > 1 and random_choice in grammar_symbols:
                if retstr[-1] == ')' and random_choice == '*':
                    pass
                elif retstr[-1] in grammar_symbols:
                    continue

            # close open brackets, if not already closed
            if len(retstr) == length - 1 and '(' in retstr and ')' not in retstr:
                retstr += ')'

            # if there's no space for a closing bracket, don't add an opening bracket
            if (len(retstr) == length - 1 and random_choice == '(') or (len(retstr) == length and random_choice == '('):
                continue

            # don't add '|' as the final symbol
            if (len(retstr) == length - 1 and random_choice == '|') or (len(retstr) == length and random_choice == '|'):
                continue

            # if there's no opening bracket, don't add a closing bracket
            if '(' not in retstr and random_choice == ')':
                continue

            # if there's an opening bracket, but no closing bracket, don't add another opening bracket
            if ('(' in retstr and ')' not in retstr) and random_choice == '(':
                continue

            retstr += random_choice

            # assert no '|)'
            retstr = retstr.replace('|)', ')')
            retstr = retstr.replace('|)', ')')

            # remove a|a , b|b type strings
            tmp = retstr.split('|')
            # clause means letter or group of letters, e.g. 'a' or 'ab'
            for clause in tmp:
                if tmp.count(clause) > 1:
                    retstr = retstr.replace(clause, '', 1)
                    retstr = retstr.replace('|', '', 1)

            # replace redundant parantheses in expressions like 'b(a*)a'
            if '(' in retstr and '*)' in retstr:
                if (retstr.index('*)') - retstr.index('(') == 2):
                    retstr = retstr.replace('(', '', 1)
                    retstr = retstr.replace('*)', '', 1)

            retstr = retstr.replace('))', ')')
            retstr = retstr.replace('()', '')

        # triviality / grammar checks
        # assert that brackets have contents, not like 'aba()'. This could be more efficiently implemented above
        # in fact, most of these checks could be made more efficient by being put above,
        # then removing the offending characters from the string and continuing!

        # trivial: contents are in form '...(a)...'
        # solution: remove '(a)' from string
        if '(' in retstr:
            if retstr.index(')') - retstr.index('(') == 2 and ')*' not in retstr:
                retstr = retstr[:retstr.index('(')] + retstr[retstr.index(')') + 1:]

        # assert grammar in regex
        if any(g in retstr for g in grammar_symbols):
            return retstr

        # trivial: no grammar in regex. We let it loop again
        pass


if __name__ == '__main__':
    rstr = ''
    count = 0

    import exrex

    # every time count is less than X in range(X), we've discarded a string. This happens roughly 1/5 times
    print('Regex\tLength\tSample accepted string')
    for i in range(10):
        # rstr = generateRegex('easy')
        rstr = generateRegex('medium')
        # rstr = generateRegex('hard')
        if rstr:
            count += 1
            # print(count, rstr, len(rstr), '\t', end='\t')
            print(count, rstr, len(rstr), end='     \t')
            # NOTE: exrex doesn't tightly stick to the character limit
            # and if it receives an invalid regex it returns '' or raises an error
            # it accepts regexes like 'b|'
            print(exrex.getone(rstr, 5))
