# This is a sample Python script.
import csv
import operator

#import double_to_single_transaction
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pm4py

import pandas

from datetime import datetime

from pm4py.algo.conformance.tokenreplay.variants import token_replay
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator

from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator

from pm4py.objects.petri_net.obj import PetriNet, Marking

from pm4py.objects.petri_net.utils import petri_utils

import random

import datetime

def found_places(net,list_of_places_names):
    places = []
    for place_name in list_of_places_names:
        place = found_place(net,place_name)
        places.append(place)
    return places
def found_start_transitions(net, source):
    start_transitions = []
    for arc in net.arcs:
        if arc.source == source:
            start_transitions.append(arc.target)
    return start_transitions


def add_arcs_from_start_transitions_to_parallel(net, place_parallel, start_transitions,number_of_tokens):
    for start_transition in start_transitions:
        petri_utils.add_arc_from_to(start_transition, place_parallel, net,number_of_tokens)


def add_arcs_from_place_to_places_transitions(net,place_of_remain, places):
    for place in places:
        arcs_out = place.out_arcs
        for arc in arcs_out:
            transition = arc.target
            petri_utils.add_arc_from_to(place_of_remain, transition, net, 1)


def group_fo_transitions_happen_x_times(net, places, number_of_tokens,index_of_row_guard):
    source = found_place(net, "source")
    start_transitions = found_start_transitions(net, source)
    place_of_remain = PetriNet.Place("counter place " + str(index_of_row_guard))
    net.places.add(place_of_remain)
    add_arcs_from_start_transitions_to_parallel(net, place_of_remain, start_transitions, number_of_tokens)
    add_arcs_from_place_to_places_transitions(net,place_of_remain, places)

def parallel_hapens_x_times(place_name, petri_net: PetriNet, number_of_tokens,name_of_transition):
    for arc in petri_net.arcs:
        if arc.target.name==place_name and arc.source.label == name_of_transition:
            arc.weight=number_of_tokens

def line_guard(list_a, list_b, petri_net: PetriNet, name_of_transition):
    can_go_to_line_a = PetriNet.Place("can go to line a")
    can_go_to_line_b = PetriNet.Place("can go to line b")
    got_service_in_a = PetriNet.Place("got service in a")
    got_service_in_b = PetriNet.Place("got service in b")
    s_t_1 = PetriNet.Transition("a", None)
    s_t_2 = PetriNet.Transition("b", None)
    s_t_3 = PetriNet.Transition("c", None)
    s_t_4 = PetriNet.Transition("e", None)
    petri_net.transitions.add(s_t_1)
    petri_net.transitions.add(s_t_2)
    petri_net.transitions.add(s_t_3)
    petri_net.transitions.add(s_t_4)
    for transition in petri_net.transitions:
        if transition.label == name_of_transition:
            petri_utils.add_arc_from_to(transition, can_go_to_line_a, petri_net)
    petri_net.places.add(can_go_to_line_a)
    petri_net.places.add(can_go_to_line_b)
    petri_net.places.add(got_service_in_a)
    petri_net.places.add(got_service_in_b)
    for transition in petri_net.transitions:
        transition_name = transition.label
        if transition_name == list_a[0]:
            get_in_line_a = transition
        if transition_name == list_b[0]:
            get_in_line_b = transition
        if transition_name == list_b[1]:
            get_service_in_a = transition
        if transition_name == list_a[1]:
            get_service_in_b = transition

    petri_utils.add_arc_from_to(get_service_in_a, got_service_in_a, petri_net)
    petri_utils.add_arc_from_to(get_service_in_b, got_service_in_b, petri_net)


    petri_utils.add_arc_from_to(can_go_to_line_a, get_in_line_a, petri_net)
    petri_utils.add_arc_from_to(can_go_to_line_b, get_in_line_b, petri_net)
    petri_utils.add_arc_from_to(get_in_line_a, can_go_to_line_b, petri_net)
    petri_utils.add_arc_from_to(get_in_line_b, can_go_to_line_a, petri_net)

    for place in petri_net.places:
        if place.name == "p_9":
            p_9 = place
        if place.name == "p_11":
            p_11 = place

    # petri_utils.add_arc_from_to(p_9, s_t_1, petri_net)
    # petri_utils.add_arc_from_to(can_go_to_line_a, s_t_1, petri_net)
    # petri_utils.add_arc_from_to(s_t_1, can_go_to_line_a, petri_net)
    # petri_utils.add_arc_from_to(p_9, s_t_2, petri_net)
    # petri_utils.add_arc_from_to(can_go_to_line_b, s_t_2, petri_net)
    # petri_utils.add_arc_from_to(s_t_2, can_go_to_line_a, petri_net)
    #
    #
    #
    # petri_utils.add_arc_from_to(p_11, s_t_3, petri_net)
    # petri_utils.add_arc_from_to(can_go_to_line_a, s_t_3, petri_net)
    # petri_utils.add_arc_from_to(s_t_3, can_go_to_line_b, petri_net)
    # petri_utils.add_arc_from_to(p_11, s_t_4, petri_net)
    # petri_utils.add_arc_from_to(can_go_to_line_b, s_t_4, petri_net)
    # petri_utils.add_arc_from_to(s_t_4, can_go_to_line_b, petri_net)

    petri_utils.add_arc_from_to(got_service_in_a, s_t_1, petri_net)
    petri_utils.add_arc_from_to(can_go_to_line_a, s_t_1, petri_net)
    petri_utils.add_arc_from_to(s_t_1, can_go_to_line_a, petri_net)
    petri_utils.add_arc_from_to(got_service_in_a, s_t_2, petri_net)
    petri_utils.add_arc_from_to(can_go_to_line_b, s_t_2, petri_net)
    petri_utils.add_arc_from_to(s_t_2, can_go_to_line_a, petri_net)

    petri_utils.add_arc_from_to(got_service_in_b, s_t_3, petri_net)
    petri_utils.add_arc_from_to(can_go_to_line_a, s_t_3, petri_net)
    petri_utils.add_arc_from_to(s_t_3, can_go_to_line_b, petri_net)
    petri_utils.add_arc_from_to(got_service_in_b, s_t_4, petri_net)
    petri_utils.add_arc_from_to(can_go_to_line_b, s_t_4, petri_net)
    petri_utils.add_arc_from_to(s_t_4, can_go_to_line_b, petri_net)


