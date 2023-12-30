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
        petri_utils.add_arc_from_to(place, transition, net, 1)

def add_arcs_from_transitions_less(net,list_of_transitions, place,difference):
    for transition in list_of_transitions:
        petri_utils.add_arc_from_to(transition, place, net, 1)


def list_of_happens_more_guard(net, list_of_happens_more, list_of_happens_less, difference,index_of_more):
    place_of_remain = PetriNet.Place("more place " + str(index_of_more))
    net.places.add(place_of_remain)
    add_from_start_to_place(net,place_of_remain,difference)
    add_arcs_from_transitions_more(net,list_of_happens_more,place_of_remain)
    add_arcs_from_transitions_less(net,list_of_happens_less,place_of_remain,difference)


def reset_place_row(net, list_of_transitions, place, difference):
    for transition in list_of_transitions:
        petri_utils.add_arc_from_to(transition, place, net, str(difference) + " - left in destination place")


def list_of_not_row_guard(net, list_of_happens_more, list_of_happens_less, difference, index_of_row_guard):
    place_of_remain = PetriNet.Place("row place " + str(index_of_row_guard))
    net.places.add(place_of_remain)
    add_from_start_to_place(net, place_of_remain, difference)
    add_arcs_from_transitions_more(net, list_of_happens_more, place_of_remain)
    reset_place_row(net, list_of_happens_less, place_of_remain, difference)


