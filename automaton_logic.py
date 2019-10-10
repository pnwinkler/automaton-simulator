# contains functions required to make an automaton simulation work,
# at least in text (no GUI to be considered yet)
# this file provides the logic for stepwise operation of automata
# namely, an Automaton class (treat as singleton / controller for all nodes), and a Node class
# these nodes will provide logic and properties for each node,
# in order to be treated by the Automaton class


class Automaton():
    # may have to provide mechanism / link in this class to modify nodes
    # NOTE: some of these may have to call Node methods
    # when necessary, check that changes to a Node object will keep automaton legal

    def __init__(self):
        # set up necessary properties of the automaton

        # user input to be tested.
        # Note: should only change when the user requests it changes & their request is valid
        # we need this to remain constant so that regression functions work
        # otherwise we cannot infer the just-processed char
        self.CONST_USER_INPUT = ''

        # initial state
        self.initial_node_obj = None

        # node currently processing the input string
        self.active_node_obj = None

        # initial node name (name initially given to a node, not the name of the initial node)
        self.initial_node_obj_node_name_val = 64  # = 'A' - 1

        # base node ID. Incremented by functions below
        self.node_ID = 'N' + str(100)

        # all nodes which form this automaton
        self.node_collection = []

        # contains the history ie the path taken which can then be undone. Includes node IDs may include the input too
        # does NOT include any reference to initial node
        self.path_taken = []

        # possibly unnecessary properties
        self.state_count = 0
        self.transition_rules = {}  # Can we not just check each connected Node for rules?

    def addStateReturnID(self):
        # create a Node object and add it to the node_collection var. Transition is added later & elsewhere
        # if self.node_collection is empty, set this first node to be the initial_node_obj !

        # display name, identifier
        self.initial_node_obj_node_name_val += 1
        initial_name = chr(self.initial_node_obj_node_name_val)
        self.node_ID = self.node_ID[0] + str(int(self.node_ID[1:]) + 1)

        self.node_collection.append(Node(initial_name, self.node_ID))
        x = self.node_ID

        # set the initial value to the only Node object in self.node_collection
        if len(self.node_collection) == 1:
            self.initial_node_obj = self.node_collection[0]
            self.active_node_obj = self.initial_node_obj

        # so that I don't pass a reference to an object which shouldn't be changed
        return x

    def takeIDReturnNodeObject(self, node_ID):
        # helper function. Take a node's string ID then return a reference to that node
        # print(node_ID)
        if not isinstance(node_ID, str):
            raise ValueError('takeIDReturnNodeObject received a node_ID not of type string')

        if len(node_ID) != 4 or node_ID[0] != 'N':
            raise ValueError()  # f'invalid node_ID given to automaton.takeIDReturnNodeObject. Should receive parameters in format \'N101\' but received {node_ID}')

        for n in self.node_collection:
            if n.identifier == node_ID:
                return n
        print("self.node_collection (names)", [n.identifier for n in self.node_collection])
        raise ValueError(f'ERROR: Node with identifier {node_ID} not found in self.node_collection')

    def setInitialNode(self, desired_start_node_ID):
        # changes which node is the initial node.
        if not self.path_taken:
            self.initial_node_obj = self.takeIDReturnNodeObject(desired_start_node_ID)
            self.active_node_obj = self.initial_node_obj
        # we prevent changes to the initial node being implemented when a simulation is in progress
        # in order to prevent user confusion. Preventing changes during input processing will prevent accidental modifications by user
        # and let them know that the automaton they started the simulation with is the one that they ended with
        # should not raise valueerror as that may disrupt user
        else:
            print(
                'Devnote: setInitialNode() called while self.path_taken!=None, which indicates a simulation is in progress. Request denied. (This should appear in testing)')

    def flipAcceptingOrRejecting(self, node_ID):
        # flips given node between an accepting or rejecting state
        self.takeIDReturnNodeObject(node_ID).flipAcceptingOrRejecting()

    def removeState(self, node_ID):
        # removes node from automaton's node_collection
        # removes all transitions referencing that node-to-be-deleted from every other node
        # complicated code which achieves better performance through fewer calls to Node.removeTransition()
        # might need to add checks, like will removing a state render the automaton illegal?
        efficient = True
        if efficient:
            for n in self.node_collection:
                for id_input_tpl in self.takeIDReturnNodeObject(
                        n.identifier).inbound_transitions + self.takeIDReturnNodeObject(
                    n.identifier).outbound_transitions:
                    if self.takeIDReturnNodeObject(node_ID).identifier in id_input_tpl[0]:
                        self.removeTransition(node_ID, n.identifier,
                                              id_input_tpl[1])  # node_ID, targetid, transitionletter

        # simplified code below. Has the problem of calling Node.removeTransition() too often, but otherwise achieves the same result
        if not efficient:
            for inbound in self.takeIDReturnNodeObject(node_ID).inbound_transitions:
                # inbound format is ('N102', 'c')
                for outbound in self.takeIDReturnNodeObject(inbound[0]).outbound_transitions:
                    if outbound[0] == node_ID:
                        self.takeIDReturnNodeObject(inbound[0]).removeTransition(node_ID, inbound[1])

            # remove other nodes' inbounds from node-to-be-deleted
            for outbound in self.takeIDReturnNodeObject(node_ID).outbound_transitions:
                for inbound in self.takeIDReturnNodeObject(outbound[0]).inbound_transitions:
                    if inbound[0] == node_ID:
                        self.takeIDReturnNodeObject(outbound[0]).removeTransition(node_ID, outbound[1])

        # remove from self.node_collection
        self.node_collection.remove(self.takeIDReturnNodeObject(node_ID))

    def addTransition(self, node_ID, target_node_ID, transition_letter):
        # check here that the request is legal and possible
        # if it is, create the node object, then give it an ID and add it to node_collection
        # note: you will need to pass the right node ID to all relevant nodes. Node class will not check the ID

        # transition_letter is the letter which would transition the active state from
        # node_ID to target_node_ID
        # skipping checks for now. Implement later

        self.takeIDReturnNodeObject(node_ID).addTransition(target_node_ID, transition_letter)

        # update the target node's inbound_transitions variable
        if self.takeIDReturnNodeObject(node_ID).addition_committed:
            # print('T1', target_node_ID)
            # print('T2', self.takeIDReturnNodeObject(target_node_ID))
            # print('T3', self.node_collection)
            # for i in self.node_collection:
            #     print(i.identifier)
            self.takeIDReturnNodeObject(target_node_ID).inbound_transitions.append((node_ID, transition_letter))

    def removeTransition(self, node_ID, target_node_ID, transition_letter):
        # maybe check here if removing that transition would keep the automaton legal / coherent ?
        # if yes, call the node method removeTransition()
        # NOTE: currently only works for an initial outbound transition parameter
        #  i.e. (originating_node, destination_node, input) and NOT (d_n, o_n, input)

        experimental = False
        if experimental:
            self.takeIDReturnNodeObject(node_ID).removeOutboundTransition(target_node_ID, transition_letter)
            self.takeIDReturnNodeObject(target_node_ID).removeInboundTransition(node_ID, transition_letter)

        if not experimental:
            self.takeIDReturnNodeObject(node_ID).removeTransition(target_node_ID, transition_letter)
            self.takeIDReturnNodeObject(target_node_ID).removeTransition(node_ID, transition_letter)

    def canNodePassLetterOn(self, node_ID, transition_letter, return_validtarget_ID=False):
        # helper method. Checks whether a given letter (of the user input) is accepted or rejected

        # find the node in node_collection
        # then call the node's method of the same name
        return self.takeIDReturnNodeObject(node_ID).canNodePassLetterOn(transition_letter, return_validtarget_ID)

    def determineWholeInputAcceptance(self, input_string, DEBUGTRACE=False):
        # Determines whether the whole input is accepted or rejected
        # returns True or False, according to whether the final node is accepting or rejecting
        # repeatedly calls the node method on the correct node, shrinks the input accordingly + changes the active node
        # does NOT progress the automaton. It makes no changes to self.path_taken, and no lasting changes to active node
        if len(input_string) == 0:
            return self.initial_node_obj.accepting  # T / F

        previously_active_node = self.active_node_obj

        # so long as the active_node_obj can pass the letter c on, we keep changing the active node and iterating
        #  through input_string
        debug_index = 0
        for c in input_string:
            if DEBUGTRACE:
                debug_index += 1
                print(self.active_node_obj.identifier, c, input_string[debug_index:])

            # canNodePassLetterOn() can, with a 2nd parameter, return the valid target's node instead
            validtarget_ID = self.active_node_obj.canNodePassLetterOn(c, True)

            # if there's a legal target, we set it to be the active_node_obj and continue
            if validtarget_ID:
                self.active_node_obj = self.takeIDReturnNodeObject(validtarget_ID)
            else:
                # problem: would pass if the input string runs out and there's still a validtarget_ID, even if it's not accepting
                # reset active node to its initial condition
                self.active_node_obj = self.initial_node_obj
                return False
        self.active_node_obj = previously_active_node
        try:
            return self.takeIDReturnNodeObject(validtarget_ID).accepting
        except AttributeError as e:
            return False

    def receiveInputString(self, user_string):
        # takes user input string. This is the ONLY place where it should change
        self.CONST_USER_INPUT = user_string

    def progressOneStep(self, input_char):
        # determines whether self.active_node has a valid outbound transition for a one-character input, input_char.
        # return True if input_char has a valid outbound transition from self.active_node
        #  in which case, self.path_taken and self.active_node are updated to that outbound_transition
        # else returns False
        return_validtarget_ID = True

        if input_char == '':
            # I don't know yet if we'll ever receive an empty string, but it's safer to have this
            return self.active_node_obj.accepting

        # canNodePassLetterOn will return either the nodeID or False
        result = self.canNodePassLetterOn(self.active_node_obj.identifier, input_char, return_validtarget_ID)
        if result:
            # valid node found. Update path_taken with said node
            self.path_taken.append(result)

            # update active node
            self.active_node_obj = self.takeIDReturnNodeObject(result)
            return True
        else:
            return False

    def progressToEnd(self, whole_input_string):
        # advances the automaton until its conclusion (accepted or rejected input)
        # returns a string signal based on the whether the string was accepted, rejected, or blocked
        # note that the string need not be exhausted to reach this state.
        # it can be rejected beforehand or stuck
        signal_rejected = 'rejected'  # used to indicate that the whole string has been processed but the final node is rejecting
        signal_blocked = 'blocked'
        signal_accepted = 'accepted'

        for c in whole_input_string:
            # advances the automaton a step, and receives either True for acceptance, or False for a blocked character
            success_tf = self.progressOneStep(c)
            if not success_tf:
                return signal_blocked

        if self.active_node_obj.accepting:
            # whole input is processed, and no stage was rejected
            return signal_accepted
        else:
            return signal_rejected

    def regressOneStep(self):
        # undoes the last operation
        # if already regressed to start, do nothing. The user need not know

        # if we're already at start, do nothing
        if len(self.path_taken) == 0 and self.active_node_obj == self.initial_node_obj:
            return

        # we are 1 step in. Change the active node, and remove the only step from self.path_taken
        if len(self.path_taken) == 1 and self.active_node_obj != self.initial_node_obj:
            self.active_node_obj = self.initial_node_obj
            self.path_taken = self.path_taken[:-1]
            return

        # we are multiple steps in. We set active node to previously active node
        self.active_node_obj = self.takeIDReturnNodeObject(self.path_taken[-2])

        # remove a step from self.path_taken
        self.path_taken = self.path_taken[:-1]

    def regressToStart(self):
        # probably calls regressOneStep() until it's done
        # reverts the automaton to its initial state
        while len(self.path_taken) > 0:
            self.regressOneStep()

    def changeNodeDisplayName(self, node_ID, intended_name):
        self.takeIDReturnNodeObject(node_ID).changeNodeDisplayName(intended_name)


