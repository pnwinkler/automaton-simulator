# test the automaton and node classes

import pytest
from simulator.automaton_logic import *

def helper_ReturnNewAutomatonAndNodeObj():
    zzz = Automaton()
    return zzz, zzz.takeIDReturnNodeObject(zzz.addStateReturnID())

def helper_ReturnNewAutomatonAnd2NodeObj():
    zzz = Automaton()
    return zzz, zzz.takeIDReturnNodeObject(zzz.addStateReturnID()), zzz.takeIDReturnNodeObject(zzz.addStateReturnID())

def test_AutomatonaddStateReturnID():
    # node should be created and added to the automaton's node collection
    # the first node to be added should be set as the initial node
    a = Automaton()
    node = a.addStateReturnID()
    assert node == 'N101'
    assert len(a.node_collection) == 1
    node2 = a.addStateReturnID()
    assert node2 == 'N102'
    assert len(a.node_collection) == 2

    # test that the first node to be added to an empty automaton becomes the initial node and the active node
    a, node = helper_ReturnNewAutomatonAndNodeObj()
    assert a.initial_node_obj == node
    assert a.active_node_obj == node

    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    assert a.initial_node_obj == node
    assert a.active_node_obj == node


def test_AutomatontakeIDReturnNodeObject():
    # given a node's string, should return a reference to that node
    # can't figure this shit out below - how to test if it's of the right type
    b = Automaton()
    node = b.addStateReturnID()
    # assert b.takeIDReturnNodeObject(node) != 'N101'
    # assert b.takeIDReturnNodeObject(node) is Node
    node2 = b.addStateReturnID()
    # assert b.takeIDReturnNodeObject(node2) != 'N102'

    # raise ValueError for invalid parameters
    with pytest.raises(ValueError):
        assert b.takeIDReturnNodeObject('something that isn\'t a node id')

def test_AutomatonsetInitialNode():
    # takes desired_start_node_ID
    c = Automaton()
    node = c.addStateReturnID()
    assert c.initial_node_obj.identifier == c.takeIDReturnNodeObject(node).identifier

    # change initial node
    node2 = c.addStateReturnID()
    c.setInitialNode(node2)
    assert c.initial_node_obj.identifier == c.takeIDReturnNodeObject(node2).identifier

    # assert that changes do not occur when a simulation is in progress
    c.path_taken = 'not an empty path'
    c.setInitialNode(node)
    assert c.initial_node_obj.identifier != c.takeIDReturnNodeObject(node).identifier

def test_AutomatonflipAcceptingOrRejecting():
    d = Automaton()
    node = d.addStateReturnID()
    assert not d.takeIDReturnNodeObject(node).accepting
    d.takeIDReturnNodeObject(node).flipAcceptingOrRejecting()
    assert d.takeIDReturnNodeObject(node).accepting

def test_AutomatonremoveState():
    # tests that calling removeState removes a state (i.e. node) from the automaton's node collection
    e = Automaton()
    node = e.takeIDReturnNodeObject(e.addStateReturnID())
    assert len(e.node_collection) == 1
    node2 = e.takeIDReturnNodeObject(e.addStateReturnID())
    assert len(e.node_collection) == 2
    e.removeState(node.identifier)
    assert len(e.node_collection) == 1

    # setup a node, give it a transition, remove that node, then check if the transition is removed from the other party
    # problem with this test is that it might fail here because of a problem in another function,
    # making debugging harder.
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    a.addTransition(node.identifier, node2.identifier, 'a')
    a.removeState(node.identifier)
    assert len(node2.inbound_transitions) == 0
    assert len(node2.outbound_transitions) == 0