def build_guard_petri_net():
    choose_drama = pm4py.ProcessTree(None, None, [], "choose drama")
    choose_comedy = pm4py.ProcessTree(None, None, [], "choose comedy")
    choose_romantic = pm4py.ProcessTree(None, None, [], "choose romantic")
    watch_drama = pm4py.ProcessTree(None, None, [], "watch drama")
    watch_comedy = pm4py.ProcessTree(None, None, [], "watch comedy")
    watch_romantic = pm4py.ProcessTree(None, None, [], "watch romantic")
    finish_drama = pm4py.ProcessTree(None, None, [], "finish drama")
    finish_comedy = pm4py.ProcessTree(None, None, [], "finish comedy")
    finish_romantic = pm4py.ProcessTree(None, None, [], "finish romantic")
    empty_transition_drama = pm4py.ProcessTree(None, None, [], "-drama")
    empty_transition_comedy = pm4py.ProcessTree(None, None, [], "-comedy")
    empty_transition_romantic = pm4py.ProcessTree(None, None, [], "-romantic")
    seq_drama = pm4py.ProcessTree("->", None, [], "seq")
    seq_comedy = pm4py.ProcessTree("->", None, [], "seq")
    seq_romantic = pm4py.ProcessTree("->", None, [], "seq")
    loop_drama = pm4py.ProcessTree("*", None, [], "loop")
    loop_comedy = pm4py.ProcessTree("*", None, [], "loop")
    loop_romantic = pm4py.ProcessTree("*", None, [], "loop")
    xor = pm4py.ProcessTree("X", None, [], "xor")
    parallel = pm4py.ProcessTree("+", None, [], "parallel")

    watch_drama._set_parent(loop_drama)
    empty_transition_drama._set_parent(loop_drama)
    watch_comedy._set_parent(loop_comedy)
    empty_transition_comedy._set_parent(loop_comedy)
    watch_romantic._set_parent(loop_romantic)
    empty_transition_romantic._set_parent(loop_romantic)
    choose_drama._set_parent(seq_drama)
    loop_drama._set_parent(seq_drama)
    finish_drama._set_parent(seq_drama)
    choose_comedy._set_parent(seq_comedy)
    loop_comedy._set_parent(seq_comedy)
    finish_comedy._set_parent(seq_comedy)
    choose_romantic._set_parent(seq_romantic)
    loop_romantic._set_parent(seq_romantic)
    finish_romantic._set_parent(seq_romantic)
    seq_drama._set_parent(xor)
    seq_comedy._set_parent(xor)
    seq_romantic._set_parent(xor)
    xor._set_parent(parallel)

    choose_drama.children = []
    watch_drama.children = []
    empty_transition_drama.children = []
    finish_drama.children = []
    choose_comedy.children = []
    watch_comedy.children = []
    empty_transition_comedy.children = []
    finish_comedy.children = []
    choose_romantic.children = []
    watch_romantic.children = []
    empty_transition_romantic.children = []
    finish_romantic.children = []
    loop_drama.children = [watch_drama,empty_transition_drama]
    loop_comedy.children = [watch_comedy,empty_transition_comedy]
    loop_romantic.children = [watch_romantic,empty_transition_romantic]
    seq_drama.children = [choose_drama,loop_drama,finish_drama]
    seq_comedy.children = [choose_comedy,loop_comedy,finish_comedy]
    seq_romantic.children = [choose_romantic,loop_romantic,finish_romantic]
    xor.children = [seq_drama,seq_comedy,seq_romantic]
    parallel.children = [xor]

    net, im, fm = pm4py.convert_to_petri_net(parallel)
    # parallel_place = found_place(net,"p_3")
    # parallel_end_place = found_place(net,"p_4")
    # parallel_hapens_x_times(parallel_place,parallel_end_place,net,10)
    # list_of_happens_more = [found_transition(net, "choose drama")]
    # list_of_happens_less = [found_transition(net, "finish drama")]
    # difference = 1
    # list_of_happens_more_guard(net, list_of_happens_more, list_of_happens_less, difference, 1)
    # list_of_happens_more = [found_transition(net, "choose comedy")]
    # list_of_happens_less = [found_transition(net, "finish comedy")]
    # difference = 1
    # list_of_happens_more_guard(net, list_of_happens_more, list_of_happens_less, difference, 2)
    # list_of_happens_more = [found_transition(net, "choose romantic")]
    # list_of_happens_less = [found_transition(net, "finish romantic")]
    # difference = 1
    # list_of_happens_more_guard(net, list_of_happens_more, list_of_happens_less, difference, 3)
    # list_of_activities = ["choose comedy","choose romantic"]
    # last_transition_is_not_guard(net,"choose drama",list_of_activities)
    # list_of_activities = ["choose drama","choose romantic"]
    # last_transition_is_not_guard(net,"choose comedy",list_of_activities)
    # list_of_activities = ["choose comedy","choose drama"]
    # last_transition_is_not_guard(net,"choose romantic",list_of_activities)
    # list_of_happens_more = [found_transition(net,"choose drama"), found_transition(net,"choose comedy") , found_transition(net,"choose romantic")]
    # list_of_happens_less = [found_transition(net,"finish drama"), found_transition(net,"finish comedy") , found_transition(net,"finish romantic")]
    # difference = 2
    # list_of_happens_more_guard(net,list_of_happens_more,list_of_happens_less,difference,1)
    list_of_happens_more = [found_transition(net,"watch drama")]
    list_of_happens_less = [found_transition(net,"watch comedy"),
                            found_transition(net, "watch romantic")]
    difference = 3
    list_of_not_row_guard(net,list_of_happens_more,list_of_happens_less,difference,4)
    # list_of_happens_more = [found_transition(net,"watch comedy")]
    # list_of_happens_less = [found_transition(net,"watch drama"),
    #                         found_transition(net, "watch romantic")]
    # difference = 3
    # list_of_happens_more_guard(net, list_of_happens_more, list_of_happens_less, difference, 5)
    # list_of_happens_more = [found_transition(net,"watch romantic")]
    # list_of_happens_less = [found_transition(net,"watch comedy"),
    #                         found_transition(net, "watch drama")]
    # difference = 3
    # list_of_happens_more_guard(net, list_of_happens_more, list_of_happens_less, difference, 6)
    # build_ski_net.guard_loop_at_most_x_times(net,"-drama",[],10)
    # build_ski_net.guard_loop_at_most_x_times(net,"-comedy",[],10)
    # build_ski_net.guard_loop_at_most_x_times(net,"-romantic",[],10)

    replace_to_empty(net)
    pm4py.view_petri_net(net,im,fm)

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

