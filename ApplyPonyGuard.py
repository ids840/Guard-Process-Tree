from pm4py import PetriNet
from pm4py.objects.petri_net.utils import petri_utils


def left_right(string_guard):
    number_of_open_brackets = 0
    number_of_close_brackets = 0
    stop = False
    index = 0
    while not stop:
        if string_guard[index] == "(" or string_guard[index] == "[":
            number_of_open_brackets = number_of_open_brackets + 1
        if string_guard[index] == ")" or string_guard[index] == "]":
            number_of_close_brackets = number_of_close_brackets + 1
        if string_guard[index] == ",":
            if number_of_open_brackets - number_of_close_brackets == 1:
                left = string_guard[1:index]
                right = string_guard[index + 1:len(string_guard) - 1]
                return left, right
        if number_of_open_brackets == number_of_close_brackets:
            stop = True
        index = index + 1
def apply_pony_guard_greater(net, target_name,expression,target_transition, sign, place_of_greater,features):
    if expression.startswith("np"):
        first_index_of_open_bracket = expression.index("(")
        func_of_guard = expression[3:first_index_of_open_bracket]
        string_guard = expression[first_index_of_open_bracket:]
        left_right_string = left_right(string_guard)
        left = left_right_string[0]
        right = left_right_string[1]
        if func_of_guard == "add":
            apply_pony_guard_greater(net, target_name, left, target_transition, sign, place_of_greater,features)
            apply_pony_guard_greater(net, target_name, right, target_transition, sign,place_of_greater,features)
        else:
            apply_pony_guard_greater(net, target_name, left, target_transition, sign, place_of_greater,features)
            apply_pony_guard_greater(net, target_name, right, target_transition,1-sign, place_of_greater,features)
    elif expression.startswith("x"):
        first_index_of_close_bracket = expression.index("]")
        feature_index = int(expression[5:first_index_of_close_bracket])
        feature = features[feature_index]
        feature_transition = found_transition(net,feature)
        if sign:
            petri_utils.add_arc_from_to(feature_transition, place_of_greater, net)
        else:
            petri_utils.add_arc_from_to(feature_transition, place_of_greater, net,-1)
    else:
        start_transitions = found_start_transitions(net,found_place(net,"source"))
        empty_transition = return_transition_or_None(net,start_transitions,target_transition)
        if empty_transition==None:
            for start_transition in start_transitions:
                if sign:
                    petri_utils.add_arc_from_to(start_transition, place_of_greater, net, int(expression[0]))
                else:
                    petri_utils.add_arc_from_to(start_transition, place_of_greater, net, -1 * int(expression[0]))
        else:
            if sign:
                petri_utils.add_arc_from_to(empty_transition, place_of_greater, net, int(expression[0]))
            else:
                petri_utils.add_arc_from_to(empty_transition, place_of_greater, net, -1 * int(expression[0]))