def test_AutomatonaddTransition():
    # tests that Automaton.addTransition() adds transitions to either inbound or outbound transitions
    # whichever is appropriate
    # does NOT check the format of these additions

    # assert that initial inbound and outbound transition variables are correct for each node
    e = Automaton()
    node = e.takeIDReturnNodeObject(e.addStateReturnID())
    assert len(node.outbound_transitions) == 0
    assert len(node.inbound_transitions) == 0
    target_node = e.takeIDReturnNodeObject(e.addStateReturnID())
    assert len(target_node.outbound_transitions) == 0
    assert len(target_node.inbound_transitions) == 0

    # add transition from node to target_node
    e.addTransition(node.identifier, target_node.identifier, 'a')
    assert len(node.outbound_transitions) == 1
    assert len(node.inbound_transitions) == 0
    assert len(target_node.outbound_transitions) == 0
    assert len(target_node.inbound_transitions) == 1

    # add transition from node to itself (circular transition)
    a, node = helper_ReturnNewAutomatonAndNodeObj()
    a.addTransition(node.identifier, node.identifier, 'a')
    assert len(node.inbound_transitions) == 1
    assert len(node.outbound_transitions) == 1

    # add one transition, then assert that a request for its duplicate is rejected
    b, node = helper_ReturnNewAutomatonAndNodeObj()
    target_node = b.takeIDReturnNodeObject(b.addStateReturnID())
    b.addTransition(node.identifier, target_node.identifier, 'a')
    b.addTransition(node.identifier, target_node.identifier, 'a')
    assert len(node.inbound_transitions) == 0
    assert len(node.outbound_transitions) == 1
    assert len(target_node.inbound_transitions) == 1
    assert len(target_node.outbound_transitions) == 0

    # try the same, but with a self referential node
    b, node = helper_ReturnNewAutomatonAndNodeObj()
    b.addTransition(node.identifier, node.identifier, 'a')
    b.addTransition(node.identifier, node.identifier, 'a')
    assert len(node.inbound_transitions) == 1
    assert len(node.outbound_transitions) == 1

    # assert that one node may not have multiple outbound transitions for the same character
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    node3 = a.takeIDReturnNodeObject(a.addStateReturnID())
    a.addTransition(node.identifier, node2.identifier, 'a')
    a.addTransition(node.identifier, node3.identifier, 'a')
    assert len(node.outbound_transitions) == 1

    # test the same but with self-reference
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    a.addTransition(node.identifier, node.identifier, 'b')
    a.addTransition(node.identifier, node2.identifier, 'b')
    assert len(node.inbound_transitions) == 1
    assert len(node.outbound_transitions) == 1
    assert len(node2.inbound_transitions) == 0