def found_transition(net, transition_name):
    for transition in net.transitions:
        if (transition.label == None and transition.name == transition_name) or transition.label == transition_name:
            return transition
def found_place(net, place_name):
    for place in net.places:
        if place.name == place_name:
            return place

def create_empty_transition_for_guard_not_good(net, transition):
    if transition.label == None:
        empty_transition = PetriNet.Transition(transition.name + "_empty_transition", None)
    else:
        empty_transition = PetriNet.Transition(transition.label + "_empty_transition", None)
    net.transitions.add(empty_transition)
    arcs_in = transition.in_arcs
    for arc in arcs_in:
        petri_utils.add_arc_from_to(arc.source, empty_transition, net,arc.weight)
    arcs_out = transition.out_arcs
    for arc in arcs_out:
        petri_utils.add_arc_from_to(empty_transition, arc.target, net,arc.weight)
    return empty_transition

def found_transitions(net,list_of_transitions_names):
    transitions = []
    for transition_name in list_of_transitions_names:
        transition = found_transition(net,transition_name)
        transitions.append(transition)
    return transitions

def counter_to_list_of_transitions(net,min_guard_place,list_of_transitions):
    for transition in list_of_transitions:
        petri_utils.add_arc_from_to(transition, min_guard_place, net)


def add_min_guard_arc_to_transition(net, min_guard_place, transition, times):
    petri_utils.add_arc_from_to(min_guard_place, transition, net, times)


def create_the_min_guard_place_and_arcs(net, transition, list_of_transitions_names, times):
    list_of_transitions = found_transitions(net,list_of_transitions_names)
    if transition.label == None:
        min_guard_place = PetriNet.Place(transition.name+"_guard")
    else:
        min_guard_place = PetriNet.Place(transition.label+"_guard")
    net.places.add(min_guard_place)
    counter_to_list_of_transitions(net,min_guard_place,list_of_transitions)
    add_min_guard_arc_to_transition(net,min_guard_place,transition, times)



def guard_of_min_times(net,transition_name, list_of_transitions_names, times, in_xor):
    transition = found_transition(net,transition_name)
    if in_xor == False:
        create_empty_transition_for_guard_not_good(net,transition)
        guard_of_max_times(net, transition_name + "_empty_transition", list_of_transitions_names, times-1, 1)
    create_the_min_guard_place_and_arcs(net,transition, list_of_transitions_names, times)

def empty_transition_if_not(net,transition_name):
    transition = found_transition(net,transition_name)
    create_empty_transition_for_guard_not_good(net, transition)


def find_place(net,place_name):
    for place in net.places:
        if place.name == place_name:
            return place