def list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, index_of_row_guard):
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


def group_fo_transitions_happen_x_times(net, places, number_of_tokens,index_of_row_guard):
    source = found_place(net, "source")
    start_transitions = found_start_transitions(net, source)
    place_of_remain = PetriNet.Place("counter place " + str(index_of_row_guard))
    net.places.add(place_of_remain)
    add_arcs_from_start_transitions_to_parallel(net, place_of_remain, start_transitions, number_of_tokens)
    add_arcs_from_place_to_places_transitions(net,place_of_remain, places)


def build_inductive_guard_petri_net():
    choose_drama = pm4py.ProcessTree(None, None, [], "choose drama")
    choose_comedy = pm4py.ProcessTree(None, None, [], "choose comedy")
    choose_romantic = pm4py.ProcessTree(None, None, [], "choose romantic")
    watch_drama = pm4py.ProcessTree(None, None, [], "watch drama")
    watch_comedy = pm4py.ProcessTree(None, None, [], "watch comedy")
    watch_romantic = pm4py.ProcessTree(None, None, [], "watch romantic")
    finish_drama = pm4py.ProcessTree(None, None, [], "finish drama")
    finish_comedy = pm4py.ProcessTree(None, None, [], "finish comedy")
    finish_romantic = pm4py.ProcessTree(None, None, [], "finish romantic")
    empty_transition_drama = pm4py.ProcessTree(None, None, [], None)
    empty_transition_comedy = pm4py.ProcessTree(None, None, [], None)
    empty_transition_romantic = pm4py.ProcessTree(None, None, [], None)
    seq_drama = pm4py.ProcessTree("->", None, [], "seq")
    seq_comedy = pm4py.ProcessTree("->", None, [], "seq")
    seq_romantic = pm4py.ProcessTree("->", None, [], "seq")
    loop_drama = pm4py.ProcessTree("*", None, [], "loop")
    loop_comedy = pm4py.ProcessTree("*", None, [], "loop")
    loop_romantic = pm4py.ProcessTree("*", None, [], "loop")
    loop_seq_drama = pm4py.ProcessTree("*", None, [], "loop")
    loop_seq_comedy = pm4py.ProcessTree("*", None, [], "loop")
    loop_seq_romantic = pm4py.ProcessTree("*", None, [], "loop")
    empty_transition_drama_loop = pm4py.ProcessTree(None, None, [], None)
    empty_transition_comedy_loop = pm4py.ProcessTree(None, None, [], None)
    empty_transition_romantic_loop = pm4py.ProcessTree(None, None, [], None)
    parallel = pm4py.ProcessTree("+", None, [], "parallel")

    watch_drama._set_parent(loop_drama)
    empty_transition_drama._set_parent(loop_drama)
    watch_comedy._set_parent(loop_comedy)
    empty_transition_comedy._set_parent(loop_comedy)
    watch_romantic._set_parent(loop_romantic)
    empty_transition_romantic._set_parent(loop_romantic)
    choose_drama._set_parent(seq_drama)
    loop_drama._set_parent(seq_drama)
    finish_drama._set_parent(seq_drama)
    choose_comedy._set_parent(seq_comedy)
    loop_comedy._set_parent(seq_comedy)
    finish_comedy._set_parent(seq_comedy)
    choose_romantic._set_parent(seq_romantic)
    loop_romantic._set_parent(seq_romantic)
    finish_romantic._set_parent(seq_romantic)
    seq_drama._set_parent(loop_seq_drama)
    seq_comedy._set_parent(loop_seq_comedy)
    seq_romantic._set_parent(loop_seq_romantic)
    empty_transition_drama_loop._set_parent(loop_seq_drama)
    empty_transition_comedy_loop._set_parent(loop_seq_comedy)
    empty_transition_romantic_loop._set_parent(loop_seq_romantic)
    loop_seq_drama._set_parent(parallel)
    loop_seq_comedy._set_parent(parallel)
    loop_seq_romantic._set_parent(parallel)

    choose_drama.children = []
    watch_drama.children = []
    empty_transition_drama.children = []
    finish_drama.children = []
    choose_comedy.children = []
    watch_comedy.children = []
    empty_transition_comedy.children = []
    finish_comedy.children = []
    choose_romantic.children = []
    watch_romantic.children = []
    empty_transition_romantic.children = []
    finish_romantic.children = []
    loop_drama.children = [watch_drama,empty_transition_drama]
    loop_comedy.children = [watch_comedy,empty_transition_comedy]
    loop_romantic.children = [watch_romantic,empty_transition_romantic]
    seq_drama.children = [choose_drama,loop_drama,finish_drama]
    seq_comedy.children = [choose_comedy,loop_comedy,finish_comedy]
    seq_romantic.children = [choose_romantic,loop_romantic,finish_romantic]
    loop_seq_drama.children = [seq_drama, empty_transition_drama_loop]
    loop_seq_comedy.children = [seq_comedy, empty_transition_comedy_loop]
    loop_seq_romantic.children = [seq_romantic, empty_transition_romantic_loop]
    parallel.children = [loop_seq_drama,loop_seq_comedy, loop_seq_romantic]
    pm4py.view_process_tree(parallel)
    net, im, fm = pm4py.convert_to_petri_net(parallel)
    # parallel_place = found_place(net,"p_3")
    # parallel_end_place = found_place(net,"p_4")
    #group_fo_transitions_happen_x_times(net,found_places(net,["p_5", "p_15", "p_25"]),10,1)
    #parallel_hapens_x_times(parallel_place,parallel_end_place,net,10)
    # list_of_happens_more = [found_transition(net, "choose drama")]
    # list_of_happens_less = [found_transition(net, "finish drama")]
    # difference = 1
    # list_of_happens_more_guard(net, list_of_happens_more, list_of_happens_less, difference, 1)
    # list_of_happens_more = [found_transition(net, "choose comedy")]
    # list_of_happens_less = [found_transition(net, "finish comedy")]
    # difference = 1
    # list_of_happens_more_guard(net, list_of_happens_more, list_of_happens_less, difference, 2)
    # list_of_happens_more = [found_transition(net, "choose romantic")]
    # list_of_happens_less = [found_transition(net, "finish romantic")]
    # difference = 1
    # list_of_happens_more_guard(net, list_of_happens_more, list_of_happens_less, difference, 3)
    # list_of_activities = ["choose comedy","choose romantic"]
    # last_transition_is_not_guard(net,"choose drama",list_of_activities)
    # list_of_activities = ["choose drama","choose romantic"]
    # last_transition_is_not_guard(net,"choose comedy",list_of_activities)
    # list_of_activities = ["choose comedy","choose drama"]
    # last_transition_is_not_guard(net,"choose romantic",list_of_activities)
    # list_of_happens_more = [found_transition(net,"choose drama"), found_transition(net,"choose comedy") , found_transition(net,"choose romantic")]
    # list_of_happens_less = [found_transition(net,"finish drama"), found_transition(net,"finish comedy") , found_transition(net,"finish romantic")]
    # difference = 2
    #list_of_happens_more_guard(net,list_of_happens_more,list_of_happens_less,difference,1)
    list_of_happens_more = [found_transition(net,"watch drama")]
    list_of_happens_less = [found_transition(net,"watch comedy"),
                            found_transition(net, "watch romantic")]
    difference = 3
    # list_of_not_row_guard(net,list_of_happens_more,list_of_happens_less,difference,4)
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 4)
    list_of_happens_more = [found_transition(net,"watch comedy")]
    list_of_happens_less = [found_transition(net,"watch drama"),
                            found_transition(net, "watch romantic")]
    difference = 3
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 4)
    list_of_happens_more = [found_transition(net,"watch romantic")]
    list_of_happens_less = [found_transition(net,"watch comedy"),
                            found_transition(net, "watch drama")]
    difference = 3
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 4)


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