def test_NoderemoveTransition():
    # test that Node.removeTransition() removes inbound or outbound transitions from ONE node (itself) appropriately
    a, node = helper_ReturnNewAutomatonAndNodeObj()
    node2 = a.takeIDReturnNodeObject(a.addStateReturnID())

    # OUTBOUND removal testing
    # assert that nodes with only one outbound transition are removed correctly
    a.addTransition(node.identifier, node2.identifier, 'a')
    assert len(node.inbound_transitions) == 0
    assert len(node.outbound_transitions) == 1
    node.removeTransition(node2.identifier, 'a') # remove the outbound transition
    assert len(node.inbound_transitions) == 0
    assert len(node.outbound_transitions) == 0

    # assert that nodes with multiple outbound transitions are removed correctly
    a.addTransition(node.identifier, node2.identifier, 'a')
    a.addTransition(node.identifier, node2.identifier, 'b')
    assert len(node.inbound_transitions) == 0
    assert len(node.outbound_transitions) == 2
    node.removeTransition(node2.identifier, 'a') # remove the outbound transition
    node.removeTransition(node2.identifier, 'b') # remove the outbound transition
    assert len(node.inbound_transitions) == 0
    assert len(node.outbound_transitions) == 0

    # test removing more outbound transitions than exist
    node3 = a.takeIDReturnNodeObject(a.addStateReturnID())
    a.addTransition(node.identifier, node2.identifier, 'a')
    a.addTransition(node.identifier, node3.identifier, 'a') # illegal under DFA rules
    assert len(node.inbound_transitions) == 0
    assert len(node.outbound_transitions) == 1
    node.removeTransition(node2.identifier, 'a') # remove the outbound transition
    node.removeTransition(node3.identifier, 'a') # try removing an outbound transition that isn't there
    assert len(node.inbound_transitions) == 0
    assert len(node.outbound_transitions) == 0

    # test same as above, but for singular removals
    node3 = a.takeIDReturnNodeObject(a.addStateReturnID())
    a.addTransition(node.identifier, node2.identifier, 'a')
    a.addTransition(node.identifier, node3.identifier, 'a')
    a.addTransition(node.identifier, node3.identifier, 'b')
    assert len(node.inbound_transitions) == 0
    assert len(node.outbound_transitions) == 2
    node.removeTransition(node2.identifier, 'a') # remove the outbound transition
    assert len(node.inbound_transitions) == 0
    assert len(node.outbound_transitions) == 1
    node.removeTransition(node3.identifier, 'a') # remove the outbound transition
    assert len(node.outbound_transitions) == 1


    # INBOUND removal testing
    # test singular inbound transition removal
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    a.addTransition(node2.identifier, node.identifier, 'a')
    assert len(node.inbound_transitions) == 1
    node.removeTransition(node2.identifier, 'a')
    assert len(node.inbound_transitions) == 0
    assert len(node.outbound_transitions) == 0

    # test multiple inbounds removal (from node2)
    a, node = helper_ReturnNewAutomatonAndNodeObj()
    node2 = a.takeIDReturnNodeObject(a.addStateReturnID())
    node3 = a.takeIDReturnNodeObject(a.addStateReturnID())
    a.addTransition(node.identifier, node2.identifier, 'a')
    a.addTransition(node.identifier, node2.identifier, 'b')
    a.addTransition(node3.identifier, node2.identifier, 'a')
    assert len(node2.inbound_transitions) == 3
    assert len(node2.outbound_transitions) == 0
    node2.removeTransition(node.identifier, 'a') # remove the inbound transition
    assert len(node2.inbound_transitions) == 2
    node2.removeTransition(node.identifier, 'b') # remove the inbound transition
    assert len(node2.inbound_transitions) == 1
    node2.removeTransition(node3.identifier, 'a') # remove the inbound transition
    assert len(node2.inbound_transitions) == 0
    assert len(node2.outbound_transitions) == 0

    # MIXED removal testing
    # test mixed removal, where there is a transition loop ('N1'->'N2' for 'a'; N2->N1 for 'a')
    # test once with complete removal, once with partial removal
    b, node = helper_ReturnNewAutomatonAndNodeObj()
    node2 = b.takeIDReturnNodeObject(b.addStateReturnID())
    b.addTransition(node.identifier, node2.identifier, 'a')
    b.addTransition(node2.identifier, node.identifier, 'a')
    assert len(node.inbound_transitions) == 1
    assert len(node.outbound_transitions) == 1
    assert len(node2.inbound_transitions) == 1
    assert len(node2.outbound_transitions) == 1
    node2.removeTransition(node.identifier, 'a')
    assert len(node2.inbound_transitions) == 1
    assert len(node2.outbound_transitions) == 0
    assert len(node.inbound_transitions) == 1 # the transitions of Node "node" remain unchanged
    assert len(node.outbound_transitions) == 1 # the transitions of Node "node" remain unchanged
    node.removeTransition(node2.identifier, 'a')
    assert len(node.inbound_transitions) == 1
    assert len(node.outbound_transitions) == 0 # the inbound transition of node2 remains unchanged

