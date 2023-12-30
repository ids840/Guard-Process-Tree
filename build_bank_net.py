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

import build_ski_net


def found_transition(net, transition_name):
    for transition in net.transitions:
        if (transition.label == None and transition.name == transition_name) or transition.label == transition_name:
            return transition
def found_place(net, place_name):
    for place in net.places:
        if place.name == place_name:
            return place

def found_places(net,list_of_places_names):
    places = []
    for place_name in list_of_places_names:
        place = found_place(net,place_name)
        places.append(place)
    return places
def found_transitions(net,list_of_transitions_names):
    transitions = []
    for transition_name in list_of_transitions_names:
        transition = found_transition(net,transition_name)
        transitions.append(transition)
    return transitions

def find_place(net,place_name):
    for place in net.places:
        if place.name == place_name:
            return place



def replace_to_empty(net):
    for transition in net.transitions:
        if transition.label!= None and transition.label[0] == "-":
            transition.label = None


def found_start_transitions(net, source):
    start_transitions = []
    for arc in net.arcs:
        if arc.source == source:
            start_transitions.append(arc.target)
    return start_transitions


def add_arcs_from_start_transitions_to_parallel(net, place_parallel, start_transitions,number_of_tokens):
    for start_transition in start_transitions:
        petri_utils.add_arc_from_to(start_transition, place_parallel, net,number_of_tokens)


def remove_arcs(net, place_parallel, start_transitions):
    for arc in net.arcs.copy():
        for start_transition in start_transitions:
            if arc.source == start_transition and arc.target == place_parallel:
                net.arcs.remove(arc)


def change_weight_of_arcs_of_place(place_parallel_end,number_of_tokens):
    for arc in place_parallel_end.out_arcs:
        arc.weight = number_of_tokens


def parallel_hapens_x_times(place_parallel,place_parallel_end,net,number_of_tokens):
    source = found_place(net,"source")
    start_transitions = found_start_transitions(net,source)
    remove_arcs(net,place_parallel,start_transitions)
    add_arcs_from_start_transitions_to_parallel(net,place_parallel,start_transitions, number_of_tokens)
    change_weight_of_arcs_of_place(place_parallel_end,number_of_tokens)

def add_from_start_to_place(net,place,number_of_tokens):
    source = found_place(net,"source")
    start_transitions = found_start_transitions(net,source)
    for start_transition in start_transitions:
        petri_utils.add_arc_from_to(start_transition, place, net,number_of_tokens)

def add_places_for_last_transition_guard(net, transition_name):
    last_transition_is_not = PetriNet.Place("last transition is not " + transition_name)
    net.places.add(last_transition_is_not)
    add_from_start_to_place(net,last_transition_is_not,1)
    return last_transition_is_not


def add_arcs_from_transition(net,transition, last_transition_is_not):
    petri_utils.add_arc_from_to(last_transition_is_not, transition, net, "need 1 to execute, take all if execute")


def add_arcs_from_list_of_transitions(net,list_of_transitions, last_transition_is_not):
    for transition in list_of_transitions:
        petri_utils.add_arc_from_to(transition, last_transition_is_not, net, 1)


def last_transition_is_not_guard(net, transition_name, list_of_transitions_names):
    last_transition_is_not = add_places_for_last_transition_guard(net,transition_name)
    transition = found_transition(net,transition_name)
    list_of_transitions = found_transitions(net, list_of_transitions_names)
    add_arcs_from_transition(net,transition,last_transition_is_not)
    add_arcs_from_list_of_transitions(net,list_of_transitions,last_transition_is_not)


def add_arcs_from_transitions_more(net,list_of_transitions, place):
    for transition in list_of_transitions:
        petri_utils.add_arc_from_to(transition, place, net, 1)

def add_arcs_from_transitions_less(net,list_of_transitions, place):
    for transition in list_of_transitions:
        petri_utils.add_arc_from_to(transition, place, net, -1)




def reset_place_row(net, list_of_transitions, place, difference):
    for transition in list_of_transitions:
        petri_utils.add_arc_from_to(transition, place, net, str(difference) + " - left in destination place")


def list_of_not_row_guard(net, list_of_happens_more, list_of_happens_less, difference, index_of_row_guard):
    place_of_remain = PetriNet.Place("row place " + str(index_of_row_guard))
    net.places.add(place_of_remain)
    add_from_start_to_place(net, place_of_remain, difference)
    add_arcs_from_transitions_more(net, list_of_happens_more, place_of_remain)
    reset_place_row(net, list_of_happens_less, place_of_remain, difference)