def build_inductive_guard_petri_net_tv2():
    choose_drama = pm4py.ProcessTree(None, None, [], "choose drama")
    choose_comedy = pm4py.ProcessTree(None, None, [], "choose comedy")
    choose_romantic = pm4py.ProcessTree(None, None, [], "choose romantic")
    watch_drama = pm4py.ProcessTree(None, None, [], "watch drama")
    watch_comedy = pm4py.ProcessTree(None, None, [], "watch comedy")
    watch_romantic = pm4py.ProcessTree(None, None, [], "watch romantic")
    finish_drama = pm4py.ProcessTree(None, None, [], "finish drama")
    finish_comedy = pm4py.ProcessTree(None, None, [], "finish comedy")
    finish_romantic = pm4py.ProcessTree(None, None, [], "finish romantic")
    empty_transition_drama = pm4py.ProcessTree(None, None, [], None)
    empty_transition_comedy = pm4py.ProcessTree(None, None, [], None)
    empty_transition_romantic = pm4py.ProcessTree(None, None, [], None)
    seq_drama = pm4py.ProcessTree("->", None, [], "seq")
    seq_comedy = pm4py.ProcessTree("->", None, [], "seq")
    seq_romantic = pm4py.ProcessTree("->", None, [], "seq")
    loop_drama = pm4py.ProcessTree("*", None, [], "loop")
    loop_comedy = pm4py.ProcessTree("*", None, [], "loop")
    loop_romantic = pm4py.ProcessTree("*", None, [], "loop")
    loop_seq_drama = pm4py.ProcessTree("*", None, [], "loop")
    loop_seq_comedy = pm4py.ProcessTree("*", None, [], "loop")
    loop_seq_romantic = pm4py.ProcessTree("*", None, [], "loop")
    empty_transition_drama_loop = pm4py.ProcessTree(None, None, [], None)
    empty_transition_comedy_loop = pm4py.ProcessTree(None, None, [], None)
    empty_transition_romantic_loop = pm4py.ProcessTree(None, None, [], None)
    parallel = pm4py.ProcessTree("+", None, [], "parallel")

    watch_drama._set_parent(loop_drama)
    empty_transition_drama._set_parent(loop_drama)
    watch_comedy._set_parent(loop_comedy)
    empty_transition_comedy._set_parent(loop_comedy)
    watch_romantic._set_parent(loop_romantic)
    empty_transition_romantic._set_parent(loop_romantic)
    choose_drama._set_parent(seq_drama)
    loop_drama._set_parent(seq_drama)
    finish_drama._set_parent(seq_drama)
    choose_comedy._set_parent(seq_comedy)
    loop_comedy._set_parent(seq_comedy)
    finish_comedy._set_parent(seq_comedy)
    choose_romantic._set_parent(seq_romantic)
    loop_romantic._set_parent(seq_romantic)
    finish_romantic._set_parent(seq_romantic)
    seq_drama._set_parent(loop_seq_drama)
    seq_comedy._set_parent(loop_seq_comedy)
    seq_romantic._set_parent(loop_seq_romantic)
    empty_transition_drama_loop._set_parent(loop_seq_drama)
    empty_transition_comedy_loop._set_parent(loop_seq_comedy)
    empty_transition_romantic_loop._set_parent(loop_seq_romantic)
    loop_seq_drama._set_parent(parallel)
    loop_seq_comedy._set_parent(parallel)
    loop_seq_romantic._set_parent(parallel)

    choose_drama.children = []
    watch_drama.children = []
    empty_transition_drama.children = []
    finish_drama.children = []
    choose_comedy.children = []
    watch_comedy.children = []
    empty_transition_comedy.children = []
    finish_comedy.children = []
    choose_romantic.children = []
    watch_romantic.children = []
    empty_transition_romantic.children = []
    finish_romantic.children = []
    loop_drama.children = [watch_drama,empty_transition_drama]
    loop_comedy.children = [watch_comedy,empty_transition_comedy]
    loop_romantic.children = [watch_romantic,empty_transition_romantic]
    seq_drama.children = [choose_drama,loop_drama,finish_drama]
    seq_comedy.children = [choose_comedy,loop_comedy,finish_comedy]
    seq_romantic.children = [choose_romantic,loop_romantic,finish_romantic]
    loop_seq_drama.children = [seq_drama, empty_transition_drama_loop]
    loop_seq_comedy.children = [seq_comedy, empty_transition_comedy_loop]
    loop_seq_romantic.children = [seq_romantic, empty_transition_romantic_loop]
    parallel.children = [loop_seq_drama,loop_seq_comedy, loop_seq_romantic]
    pm4py.view_process_tree(parallel)
    net, im, fm = pm4py.convert_to_petri_net(parallel)
    # parallel_place = found_place(net,"p_3")
    # parallel_end_place = found_place(net,"p_4")
    #group_fo_transitions_happen_x_times(net,found_places(net,["p_5", "p_15", "p_25"]),10,1)
    #parallel_hapens_x_times(parallel_place,parallel_end_place,net,10)
    # list_of_happens_more = [found_transition(net, "choose drama")]
    # list_of_happens_less = [found_transition(net, "finish drama")]
    # difference = 1
    # list_of_happens_more_guard(net, list_of_happens_more, list_of_happens_less, difference, 1)
    # list_of_happens_more = [found_transition(net, "choose comedy")]
    # list_of_happens_less = [found_transition(net, "finish comedy")]
    # difference = 1
    # list_of_happens_more_guard(net, list_of_happens_more, list_of_happens_less, difference, 2)
    # list_of_happens_more = [found_transition(net, "choose romantic")]
    # list_of_happens_less = [found_transition(net, "finish romantic")]
    # difference = 1
    # list_of_happens_more_guard(net, list_of_happens_more, list_of_happens_less, difference, 3)
    # list_of_activities = ["choose comedy","choose romantic"]
    # last_transition_is_not_guard(net,"choose drama",list_of_activities)
    # list_of_activities = ["choose drama","choose romantic"]
    # last_transition_is_not_guard(net,"choose comedy",list_of_activities)
    # list_of_activities = ["choose comedy","choose drama"]
    # last_transition_is_not_guard(net,"choose romantic",list_of_activities)
    list_of_happens_more = [found_transition(net,"choose drama"), found_transition(net,"choose comedy") , found_transition(net,"choose romantic")]
    list_of_happens_less = [found_transition(net,"finish drama"), found_transition(net,"finish comedy") , found_transition(net,"finish romantic")]
    difference = 2
    list_of_happens_more_guard(net,list_of_happens_more,list_of_happens_less,difference,1)
    list_of_happens_more = [found_transition(net,"choose drama")]
    list_of_happens_less = [found_transition(net,"choose comedy"),
                            found_transition(net, "choose romantic")]
    difference = 1
    # list_of_not_row_guard(net,list_of_happens_more,list_of_happens_less,difference,4)
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 4)
    list_of_happens_more = [found_transition(net,"choose comedy")]
    list_of_happens_less = [found_transition(net,"choose drama"),
                            found_transition(net, "choose romantic")]
    difference = 1
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 4)
    list_of_happens_more = [found_transition(net,"choose romantic")]
    list_of_happens_less = [found_transition(net,"choose comedy"),
                            found_transition(net, "choose drama")]
    difference = 1
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 4)


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