def create_max_guard_place(net, transition_name, times, source):
    max_guard_place = PetriNet.Place(transition_name + "_guard")
    net.places.add(max_guard_place)
    for arc in net.arcs.copy():
        if arc.source == source:
            petri_utils.add_arc_from_to(arc.target, max_guard_place, net, times + 1)
    return max_guard_place


def minus_one_from_transitions(net,max_guard_place,list_of_transitions):
    for transition in list_of_transitions:
        petri_utils.add_arc_from_to(transition, max_guard_place, net,-1)

def minus_counter_to_list_of_activites(net, list_of_transitions_names, max_guard_place):
    list_of_transitions = found_transitions(net, list_of_transitions_names)
    minus_one_from_transitions(net,max_guard_place,list_of_transitions)
    # max_guard_place = PetriNet.Place("counter")
    # net.places.add(max_guard_place)
    #counter_to_list_of_transitions(net, max_guard_place, list_of_transitions)


def guard_of_max_times(net, transition_name, list_of_transitions_names, times, in_xor):
    transition= found_transition(net,transition_name)
    if in_xor == False:
        create_empty_transition_for_guard_not_good(net,transition)
        guard_of_min_times(net, transition_name + "_empty_transition", list_of_transitions_names, times+1, 1)
    source = find_place(net,"source")
    max_guard_place=create_max_guard_place(net,transition_name,times,source)
    minus_counter_to_list_of_activites(net, list_of_transitions_names,max_guard_place)
    add_min_guard_arc_to_transition(net, max_guard_place, transition, 1)

def guard_exactly_x_times(net, transition_name, list_of_transitions_names, times, in_xor):
    guard_of_min_times(net, transition_name, list_of_transitions_names, times, in_xor)
    guard_of_max_times(net, transition_name, list_of_transitions_names, times,1)

def guard_loop_at_most_x_times(net, transition_name, list_of_transitions_names, times):
    transition= found_transition(net,transition_name)
    source = find_place(net,"source")
    max_guard_place=create_max_guard_place(net,transition_name,times-2,source)
    #minus_counter_to_list_of_activites(net, list_of_transitions_names,max_guard_place)
    add_min_guard_arc_to_transition(net, max_guard_place, transition, 1)

def apply_or_guards(guards_parameters_list, guards_functions_list):
    for index_in_or in range (len(guards_functions_list)):
        functions = guards_functions_list[index_in_or]
        functions_paramater_list = guards_parameters_list[index_in_or]
        for index_of_function in range(len(functions)):
            function = functions[index_of_function]
            parameter_list = functions_paramater_list[index_of_function]
            function(*parameter_list)




def add_arcs_from_transition_to_place_of_or(net, empty_transitions_names, place_of_or):
    for empty_transitions_name in empty_transitions_names:
        empty_transition = found_transition(net, empty_transitions_name)
        petri_utils.add_arc_from_to(empty_transition, place_of_or, net, 1)
        empty_transition.label = None


def add_arc_from_place_to_transition(net,place_of_or, transition):
    petri_utils.add_arc_from_to(place_of_or, transition, net, 1)


def or_guards_transition(net, transition_name, guards_parameters_list, guards_functions_list, or_index, empty_transitions_names):
    place_of_or = PetriNet.Place("or place " + str(or_index))
    net.places.add(place_of_or)
    apply_or_guards(guards_parameters_list,guards_functions_list)
    add_arcs_from_transition_to_place_of_or(net, empty_transitions_names,place_of_or)
    transition = found_transition(net,transition_name)
    add_arc_from_place_to_transition(net,place_of_or,transition)


def found_arc(net, xor_place, transition):
    for arc in net.arcs:
        if arc.target == transition and arc.source == xor_place:
            return arc


def create_empty_transitions_for_or_guards(net,number_of_or_guards, index_of_or_for_name, xor_place_name):
    list_of_empty_transitions = []
    xor_place = found_place(net,xor_place_name)
    for index in range(number_of_or_guards):
        empty_transition_name =str(index_of_or_for_name) + " empty transition " + str(index+1)
        list_of_empty_transitions.append(empty_transition_name)
        empty_transition = PetriNet.Transition(empty_transition_name, empty_transition_name)
        net.transitions.add(empty_transition)
        add_arc_from_place_to_transition(net, xor_place, empty_transition)
    return list_of_empty_transitions


def replace_to_empty(net):
    for transition in net.transitions:
        if transition.label == "-":
            transition.label = None


def remove_xor_edge_from_option_with_xor(net,xor_place_name, transition_name):
    xor_place = found_place(net,xor_place_name)
    transition = found_transition(net,transition_name)
    arc = found_arc(net, xor_place, transition)
    net.arcs.remove(arc)
    transition.in_arcs.remove(arc)
    xor_place.out_arcs.remove(arc)