def build_places_for_count_row(net, difference,  index_of_row_guard):
    places = []
    for i in range(difference):
        place = PetriNet.Place("row place " + str(index_of_row_guard) + " now row " + str(i))
        net.places.add(place)
        places.append(place)
    return places


def build_transitions_to_happens_more_transitions(net,places_count_row, change_row, can_do,index_of_row_guard):
    for index in range(len(places_count_row)-1):
        empty_transition = PetriNet.Transition("empty transition for row " + str(index_of_row_guard) + str(index), None)
        net.transitions.add(empty_transition)
        petri_utils.add_arc_from_to(change_row, empty_transition, net)
        petri_utils.add_arc_from_to(empty_transition, can_do, net)
        source = places_count_row[index]
        destination = places_count_row[index + 1]
        petri_utils.add_arc_from_to(source, empty_transition, net)
        petri_utils.add_arc_from_to(empty_transition, destination, net)



def  build_transitions_to_happens_less_transitions(net,place_of_remain,places_count_row,can_do,reset,index_of_row_guard):
    for index in range(len(places_count_row)):
        empty_transition = PetriNet.Transition("empty transition for reset " + str(index_of_row_guard) + str(index), None)
        net.transitions.add(empty_transition)
        petri_utils.add_arc_from_to(reset, empty_transition, net)
        petri_utils.add_arc_from_to(empty_transition, can_do, net)
        source = places_count_row[index]
        petri_utils.add_arc_from_to(source, empty_transition, net)
        petri_utils.add_arc_from_to(empty_transition, places_count_row[0], net)
        petri_utils.add_arc_from_to(empty_transition, place_of_remain, net,index)


def add_arcs_from_transitions_to_place(net, list_of_transitions, place):
    for transition in list_of_transitions:
        petri_utils.add_arc_from_to(transition,place, net, 1)


def add_arcs_from_place_to_transitions(net, place, transitions):
    for transition in transitions:
        petri_utils.add_arc_from_to(place, transition, net, 1)

def build_places_for_row(net, index_of_row_guard):
    place_of_remain = PetriNet.Place("row place " + str(index_of_row_guard))
    net.places.add(place_of_remain)
    can_do = PetriNet.Place("can do " + str(index_of_row_guard))
    net.places.add(can_do)
    reset = PetriNet.Place("reset " + str(index_of_row_guard))
    net.places.add(reset)
    change_row = PetriNet.Place("change_row " + str(index_of_row_guard))
    net.places.add(change_row)
    return place_of_remain,can_do,reset, change_row

def list_of_not_row_guard_syntactic_sugar_1(net, list_of_happens_more, list_of_happens_less, index_of_row_guard):
    place_of_remain = PetriNet.Place("can do " + str(index_of_row_guard))
    net.places.add(place_of_remain)
    add_from_start_to_place(net,place_of_remain,1)
    add_arcs_from_place_to_transitions(net,place_of_remain,list_of_happens_more)
    add_arcs_from_transitions_to_place(net,list_of_happens_less,place_of_remain)


def list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less,difference, index_of_row_guard):
    place_of_remain, can_do, reset, change_row = build_places_for_row(net,index_of_row_guard)
    add_from_start_to_place(net, place_of_remain, difference)
    add_from_start_to_place(net, can_do, 1)
    places_count_row = build_places_for_count_row(net,difference+1,index_of_row_guard)
    add_from_start_to_place(net,places_count_row[0],1)
    add_arcs_from_place_to_transitions(net,can_do,list_of_happens_more+list_of_happens_less)
    add_arcs_from_place_to_transitions(net,place_of_remain,list_of_happens_more)
    add_arcs_from_transitions_to_place(net,list_of_happens_more,change_row)
    add_arcs_from_transitions_to_place(net,list_of_happens_less,reset)
    build_transitions_to_happens_more_transitions(net,places_count_row, change_row, can_do,index_of_row_guard)
    build_transitions_to_happens_less_transitions(net,place_of_remain,places_count_row,can_do,reset,index_of_row_guard)