# in general, Node functions should be accessed through the automaton to which they are bound, not directly
# they always take ID arguments, not node object arguments
class Node():
    def __init__(self, display_name, identifier):
        # name displayed on the node's name, the name in the center of the state circle. like 'q'
        self.display_name = display_name

        # unique ID used internally. We generate this
        self.identifier = identifier

        # determines whether this node is accepting or rejecting. Default is False. Changed via helper method
        self.accepting = False

        # identifiers of any nodes connected by a transition, inbound or outbound
        # It's important to keep this current in case a node (D) is deleted!
        # In that case, we refer to D's inbound nodes + outbound nodes, remove their connections to D, then delete D
        # should be in the same format as outbound_transitions
        # self.connected_nodes = []

        # same format as outbounds! Purpose is to keep the ID
        # probably best not hold the transition rules of inbound nodes, because that's one more place to modify them
        # NOTE: transitions are in form ('N125', a) for input 'a' transition to node ID N125
        self.inbound_transitions = []
        self.outbound_transitions = []

    def addTransition(self, target_node_ID, input):
        # check that there is not already an identical transition
        # note: the tuple below has to be in the right order
        # if (target_node_ID, input) in self.outbound_transitions:
        #     addition_committed is used by automaton's addTransition() to determine
        #     if the transition was committed or rejected
        # self.addition_committed = False
        # return

        # iterate through outbounds and ensure no existing transition for that letter
        # standard DFA requirement
        for transition in self.outbound_transitions:
            if transition[1] == input:
                self.addition_committed = False
                return

        else:
            # NOTE: transitions are in form ('N125', 'a') for input 'a' transition to node ID N125
            self.outbound_transitions.append((target_node_ID, input))
            self.addition_committed = True

    def removeTransition(self, target_node_ID, input):
        # removes transitions from connected (either inbound or from outbound) transitions variables

        # if this function receives a node with both an inbound and an outbound to the same other node, it will remove the outbound then return
        # even if it was intended to remove the inbound
        # probably the problem arises when we try to remove inbounds, as this code will preferentially remove outbounds
        # I don't think the automaton logic exclusively removes outbounds? If it did, why does commenting out the inbounds code below result in errors?
        # targetIdentifier does NOT mean that it's an outbound. It could be an inbound
        # therefore, when we call removeTransition(), we are not specifying inbound or outbound
        # so in the case that we want to remove an inbound to targetIdentifier, we receive problems because the outbound is removed first
        # I think splitting this function up may be the right call. We probably would still need to specify elsewhere
        # whether we're removing an inbound or an outbound though
        # that seems easier than changing the format of inbound and outbound_transitions, which is another option
        # a third is forcing the coder (me) to only use removeTransition() in one direction (i.e. inbound or outbound)
        # but that's really awkward and ignores a major problem / flaw. The error codes will be super ambiguous too.
        for element in self.outbound_transitions:
            if element[0] == target_node_ID and element[1] == input:
                self.outbound_transitions.remove(element)
                return

        for element in self.inbound_transitions:
            if element[0] == target_node_ID and element[1] == input:
                self.inbound_transitions.remove(element)
                return

        print(
            f'class Node removeTransition() for node {self.identifier} received targetIdentifier {target_node_ID}, input \'{input}\' but did not find it in self.transitions')
        print('This node may have been deleted, or may never have existed. (This will appear in testing)')

    # these 2 functions below are experimental
    def removeOutboundTransition(self, target_node_ID, input):
        for element in self.outbound_transitions:
            if element[0] == target_node_ID and element[1] == input:
                self.outbound_transitions.remove(element)
                return
        print(
            f'ERROR in class Node removeTransition() for node {self.identifier}. targetIdentifier {target_node_ID}, input \'{input}\' not found in self.outbound_transitions')
        print('This node may have been deleted, or may never have existed')

    def removeInboundTransition(self, target_node_ID, input):
        for element in self.inbound_transitions:
            if element[0] == target_node_ID and element[1] == input:
                self.inbound_transitions.remove(element)
                return
        print(
            f'ERROR in class Node removeTransition() for node {self.identifier}. targetIdentifier {target_node_ID}, input \'{input}\' not found in self.inbound_transitions')
        print('This node may have been deleted, or may never have existed')

    def canNodePassLetterOn(self, transition_letter, return_validtarget_ID=False):
        # check outbounds for target_node_ID
        # if there, and if transition_letter appropriate, return true
        # else, return false
        # HOWEVER, if return_validtarget_ID is True, returns the ID of that valid target instead
        for outbound in self.outbound_transitions:
            if outbound[1] == transition_letter:
                if return_validtarget_ID:
                    return outbound[0]
                return True
        return False

    def changeNodeDisplayName(self, intended_name):
        # allows the user to change the name of a node
        # nodes may be created with an automatically generated name, which the user may wish to change
        self.display_name = intended_name

    def flipAcceptingOrRejecting(self):
        if self.accepting:
            self.accepting = False
        else:
            self.accepting = True