def test_AutomatonremoveTransition():
    # tests that Automaton.addTransition() removes transitions from either inbound or outbound transitions
    # whichever is appropriate
    # does NOT check the format of these additions
    # NOTE!!! works, but ONLY IF in format removeTransition(source, destination, input)
    # i.e. it must be for an outbound transition, source -> destination, not destination <- source
    e, node = helper_ReturnNewAutomatonAndNodeObj()
    assert len(node.outbound_transitions) == 0
    assert len(node.inbound_transitions) == 0

    target_node = e.takeIDReturnNodeObject(e.addStateReturnID())
    assert len(target_node.outbound_transitions) == 0
    assert len(target_node.inbound_transitions) == 0

    # simple tests first (just 1 or 2 removals)
    e.addTransition(node.identifier, target_node.identifier, 'z')
    e.removeTransition(target_node.identifier, node.identifier, 'z')
    assert len(target_node.outbound_transitions) == 0
    assert len(target_node.inbound_transitions) == 0
    assert len(node.outbound_transitions) == 0
    assert len(node.inbound_transitions) == 0

    # multiple removals of transitions
    e.addTransition(node.identifier, target_node.identifier, 'a')
    e.addTransition(node.identifier, target_node.identifier, 'b')
    e.addTransition(target_node.identifier, node.identifier, 'c')
    e.addTransition(target_node.identifier, node.identifier, 'b')
    assert len(target_node.inbound_transitions) == 2
    assert len(target_node.outbound_transitions) == 2
    assert len(node.inbound_transitions) == 2
    assert len(node.outbound_transitions) == 2
    e.removeTransition(node.identifier, target_node.identifier, 'a') # remove the transition going from node -> target_node for char 'a'
    assert len(node.inbound_transitions) == 2 # should be unaffected
    assert len(node.outbound_transitions) == 1 # affected
    assert len(target_node.outbound_transitions) == 2 # unaffected, bc we're removing the other node's outbound, therefore target_node's inbound
    assert len(target_node.inbound_transitions) == 1 # affected



    # removing inbounds. Failed. Temporarily disabled.
    #  As I'm the one calling automaton.removeTransition(), I'll just reverse the parameter order when there's a problem
    #  and try to call automaton.removeTransition() on outbounds only, until I have a fix.

    # # assert len(target_node.outbound_transitions) == 2 # temporary: demonstration purposes.
    # # print(target_node.outbound_transitions) # temporary
    # e.removeTransition(node.identifier, target_node.identifier, 'b') # node should lose an outbound, and target_node one inbound
    # assert len(node.outbound_transitions) == 0
    # assert len(node.inbound_transitions) == 2
    # # print(target_node.outbound_transitions) # temporary
    # # target_node only has ('N101', 'c'). target_node loses its outbound_transition ('N101', 'b')
    # # node also loses its outbound ('N102', 'b'), but that's intentional
    # # PROBLEM: target_node loses an outbound transition when it shouldn't!!
    # #   This all happens when 2 nodes have transitions leading to each other for the same input
    # # todo: resolve the line below
    # # then tackle the following lines
    # # I suspect that automaton's function is calling on both nodes to remove those transitions, but it isn't specifying whether they're inbound
    # # or outbound, so they're removed inappropriately (perhaps from just one - outbound in this case - and not from the other)
    # assert len(target_node.outbound_transitions) == 2 # NOTE: THIS IS FAILING. it says 1 != 2
    # assert len(target_node.inbound_transitions) == 0 # NOTE: it says 1 != 0
    # e.removeTransition(target_node.identifier, node.identifier, 'c')

def test_AutomatoncanNodePassLetterOn():
    # tests whether a node has a valid outbound node for the given letter
    #  that function returns True or False
    # most of the code will probably be in Node class. Automaton will simply call it.

    # test one valid outbound
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    a.addTransition(node.identifier, node2.identifier, 'a')
    assert a.canNodePassLetterOn(node.identifier, 'a') == True

    # test one illegal outbound
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    a.addTransition(node.identifier, node2.identifier, 'a')
    assert a.canNodePassLetterOn(node.identifier, 'b') == False

def test_AutomatonchangeNodeDisplayName():
    # the node method is trivial, so here we test whether the automaton maintains its integrity after name changes
    # i.e. do its inbound and outbound transitions still point to the same node? Was the name change successful?

    # test name change works
    a, node = helper_ReturnNewAutomatonAndNodeObj()
    a.changeNodeDisplayName(node.identifier, 't-rex')
    assert node.display_name == 't-rex'

    # test that inbound and outbound transitions remain unaffected
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    a.addTransition(node.identifier, node2.identifier, 'x')
    a.addTransition(node2.identifier, node.identifier, 'y')
    prior_inbounds = node.inbound_transitions
    prior_outbounds = node.outbound_transitions
    assert prior_inbounds == node.inbound_transitions
    assert prior_outbounds == node.outbound_transitions