def add_arcs_from_place_to_places_transitions(net,place_of_remain, places):
    for place in places:
        arcs_out = place.out_arcs
        for arc in arcs_out:
            transition = arc.target
            petri_utils.add_arc_from_to(place_of_remain, transition, net, 1)



def guard_min_x_times(net, transition, list_of_transitions, times,index_for_transition):
    place = PetriNet.Place("happened " + str(index_for_transition))
    net.places.add(place)
    for transition_in_list in list_of_transitions:
        petri_utils.add_arc_from_to(transition_in_list, place, net)
    petri_utils.add_arc_from_to(place, transition, net,times)

def add_basic_transitions(net, turn_a, turn_b, enable_a, enable_b, list_a, list_b):
    petri_utils.add_arc_from_to(list_a[0], turn_b, net)
    petri_utils.add_arc_from_to(list_b[0], turn_a, net)

    petri_utils.add_arc_from_to(turn_a, list_a[0] , net)
    petri_utils.add_arc_from_to(turn_b, list_b[0], net)

    for transition_in_list_a in list_a[1:]:
        petri_utils.add_arc_from_to(transition_in_list_a, enable_a, net)

    for transition_in_list_b in list_b[1:]:
        petri_utils.add_arc_from_to(transition_in_list_b, enable_b, net)


def create_the_change_in_turn(petri_net, turn_a, turn_b, enable_a, enable_b):
    remain_turn_a = PetriNet.Transition("remain turn a", None)
    change_turn_to_a = PetriNet.Transition("change turn to a", None)
    remain_turn_b = PetriNet.Transition("remain turn b", None)
    change_turn_to_b = PetriNet.Transition("change turn to b", None)
    petri_net.transitions.add(remain_turn_a)
    petri_net.transitions.add(change_turn_to_a)
    petri_net.transitions.add(remain_turn_b)
    petri_net.transitions.add(change_turn_to_b)
    petri_utils.add_arc_from_to(enable_a, remain_turn_a, petri_net)
    petri_utils.add_arc_from_to(remain_turn_a, turn_a, petri_net)
    petri_utils.add_arc_from_to(enable_a, change_turn_to_a, petri_net)
    petri_utils.add_arc_from_to(turn_b, change_turn_to_a, petri_net)
    petri_utils.add_arc_from_to(change_turn_to_a, turn_a, petri_net)

    petri_utils.add_arc_from_to(enable_b, change_turn_to_b, petri_net)
    petri_utils.add_arc_from_to(turn_a, change_turn_to_b, petri_net)
    petri_utils.add_arc_from_to(change_turn_to_b, turn_b, petri_net)
    petri_utils.add_arc_from_to(enable_b, remain_turn_b, petri_net)
    petri_utils.add_arc_from_to(remain_turn_b, turn_b, petri_net)

def turn_places(petri_net,list_a,list_b):
    turn_a = PetriNet.Place("turn " + list_a[0].label)
    turn_b = PetriNet.Place("turn " + list_b[0].label)
    enable_a = PetriNet.Place("enable " + list_a[0].label)
    enable_b = PetriNet.Place("enable " + list_b[0].label)
    petri_net.places.add(turn_a)
    petri_net.places.add(turn_b)
    petri_net.places.add(enable_a)
    petri_net.places.add(enable_b)
    start_transitions = found_start_transitions(petri_net,found_place(petri_net,"source"))
    for start_transition in start_transitions:
        petri_utils.add_arc_from_to(start_transition, turn_a, petri_net)
    return turn_a,turn_b,enable_a,enable_b





def line_guard_general(list_a, list_b, net):
    turn_a,turn_b,enable_a,enable_b = turn_places(net,list_a,list_b)
    add_basic_transitions(net,turn_a,turn_b,enable_a,enable_b,list_a,list_b)
    create_the_change_in_turn(net,turn_a,turn_b,enable_a,enable_b)

def create_max_guard_place(net, transition, times,index_of_guard):
    max_guard_place = PetriNet.Place(transition.label + " guard " + str(index_of_guard))
    net.places.add(max_guard_place)
    start_transitions = found_start_transitions(net,found_place(net,"source"))
    for start_transition in start_transitions:
        petri_utils.add_arc_from_to(start_transition, max_guard_place, net, times + 1)
    return max_guard_place


def minus_one_from_transitions(net,max_guard_place,list_of_transitions):
    for transition in list_of_transitions:
        petri_utils.add_arc_from_to(transition, max_guard_place, net,-1)