def build_inductive_guard_petri_net_original():
    choose_drama = pm4py.ProcessTree(None, None, [], "choose drama")
    choose_comedy = pm4py.ProcessTree(None, None, [], "choose comedy")
    choose_romantic = pm4py.ProcessTree(None, None, [], "choose romantic")
    watch_drama = pm4py.ProcessTree(None, None, [], "watch drama")
    watch_comedy = pm4py.ProcessTree(None, None, [], "watch comedy")
    watch_romantic = pm4py.ProcessTree(None, None, [], "watch romantic")
    finish_drama = pm4py.ProcessTree(None, None, [], "finish drama")
    finish_comedy = pm4py.ProcessTree(None, None, [], "finish comedy")
    finish_romantic = pm4py.ProcessTree(None, None, [], "finish romantic")
    empty_transition_drama = pm4py.ProcessTree(None, None, [], None)
    empty_transition_comedy = pm4py.ProcessTree(None, None, [], None)
    empty_transition_romantic = pm4py.ProcessTree(None, None, [], None)
    seq_drama = pm4py.ProcessTree("->", None, [], "seq")
    seq_comedy = pm4py.ProcessTree("->", None, [], "seq")
    seq_romantic = pm4py.ProcessTree("->", None, [], "seq")
    loop_drama = pm4py.ProcessTree("*", None, [], "loop")
    loop_comedy = pm4py.ProcessTree("*", None, [], "loop")
    loop_romantic = pm4py.ProcessTree("*", None, [], "loop")
    loop_seq_drama = pm4py.ProcessTree("*", None, [], "loop")
    loop_seq_comedy = pm4py.ProcessTree("*", None, [], "loop")
    loop_seq_romantic = pm4py.ProcessTree("*", None, [], "loop")
    empty_transition_drama_loop = pm4py.ProcessTree(None, None, [], None)
    empty_transition_comedy_loop = pm4py.ProcessTree(None, None, [], None)
    empty_transition_romantic_loop = pm4py.ProcessTree(None, None, [], None)
    parallel = pm4py.ProcessTree("+", None, [], "parallel")

    watch_drama._set_parent(loop_drama)
    empty_transition_drama._set_parent(loop_drama)
    watch_comedy._set_parent(loop_comedy)
    empty_transition_comedy._set_parent(loop_comedy)
    watch_romantic._set_parent(loop_romantic)
    empty_transition_romantic._set_parent(loop_romantic)
    choose_drama._set_parent(seq_drama)
    loop_drama._set_parent(seq_drama)
    finish_drama._set_parent(seq_drama)
    choose_comedy._set_parent(seq_comedy)
    loop_comedy._set_parent(seq_comedy)
    finish_comedy._set_parent(seq_comedy)
    choose_romantic._set_parent(seq_romantic)
    loop_romantic._set_parent(seq_romantic)
    finish_romantic._set_parent(seq_romantic)
    seq_drama._set_parent(loop_seq_drama)
    seq_comedy._set_parent(loop_seq_comedy)
    seq_romantic._set_parent(loop_seq_romantic)
    empty_transition_drama_loop._set_parent(loop_seq_drama)
    empty_transition_comedy_loop._set_parent(loop_seq_comedy)
    empty_transition_romantic_loop._set_parent(loop_seq_romantic)
    loop_seq_drama._set_parent(parallel)
    loop_seq_comedy._set_parent(parallel)
    loop_seq_romantic._set_parent(parallel)

    choose_drama.children = []
    watch_drama.children = []
    empty_transition_drama.children = []
    finish_drama.children = []
    choose_comedy.children = []
    watch_comedy.children = []
    empty_transition_comedy.children = []
    finish_comedy.children = []
    choose_romantic.children = []
    watch_romantic.children = []
    empty_transition_romantic.children = []
    finish_romantic.children = []
    loop_drama.children = [watch_drama,empty_transition_drama]
    loop_comedy.children = [watch_comedy,empty_transition_comedy]
    loop_romantic.children = [watch_romantic,empty_transition_romantic]
    seq_drama.children = [choose_drama,loop_drama,finish_drama]
    seq_comedy.children = [choose_comedy,loop_comedy,finish_comedy]
    seq_romantic.children = [choose_romantic,loop_romantic,finish_romantic]
    loop_seq_drama.children = [seq_drama, empty_transition_drama_loop]
    loop_seq_comedy.children = [seq_comedy, empty_transition_comedy_loop]
    loop_seq_romantic.children = [seq_romantic, empty_transition_romantic_loop]
    parallel.children = [loop_seq_drama,loop_seq_comedy, loop_seq_romantic]
    net, im, fm = pm4py.convert_to_petri_net(parallel)
    pm4py.view_petri_net(net,im,fm)
    return net,im,fm