def apply_pony_guard(net,target_name,string_guard, features):
    if string_guard.startswith("np"):
        first_index_of_open_bracket = string_guard.index("(")
        func_of_guard = string_guard[3:first_index_of_open_bracket]
        string_guard = string_guard[first_index_of_open_bracket:]
        left_right_string = left_right(string_guard)
        left = left_right_string[0]
        right = left_right_string[1]
        target_transition = found_transition(net,target_name)
        if func_of_guard == "greater":
            place_of_greater = PetriNet.Place("greater condition to " + target_transition.label)
            net.places.add(place_of_greater)
            apply_pony_guard_greater(net,target_name,left,target_transition, 1, place_of_greater,features)
            apply_pony_guard_greater(net,target_name,right,target_transition, 0, place_of_greater, features)
            petri_utils.add_arc_from_to(place_of_greater, target_transition, net)
        elif func_of_guard == "less":
            place_of_less = PetriNet.Place("less condition to " + target_transition.label)
            net.places.add(place_of_less)
            apply_pony_guard_greater(net, target_name, right, target_transition, 1, place_of_less, features)
            apply_pony_guard_greater(net, target_name, left, target_transition, 0, place_of_less, features)
            petri_utils.add_arc_from_to(place_of_less, target_transition, net)
        elif func_of_guard == "logical_and":
            apply_pony_guard(net, target_name, left, features)
            apply_pony_guard(net, target_name, right, features)
        elif func_of_guard == "logical_or":
            empty_transition_name_1 = "empty transition 1 for " + target_name
            empty_transition_1 = PetriNet.Transition(empty_transition_name_1, empty_transition_name_1)
            net.transitions.add(empty_transition_1)
            empty_transition_name_2 = "empty transition 2 for " + target_name
            empty_transition_2 = PetriNet.Transition(empty_transition_name_2, empty_transition_name_2)
            net.transitions.add(empty_transition_2)
            replace_edges_between_transition_to_empty(net,target_transition, empty_transition_1,empty_transition_2)
            apply_pony_guard(net,empty_transition_name_1,left,features)
            apply_pony_guard(net,empty_transition_name_2,right,features)
        elif func_of_guard == "equal":
            left_copy = left
            right_copy = right
            start_transitions = found_start_transitions(net, found_place(net,"source"))
            place_of_greater = PetriNet.Place("greater condition to " + target_transition.label)
            net.places.add(place_of_greater)
            empty_transition = return_transition_or_None(net, start_transitions, target_transition)
            if empty_transition == None:
                for transition in start_transitions:
                    petri_utils.add_arc_from_to(transition, place_of_greater, net)
            else:
                petri_utils.add_arc_from_to(empty_transition, place_of_greater, net)
            apply_pony_guard_greater(net, target_name, left_copy, target_transition, 1, place_of_greater, features)
            apply_pony_guard_greater(net, target_name, right_copy, target_transition, 0, place_of_greater, features)
            petri_utils.add_arc_from_to(place_of_greater, target_transition, net)


            place_of_less = PetriNet.Place("less condition to " + target_transition.label)
            net.places.add(place_of_less)
            empty_transition = return_transition_or_None(net, start_transitions, target_transition)
            if empty_transition == None:
                for transition in start_transitions:
                    petri_utils.add_arc_from_to(transition, place_of_less, net)
            else:
                petri_utils.add_arc_from_to(empty_transition, place_of_less, net)
            apply_pony_guard_greater(net, target_name, right, target_transition, 1, place_of_less, features)
            apply_pony_guard_greater(net, target_name, left, target_transition, 0, place_of_less, features)
            petri_utils.add_arc_from_to(place_of_less, target_transition, net)



def found_arc(net, xor_place, transition):
    for arc in net.arcs:
        if arc.target == transition and arc.source == xor_place:
            return arc

def return_transition_or_None(net,start_transitions, transition):
    pre_places = found_pre_places(transition)
    for pre_place in pre_places:
        for start_transition in start_transitions:
            for arc in net.arcs:
                if arc.source == start_transition and arc.target == pre_place:
                    return start_transition
    return None
def found_pre_places(transition):
    places = []
    for arc in transition.in_arcs:
        places.append(arc.source)
    return places

def remove_xor_edge_from_option_with_xor(net, pre_places, target_transition,empty_transition_1, empty_transition_2):
    for place in pre_places:
        arc = found_arc(net, place, target_transition)
        net.arcs.remove(arc)
        target_transition.in_arcs.remove(arc)
        place.out_arcs.remove(arc)
        petri_utils.add_arc_from_to(place, empty_transition_1, net)
        petri_utils.add_arc_from_to(place, empty_transition_2, net)

def replace_edges_between_transition_to_empty(net,target_transition, empty_transition_1, empty_transition_2):
    pre_places = found_pre_places(target_transition)
    remove_xor_edge_from_option_with_xor(net, pre_places, target_transition,empty_transition_1,empty_transition_2)
    place_of_or = PetriNet.Place("or place of " + target_transition.label)
    net.places.add(place_of_or)
    petri_utils.add_arc_from_to(empty_transition_1, place_of_or, net)
    petri_utils.add_arc_from_to(empty_transition_2, place_of_or, net)
    petri_utils.add_arc_from_to(place_of_or, target_transition, net)

def found_transition(net, transition_name):
    for transition in net.transitions:
        if (transition.label == None and transition.name == transition_name) or transition.label == transition_name:
            return transition


def found_place(net, place_name):
    for place in net.places:
        if place.name == place_name:
            return place


def found_start_transitions(net, source):
    start_transitions = []
    for arc in net.arcs:
        if arc.source == source:
            start_transitions.append(arc.target)
    return start_transitions

def add_arcs_from_place_to_transitions(net, place, transitions):
    for transition in transitions:
        petri_utils.add_arc_from_to(place, transition, net, 1)