def minus_counter_to_list_of_activites(net, list_of_transitions, max_guard_place):
    minus_one_from_transitions(net,max_guard_place,list_of_transitions)

def guard_of_max_times(net,transition, list_of_transitions, times,index_of_guard):
    max_guard_place = create_max_guard_place(net, transition, times,index_of_guard)
    minus_counter_to_list_of_activites(net, list_of_transitions, max_guard_place)
    add_arcs_from_place_to_transitions(net, max_guard_place, [transition])

def list_of_happens_more_guard(net, transitions,list_of_happens_more, list_of_happens_less):
    place_of_remain = PetriNet.Place("remain tokens for " + transitions[0].label)
    net.places.add(place_of_remain)
    add_from_start_to_place(net,place_of_remain,0)
    add_arcs_from_transitions_more(net,list_of_happens_more,place_of_remain)
    #add_arcs_from_transitions_less(net,list_of_happens_less,place_of_remain)
    add_arcs_from_place_to_transitions(net,place_of_remain,transitions)

def create_max_guard_place_remain(net, times,index_of_guard):
    max_guard_place = PetriNet.Place("remain " + str(index_of_guard))
    net.places.add(max_guard_place)
    start_transitions = found_start_transitions(net,found_place(net,"source"))
    for start_transition in start_transitions:
        petri_utils.add_arc_from_to(start_transition, max_guard_place, net, times)
    return max_guard_place

def transitions_happen_x_time(net, transitions, times,index_of_x_times):
    max_guard_place = create_max_guard_place_remain(net, times, index_of_x_times)
    add_arcs_from_place_to_transitions(net,max_guard_place,transitions)


def apply_guards_on_net(net):
    net.original_places = net.places.copy()
    transitions = found_transitions(net,["get into bank"])
    times = 10
    transitions_happen_x_time(net, transitions, times,1)
    transitions = found_transitions(net, ["get out from a", "get out from b"])
    times = 10
    transitions_happen_x_time(net, transitions, times, 2)
    list_a = found_transitions(net, ["get in line a", "get service in a"])
    list_b = found_transitions(net, ["get in line b", "get service in b"])
    line_guard_general(list_a, list_b, net)

    guard_min_x_times(net, found_transition(net, "close bank"), found_transitions(net, ["get into bank"]), 10, 1)
    guard_min_x_times(net, found_transition(net, "close bank"),
                          found_transitions(net, ["get out from a", "get out from b"]), 10, 2)
    #guard_of_max_times(net, found_transition(net, "close bank"), found_transitions(net, ["get into bank"]), 10, 1)
    # # guard_of_max_times(net, found_transition(net, "close bank"),
    # #                   found_transitions(net, ["get out from a", "get out from b"]), 10, 2)
    list_of_happens_more_guard(net,found_transitions(net,["get in line a", "get in line b"]),
                               found_transitions(net, ["get into bank"]),
                               found_transitions(net, ["get in line a", "get in line b"]))

    list_of_happens_more_guard(net, found_transitions(net, ["get service in a"]),
                               found_transitions(net, ["get in line a"]),
                               found_transitions(net, ["get service in a"]))

    list_of_happens_more_guard(net, found_transitions(net, ["get service in b"]),
                               found_transitions(net, ["get in line b"]),
                               found_transitions(net,  ["get service in b"]))

    list_of_happens_more_guard(net, found_transitions(net, ["get out from a"]),
                               found_transitions(net, ["get service in a"]),
                               found_transitions(net, ["get out from a"]))

    list_of_happens_more_guard(net, found_transitions(net, ["get out from b"]),
                               found_transitions(net,  ["get service in b"]),
                               found_transitions(net,  ["get out from b"]))

    list_of_not_row_guard_syntactic_sugar_1(net,found_transitions(net, ["get service in a"]),found_transitions(net, ["get out from a"]),1)
    list_of_not_row_guard_syntactic_sugar_1(net,found_transitions(net, ["get service in b"]),found_transitions(net, ["get out from b"]),2)
    list_of_not_row_guard_syntactic_sugar_1(net,found_transitions(net, ["get out from a"]),found_transitions(net, ["get service in a"]),3)
    list_of_not_row_guard_syntactic_sugar_1(net,found_transitions(net, ["get out from b"]),found_transitions(net, ["get service in b"]),4)

    replace_to_empty(net)
    return net