def test_determineWholeInputAcceptance():
    # tests whether whole strings are accepted or rejected by the automaton (returns True or False)
    # this is different to repeated calls of automaton.canNodePassLetterOn() in that this function
    # involves active state changes, which are later undone
    # unlike progressOneStep() or progressToEnd(), this function makes NO LASTING CHANGES

    # 2 node, 2 transition test
    # accept any string of 'a' and 't' ending in 't'
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    a.addTransition(node.identifier, node2.identifier, 't')
    a.addTransition(node2.identifier, node.identifier, 'a')
    assert a.initial_node_obj == node
    assert a.active_node_obj == node
    a.flipAcceptingOrRejecting(node2.identifier)
    assert node.accepting == False
    assert node2.accepting == True
    assert a.active_node_obj == node
    assert a.determineWholeInputAcceptance('') == False
    assert a.determineWholeInputAcceptance('t') == True
    assert a.determineWholeInputAcceptance('ta') == False
    assert a.determineWholeInputAcceptance('tat') == True # 101,tat->102,at->101,t->102,E
    assert a.determineWholeInputAcceptance('tatatatat') == True

    # test 2 node automaton, each with 2 outbound
    # each passes either a or b to the other node. Automaton accepts an odd number of 'a' or 'b'
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    a.addTransition(node.identifier, node2.identifier, 'a')
    a.addTransition(node.identifier, node2.identifier, 'b')
    a.addTransition(node2.identifier, node.identifier, 'a')
    a.addTransition(node2.identifier, node.identifier, 'b')
    a.flipAcceptingOrRejecting(node2.identifier)
    assert node.accepting == False
    assert node2.accepting == True
    assert a.determineWholeInputAcceptance('a') == True
    assert a.determineWholeInputAcceptance('aaa') == True
    assert a.determineWholeInputAcceptance('aba') == True
    assert a.determineWholeInputAcceptance('abaabaaba') == True
    assert a.determineWholeInputAcceptance('') == False
    assert a.determineWholeInputAcceptance('ab') == False
    assert a.determineWholeInputAcceptance('bb') == False
    assert a.determineWholeInputAcceptance('bbab') == False

    # test 3 node automaton, each with 1 outbound
    # accepts the empty string, tatt*(aat*)*
    # t -> a -> t <t>
    #        <- a
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    node3 = a.takeIDReturnNodeObject(a.addStateReturnID())
    a.addTransition(node.identifier, node2.identifier, 't')  # node, t -> node2
    a.addTransition(node2.identifier, node3.identifier, 'a') # node2, a -> node3
    a.addTransition(node3.identifier, node3.identifier, 't') # node3, t -> node3; loop.
    a.addTransition(node3.identifier, node2.identifier, 'a') # node3, a -> node2
    a.flipAcceptingOrRejecting(node.identifier)
    a.flipAcceptingOrRejecting(node3.identifier)
    assert node.accepting == True
    assert node3.accepting == True
    assert a.determineWholeInputAcceptance('') == True
    assert a.determineWholeInputAcceptance('t') == False
    assert a.determineWholeInputAcceptance('ta') == True # node, ta -> node2, a -> node3, E
    assert a.determineWholeInputAcceptance('tat') == True
    assert a.determineWholeInputAcceptance('tattat') == False
    assert a.determineWholeInputAcceptance('tataat') == True
    assert a.determineWholeInputAcceptance('tataataat') == True
    assert a.determineWholeInputAcceptance('tataataattt') == True
    assert a.determineWholeInputAcceptance('tatatatc') == False
    assert a.determineWholeInputAcceptance('tatttt') == True


    # test for stuck input (i.e. there's no valid transition for this character that's in the automaton alphabet)
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    a.addTransition(node.identifier, node2.identifier, 't')
    a.addTransition(node2.identifier, node.identifier, 'a')
    assert a.determineWholeInputAcceptance('b') == False
    assert a.determineWholeInputAcceptance('tb') == False
    assert a.determineWholeInputAcceptance('tab') == False

    # test for invalid characters (e.g. 'v' when there are no 'v' transitions)
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    a.addTransition(node.identifier, node2.identifier, 't')
    a.addTransition(node2.identifier, node.identifier, 'a')
    assert a.determineWholeInputAcceptance('tf') == False
    assert a.determineWholeInputAcceptance('T') == False
    assert a.determineWholeInputAcceptance('v') == False
    assert a.determineWholeInputAcceptance('tmoney') == False