def ski_example():
    dress_for_ski = pm4py.ProcessTree(None, None, [], "dress for ski")
    seq = pm4py.ProcessTree("->", None, [], "seq")
    meat_dinner = pm4py.ProcessTree(None, None, [], "meat dinner")
    veg_dinner = pm4py.ProcessTree(None, None, [], "vegetarian dinner")
    empty_transition_2 = pm4py.ProcessTree(None, None, [], "-")
    green = pm4py.ProcessTree(None, None, [], "green")
    blue = pm4py.ProcessTree(None, None, [], "blue")
    red = pm4py.ProcessTree(None, None, [], "red")
    black = pm4py.ProcessTree(None, None, [], "black")
    breakfast = pm4py.ProcessTree(None, None, [], "breakfast")
    gym = pm4py.ProcessTree(None, None, [], "gym")
    xor_2 = pm4py.ProcessTree("X", None, [], "xor")
    xor_4 = pm4py.ProcessTree("X", None, [], "xor")
    loop = pm4py.ProcessTree("*", None, [], "loop")
    parallel = pm4py.ProcessTree("+", None, [], "parallel")
    dress_for_ski._set_parent(parallel)
    breakfast._set_parent(parallel)
    parallel._set_parent(seq)
    green._set_parent(xor_2)
    red._set_parent(xor_2)
    blue._set_parent(xor_2)
    black._set_parent(xor_2)
    xor_2._set_parent(loop)
    empty_transition_2._set_parent(loop)
    loop._set_parent(seq)
    gym._set_parent(seq)
    veg_dinner._set_parent(xor_4)
    meat_dinner._set_parent(xor_4)
    xor_4._set_parent(seq)

    dress_for_ski.children = []
    breakfast.children = []
    green.children = []
    blue.children = []
    red.children = []
    black.children = []
    parallel.children = [dress_for_ski,breakfast]
    empty_transition_2.children = []
    xor_2.children = [green,blue,red,black]
    loop.children = [xor_2,empty_transition_2]
    gym.children = []
    veg_dinner.children = []
    meat_dinner.children = []
    xor_4.children = [veg_dinner,meat_dinner]
    seq.children = [parallel,loop,gym,xor_4]


    net, im, fm = pm4py.convert_to_petri_net(seq)
    net.original_places=net.places.copy()
    # empty_transition_if_not(net,"breakfast")
    # guard_of_max_times(net,"gym",["black"],3,0)
    # guard_loop_at_most_x_times(net,"-",["green","blue","red","black"],20)
    # guard_of_min_times(net,"meat dinner",["gym"],1,1)
    # guard_of_max_times(net,"meat dinner",["breakfast"],0,1)
    # empty_transitions = create_empty_transitions_for_or_guards(net,2,1,"p_12")
    # remove_xor_edge_from_option_with_xor(net,"p_12","vegetarian dinner")
    # or_guards_transition(net,"vegetarian dinner",[[[net,empty_transitions[0],["gym"],0,1]], [[net,empty_transitions[1],["breakfast"],1,1]]],[[guard_of_max_times], [guard_of_min_times]],1, empty_transitions)
    # replace_to_empty(net)
    # guard_exactly_x_times(net, "vegetarian dinner", ["breakfast"], 1, 1)
    # guard_of_max_times(net, "vegetarian dinner", ["gym"], 0, 1)

    # #pm4py.view_process_tree(seq, format='png')
    # line_guard(list_a,list_b,net, "open bank")
    # #list_a_happens_less_than_list_b(list_b,list_a,net,"guard to b")
    # parallel_hapens_x_times("p_5", net, 10, "open bank")
    # for arc in net.arcs:
    #     if type(arc.target) is PetriNet.Transition and arc.target.label == "close bank":
    #         arc.weight=10
    return net,im,fm