def apply_guards_on_net(net):
    net.original_places = net.places.copy()

    list_of_happens_more = [found_transition(net,"watch drama")]
    list_of_happens_less = [found_transition(net,"watch comedy"),
                            found_transition(net, "watch romantic")]
    difference = 2
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 1)
    list_of_happens_more = [found_transition(net,"watch comedy")]
    list_of_happens_less = [found_transition(net,"watch drama"),
                            found_transition(net, "watch romantic")]
    difference = 2
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 2)
    list_of_happens_more = [found_transition(net,"watch romantic")]
    list_of_happens_less = [found_transition(net,"watch comedy"),
                            found_transition(net, "watch drama")]
    difference = 2
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 3)

    list_of_happens_more = [found_transition(net, "choose drama")]
    list_of_happens_less = [found_transition(net, "choose comedy"),
                            found_transition(net, "choose romantic")]
    difference = 1
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 4)
    list_of_happens_more = [found_transition(net, "choose comedy")]
    list_of_happens_less = [found_transition(net, "choose drama"),
                            found_transition(net, "choose romantic")]
    difference = 1
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 5)
    list_of_happens_more = [found_transition(net, "choose romantic")]
    list_of_happens_less = [found_transition(net, "choose comedy"),
                            found_transition(net, "choose drama")]
    difference=1
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 6)

    replace_to_empty(net)