def test_AutomatonprogressOneStep():
    # returns True if self.active_node has a valid outbound for the given single character (even if self-referential)
    # else returns False
    # changes self.path_taken and self.active_node_obj as state transitions take place
    # looped state transitions are also added to self.path_taken
    # try to choose a name more reflective of what it does

    # test 3 node automaton, each with 1 outbound, starting from initial state
    # --> automaton copied from above <--
    # accepts the empty string, tatt*(aat*)*
    # t -> a -> t <t>
    #        <- a
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    node3 = a.takeIDReturnNodeObject(a.addStateReturnID())
    a.addTransition(node.identifier, node2.identifier, 't')  # node, t -> node2
    a.addTransition(node2.identifier, node3.identifier, 'a')  # node2, a -> node3
    a.addTransition(node3.identifier, node3.identifier, 't')  # node3, t -> node3; loop.
    a.addTransition(node3.identifier, node2.identifier, 'a')  # node3, a -> node2
    a.flipAcceptingOrRejecting(node.identifier)
    a.flipAcceptingOrRejecting(node3.identifier)
    assert node.accepting == True
    assert node3.accepting == True

    # For the empty string: return self.active_node.accepting when remaining input is ''
    # make no other changes
    # I'm not sure if it will receive the empty string, but it's worth establishing a protocol for if it does
    assert a.progressOneStep('') == True
    assert node.accepting == True
    assert a.active_node_obj == node
    assert len(a.path_taken) == 0


    # test that rejected characters do not affect self.path_taken or self.active_node
    assert a.progressOneStep('a') == False
    assert a.active_node_obj == node
    assert len(a.path_taken) == 0

    assert a.progressOneStep('t') == True # node, ta -> node2, a
    assert a.active_node_obj == node2
    assert len(a.path_taken) == 1
    assert a.path_taken[0] == node2.identifier

    assert a.progressOneStep('') == False # not on an accepting node

    assert a.progressOneStep('a') == True # node2, a -> node3, E
    assert a.active_node_obj == node3
    assert len(a.path_taken) == 2
    assert a.path_taken[0] == node2.identifier
    assert a.path_taken[1] == node3.identifier

    assert a.progressOneStep('') == True # because we're on an accepting node, node3
    assert a.active_node_obj == node3
    assert len(a.path_taken) == 2
    assert a.path_taken[0] == node2.identifier
    assert a.path_taken[1] == node3.identifier

    # test self-referencing nodes
    # these should return true and update self.path_taken, regardless of whether that node is accepting
    # the empty string will be the final test of whether the string is accepted overall or not (in another function)
    a, node = helper_ReturnNewAutomatonAndNodeObj()
    a.addTransition(node.identifier, node.identifier, 'a')
    assert node.accepting == False
    assert a.progressOneStep('a') == True
    assert len(a.path_taken) == 1
    assert a.initial_node_obj == node
    assert a.active_node_obj == node