def ski_example_with_guards():
    dress_for_ski = pm4py.ProcessTree(None, None, [], "dress for ski")
    seq = pm4py.ProcessTree("->", None, [], "seq")
    meat_dinner = pm4py.ProcessTree(None, None, [], "meat dinner")
    veg_dinner = pm4py.ProcessTree(None, None, [], "vegetarian dinner")
    empty_transition_2 = pm4py.ProcessTree(None, None, [], "-")
    green = pm4py.ProcessTree(None, None, [], "green")
    blue = pm4py.ProcessTree(None, None, [], "blue")
    red = pm4py.ProcessTree(None, None, [], "red")
    black = pm4py.ProcessTree(None, None, [], "black")
    breakfast = pm4py.ProcessTree(None, None, [], "breakfast")
    gym = pm4py.ProcessTree(None, None, [], "gym")
    xor_2 = pm4py.ProcessTree("X", None, [], "xor")
    xor_4 = pm4py.ProcessTree("X", None, [], "xor")
    loop = pm4py.ProcessTree("*", None, [], "loop")
    parallel = pm4py.ProcessTree("+", None, [], "parallel")
    dress_for_ski._set_parent(parallel)
    breakfast._set_parent(parallel)
    parallel._set_parent(seq)
    green._set_parent(xor_2)
    red._set_parent(xor_2)
    blue._set_parent(xor_2)
    black._set_parent(xor_2)
    xor_2._set_parent(loop)
    empty_transition_2._set_parent(loop)
    loop._set_parent(seq)
    gym._set_parent(seq)
    veg_dinner._set_parent(xor_4)
    meat_dinner._set_parent(xor_4)
    xor_4._set_parent(seq)

    dress_for_ski.children = []
    breakfast.children = []
    green.children = []
    blue.children = []
    red.children = []
    black.children = []
    parallel.children = [dress_for_ski,breakfast]
    empty_transition_2.children = []
    xor_2.children = [green,blue,red,black]
    loop.children = [xor_2,empty_transition_2]
    gym.children = []
    veg_dinner.children = []
    meat_dinner.children = []
    xor_4.children = [veg_dinner,meat_dinner]
    seq.children = [parallel,loop,gym,xor_4]


    net, im, fm = pm4py.convert_to_petri_net(seq)
    net.original_places=net.places.copy()
    empty_transition_if_not(net,"breakfast")
    guard_of_max_times(net,"gym",["black"],3,0)
    guard_loop_at_most_x_times(net,"-",["green","blue","red","black"],20)
    guard_of_min_times(net,"meat dinner",["gym"],1,1)
    guard_of_max_times(net,"meat dinner",["breakfast"],0,1)
    empty_transitions = create_empty_transitions_for_or_guards(net,2,1,"p_29")
    remove_xor_edge_from_option_with_xor(net,"p_29","vegetarian dinner")
    or_guards_transition(net,"vegetarian dinner",[[[net,empty_transitions[0],["gym"],0,1]], [[net,empty_transitions[1],["breakfast"],1,1]]],[[guard_of_max_times], [guard_of_min_times]],1, empty_transitions)
    replace_to_empty(net)
    # guard_exactly_x_times(net, "vegetarian dinner", ["breakfast"], 1, 1)
    # guard_of_max_times(net, "vegetarian dinner", ["gym"], 0, 1)

    # #pm4py.view_process_tree(seq, format='png')
    # line_guard(list_a,list_b,net, "open bank")
    # #list_a_happens_less_than_list_b(list_b,list_a,net,"guard to b")
    # parallel_hapens_x_times("p_5", net, 10, "open bank")
    # for arc in net.arcs:
    #     if type(arc.target) is PetriNet.Transition and arc.target.label == "close bank":
    #         arc.weight=10
    return net,im,fm

def apply_guards_on_net(net):
    net.original_places = net.places.copy()
    # net.original_places.add(found_place(net,"p_16"))
    # net.original_places.add(found_place(net,"p_26"))
    # net.original_places.add(found_place(net,"p_11"))
    # net.original_places.add(found_place(net,"p_21"))

    #empty_transition_if_not(net, "breakfast")
    group_fo_transitions_happen_x_times(net,found_places(net,["p_16", "p_11", "p_21", "p_26"]), 20, 1)
    guard_of_max_times(net, "gym", ["black"], 2, 1)
    guard_of_min_times(net,"skip_26",["black"],3,1)
    #guard_loop_at_most_x_times(net, "init_loop_22", ["green", "blue", "red", "black"], 20)
    guard_of_min_times(net, "meat dinner", ["gym"], 1, 1)
    guard_of_max_times(net, "meat dinner", ["breakfast"], 0, 1)
    empty_transitions = create_empty_transitions_for_or_guards(net, 2, 1, "p_29")
    remove_xor_edge_from_option_with_xor(net, "p_29", "vegetarian dinner")
    or_guards_transition(net, "vegetarian dinner", [[[net, empty_transitions[0], ["gym"], 0, 1]],
                                                    [[net, empty_transitions[1], ["breakfast"], 1, 1]]],
                         [[guard_of_max_times], [guard_of_min_times]], 1, empty_transitions)
    replace_to_empty(net)





