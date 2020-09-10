# takes the regex, generates and returns sorted lists for pass and fail strings,
# for use in automaton testing.

import exrex
import random
import re


def generate_Strings_from_reg(reg):
    # passes the regex, and therefore should pass the automaton
    pass_strings = set({})

    # fails the regex, and therefore should fail the automaton
    fail_strings = set({})

    # the numbers below are trial and error. It's a tradeoff
    # I want a large collection of short strings, but generating them is expensive
    for x in range(100):
        pass_strings.add(exrex.getone(reg, 4))

    # extract alphabet from reg
    alphabet = {c for c in reg if c.isalnum()}

    # brackets are needed so that the expression takes up the whole line
    # else, regex associates $ and ^ with the closest group, not the whole regex
    reg = '^(' + reg + ')$'
    local_re = re.compile(reg)

    # add test for the empty string to the right category
    if local_re.search(''):
        pass_strings.add('')
    else:
        fail_strings.add('')

    # generate fail strings of similar length to pass strings, then add them to fail_strings
    # if of exactly equivalent length, it can be impossible to generate enough fails for a regex like 'a|b'
    def add_str_to_fail_strings():
        for ps in pass_strings:
            fail_strings.add(
                ''.join(random.choice(list(alphabet)) for z in range(random.randrange(len(ps) + 1))))

    # removes pass strings from fail_strings
    def remove_passes_from_fail_strings():
        # cannot change set size during iteration. Therefore, we use to_remove
        to_remove = []
        for s in fail_strings:
            if local_re.match(s):
                to_remove.append(s)
        for s in to_remove:
            fail_strings.remove(s)

    # generate an almost equivalent number of fail_strings to pass_strings
    # the -1 is to prevent infinite loops for tiny regexes, like 'a|b.
    count = 0
    while len(fail_strings) < len(pass_strings) - 1:
        add_str_to_fail_strings()
        remove_passes_from_fail_strings()
        count += 1
        if count == 3:
            # our infinite loop breaker. Needed only in rare circumstances, with super-short regexes
            break

    # If insufficient fail strings are generated, generate more
    # That can occur because super simple regexes generate few pass strings
    if len(fail_strings) < 3:
        for x in range(2):
            fail_strings.add(''.join(random.choice(list(alphabet)) for z in range(random.randrange(3))))
            fail_strings.add(''.join(random.choice(list(alphabet)) for z in range(random.randrange(4))))
            fail_strings.add(''.join(random.choice(list(alphabet)) for z in range(random.randrange(5))))
        remove_passes_from_fail_strings()

    return sorted(list(pass_strings), key=len), sorted(list(fail_strings), key=len)


if __name__ == '__main__':
    # ps, fs = generate_Strings_from_reg('a|b', 10, 5)
    # print('pass strings:', ps)
    # print('fail strings:', fs)

    # ps, fs = generate_Strings_from_reg('c*b*bb')
    # print(f'pass strings, len{len(ps)}:', ps)
    # print(f'fail strings, len{(len(fs))}:', fs)

    # ps, fs = generate_Strings_from_reg('(abaab)*|ab')
    # print(f'pass strings, len{len(ps)}:', ps)
    # print(f'fail strings, len{(len(fs))}:', fs)

    ps, fs = generate_Strings_from_reg('(ab)|((aba)*|(abaab)*)*')
    print(f'pass strings, len={len(ps)}:', ps)
    print(f'fail strings, len={(len(fs))}:', fs)