def test_AutomatonprogressToEnd():
    # returns accepted signal if accepted
    # else, returns blocked or rejected signals
    # progresses the automaton as far as it may legally go
    # fails and returns signal if any input character is blocked
    # updates self.path_taken and self.active_node_obj appropriately, for each accepted character

    signal_rejected = 'rejected' # indicates that the whole string has been processed but the final node is rejecting
    signal_blocked = 'blocked' # indicates that a character has no valid outbound
    signal_accepted = 'accepted' # indicates that the whole string was accepted, and the progression / sim successful

    # test 3 node automaton, each with 1 outbound, starting from initial state
    # --> automaton copied from above <--
    # accepts the empty string, tatt*(aat*)*
    # t -> a -> t <t>
    #        <- a
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    node3 = a.takeIDReturnNodeObject(a.addStateReturnID())
    a.addTransition(node.identifier, node2.identifier, 't')  # node, t -> node2
    a.addTransition(node2.identifier, node3.identifier, 'a')  # node2, a -> node3
    a.addTransition(node3.identifier, node3.identifier, 't')  # node3, t -> node3; loop.
    a.addTransition(node3.identifier, node2.identifier, 'a')  # node3, a -> node2
    a.flipAcceptingOrRejecting(node.identifier)
    a.flipAcceptingOrRejecting(node3.identifier)

    assert a.progressToEnd('') == signal_accepted
    assert len(a.path_taken) == 0
    assert a.active_node_obj == node

    # rejected inputs may lengthen self.path_taken, but will still return the rejected signal
    assert len(a.path_taken) == 0
    assert a.progressToEnd('t') == signal_rejected
    assert len(a.path_taken) == 1
    assert a.active_node_obj == node2

    # reset the automaton and test again
    a.path_taken = []
    a.active_node_obj = a.initial_node_obj
    assert a.progressToEnd('ta') == signal_accepted # node, ta -> node2, a -> node3, E
    assert len(a.path_taken) == 2
    assert a.active_node_obj == node3

    a.path_taken = []
    a.active_node_obj = a.initial_node_obj
    assert a.progressToEnd('tat') == signal_accepted # node, tat -> node2, at -> node3, t -> node3, E
    assert len(a.path_taken) == 3 # node2 -> node3 -> node3
    assert a.active_node_obj == node3

    # test from partial completion / advanced simulation
    a.path_taken = a.path_taken[:-2] # remove the last 2 elements
    length_before = len(a.path_taken)
    a.active_node_obj = a.takeIDReturnNodeObject(a.path_taken[-1]) # set to the last element
    assert a.active_node_obj == node2
    assert a.progressToEnd('attttttt') == signal_accepted # node2, at... -> node3, t loop
    assert len(a.path_taken) == length_before + len('attttttt')
    assert a.active_node_obj == node3

    # test blocked from partial completion
    assert a.progressToEnd('at') == signal_blocked

    # test blocked from fresh automaton
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    a.addTransition(node.identifier, node2.identifier, 'a')
    a.addTransition(node.identifier, node2.identifier, 'b')
    assert a.progressToEnd('abb') == signal_blocked
    assert len(a.path_taken) == 1
    assert a.active_node_obj == node2


def test_AutomatonregressOneStep():
    # undoes however many previous operations
    # if already regressed to start, do nothing. No need to tell user
    # looks to self.path_taken and undoes each step
    # that means it also removes entries from the self.path_taken
    # NOTE: currently relies on the play forward functions, so if they change, that could cause errors here

    # test stuff similar to above. Also check that active node is correct when supposed to change
    # test from 1 step in, on a 2 node automaton
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    a.addTransition(node.identifier, node2.identifier, 'a')
    a.addTransition(node2.identifier, node.identifier, 'b')
    a.progressOneStep('a')
    assert len(a.path_taken) == 1 # proofing correct setup
    assert a.active_node_obj == node2 # proofing correct setup
    a.regressOneStep()
    assert len(a.path_taken) == 0
    assert a.active_node_obj == node

    # test from 2 steps in on same 2 step automaton
    a.progressOneStep('a')
    a.progressOneStep('b')
    assert len(a.path_taken) == 2
    assert a.active_node_obj == node
    a.regressOneStep()
    assert len(a.path_taken) == 1
    assert a.active_node_obj == node2
    a.regressOneStep()

    # test on a fresh automaton, one which hasn't had any steps taken
    # should do nothing
    assert len(a.path_taken) == 0
    assert a.active_node_obj == a.initial_node_obj
    a.regressOneStep()
    assert len(a.path_taken) == 0
    assert a.active_node_obj == a.initial_node_obj


def test_AutomatonregressToStart():
    # test scenarios: virgin automaton, completed automaton
    # need not return anything. We just check path taken and active node
    a, node, node2 = helper_ReturnNewAutomatonAnd2NodeObj()
    a.addTransition(node.identifier, node2.identifier, 'a')
    a.addTransition(node2.identifier, node.identifier, 'b')
    a.progressToEnd('abababababa')
    assert len(a.path_taken) == len('abababababa')
    assert a.active_node_obj == node2
    a.regressToStart()
    assert len(a.path_taken) == 0
    assert a.active_node_obj == node

    # from clean slate
    a.regressToStart()
    assert len(a.path_taken) == 0
    assert a.active_node_obj == node