def apply_guards_on_net_2(net):
    net.original_places = net.places.copy()
    list_of_happens_more = [found_transition(net, "watch drama")]
    list_of_happens_less = [found_transition(net, "watch comedy"),
                            found_transition(net, "watch romantic")]
    difference = 2
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 1)
    list_of_happens_more = [found_transition(net, "watch comedy")]
    list_of_happens_less = [found_transition(net, "watch drama"),
                            found_transition(net, "watch romantic")]
    difference = 2
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 2)
    list_of_happens_more = [found_transition(net, "watch romantic")]
    list_of_happens_less = [found_transition(net, "watch comedy"),
                            found_transition(net, "watch drama")]
    difference = 2
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 3)

    list_of_happens_more = [found_transition(net, "choose drama")]
    list_of_happens_less = [found_transition(net, "choose comedy"),
                            found_transition(net, "choose romantic")]
    difference = 1
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 4)
    list_of_happens_more = [found_transition(net, "choose comedy")]
    list_of_happens_less = [found_transition(net, "choose drama"),
                            found_transition(net, "choose romantic")]
    difference = 1
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 5)
    list_of_happens_more = [found_transition(net, "choose romantic")]
    list_of_happens_less = [found_transition(net, "choose comedy"),
                            found_transition(net, "choose drama")]
    difference = 1
    list_of_not_row_guard_syntactic_sugar(net, list_of_happens_more, list_of_happens_less, difference, 6)

    replace_to_empty(net)
