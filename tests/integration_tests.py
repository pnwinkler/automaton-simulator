# this file tests that the following components interact as expected:
#  automaton/node input processors
#  regex_generator
#  pass / fail string generator
# i.e. starting from a given regex, do we generate appropriate strings
#  that the automaton appropriately accepts or rejects?
# NOTE: this file assumes that all automaton_logic_test tests were passed

from simulator.automaton_logic import *
from simulator.regex_generator import *
from simulator.generate_strings_from_regex import *

def helper_ReturnNewAutomatonAnd2NodeObj():
    zzz = Automaton()
    return zzz, zzz.takeIDReturnNodeObject(zzz.addStateReturnID()), zzz.takeIDReturnNodeObject(zzz.addStateReturnID())

# test that valid strings are created from generated regexes,
#  and that these strings are correctly accepted or rejected by automata
def test_automata_with_generated_strings():
    # This test:
    #  1) provides a mock regex (for the sake of testing)
    #  2) generates pass/fail strings for that regex
    #  3) asserts that the automaton accepts all pass strings and rejects all fail strings
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    a.addTransition(node.identifier, node2.identifier, 'a')
    a.addTransition(node.identifier, node2.identifier, 'b')
    a.flipAcceptingOrRejecting(node2.identifier)

    # cursory regex generator checks
    tmp_reg = generateRegex("medium")
    assert tmp_reg != None
    assert tmp_reg != ''
    assert any(g in tmp_reg for g in ['*', '(',')', '|'])

    # using the regex that describes the language of the automaton above,
    # generate test strings
    test_reg1 = 'a|b'
    pass_strings, fail_strings = generate_Strings_from_reg(test_reg1)

    # test the automaton on all test strings
    for ps in pass_strings:
        assert a.determineWholeInputAcceptance(ps) == True
    for fs in fail_strings:
        assert a.determineWholeInputAcceptance(fs) == False


    # test with 3 node automaton
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    node3 = a.takeIDReturnNodeObject(a.addStateReturnID())
    a.addTransition(node.identifier, node2.identifier, 'a')
    a.addTransition(node2.identifier, node3.identifier, 'b')
    a.addTransition(node3.identifier, node.identifier, 'a')
    a.flipAcceptingOrRejecting(node.identifier)
    a.flipAcceptingOrRejecting(node3.identifier)

    # using the regex that describes the language of the automaton above,
    # generate test strings
    test_reg2 = '(ab)|((aba)*|(abaaba)*)*'
    pass_strings, fail_strings = generate_Strings_from_reg(test_reg2)

    # test the automaton on all test strings
    # generating and testing 27 strings takes 0.016671975987264886 seconds
    debug_trace = False
    for ps in pass_strings:
        if debug_trace: print(ps)
        assert a.determineWholeInputAcceptance(ps, debug_trace) == True
    for fs in fail_strings:
        assert a.determineWholeInputAcceptance(fs, debug_trace) == False
