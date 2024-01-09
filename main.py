# This is a sample Python script.
import csv
import operator
from pm4py.objects.conversion.process_tree import converter as process_tree_converter

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pm4py

import pandas

from datetime import datetime

from pm4py import ProcessTree
from pm4py.algo.conformance.tokenreplay.variants import token_replay
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator

from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator

from pm4py.objects.petri_net.obj import PetriNet, Marking

from pm4py.objects.petri_net.utils import petri_utils

import random

import datetime

import Decision_Tree_To_Guards
import build_bank_net
import build_ski_net
import build_tv_net


def simulate_execution(petri_net, initial_marking, final_marking, num_cases=10):
    event_log = []

    for _ in range(num_cases):
        case_id = f"Case_{_ + 1}"
        current_marking = initial_marking.copy()
        trace = []

        while current_marking not in final_marking:
            enabled_transitions = pm4py.objects.petri_net.semantics.enabled_transitions(petri_net, current_marking)
            if not enabled_transitions:
                break

            # Choose a random enabled transition
            random_number = random.randint(0, len(enabled_transitions) - 1)
            chosen_transition = list(enabled_transitions)[random_number]

            # Simulate the execution of the transition
            event = {
                "case_id": case_id,
                "activity": chosen_transition.label,
                "timestamp": datetime.datetime.now().isoformat(),
            }
            if chosen_transition.label is not None:
                trace.append(event)

            current_marking = pm4py.objects.petri_net.semantics.execute(chosen_transition, petri_net, current_marking)

        event_log.extend(trace)

    return event_log


def import_csv(file_path):
    event_log = pandas.read_csv(file_path, sep=',')
    event_log['case ID'] = event_log['case ID'].astype(str)
    event_log['activity'] = event_log['activity'].astype(str)
    event_log['timestamp'] = pandas.to_datetime(event_log['timestamp'],format='mixed')
    return event_log
    # event_log = pandas.read_csv(file_path)
    # event_log['case ID'] = event_log['case ID'].astype(str)
    # event_log['activity'] = event_log['activity'].astype(str)
    # event_log['timestamp'] = pandas.to_datetime(event_log['timestamp'])
    # return event_log


def petri_net_by_inductive(log):
    net, initial_marking, final_marking = pm4py.discovery.discover_petri_net_inductive(log, False, 0.0, "activity",
                                                                                       "timestamp", "case ID")
    return net, initial_marking, final_marking


def petri_net_by_alpha(log):
    net, initial_marking, final_marking = pm4py.discovery.discover_petri_net_alpha(log, "activity", "timestamp",
                                                                                   "case ID")
    return net, initial_marking, final_marking


def petri_net_by_heuristics(log):
    net, initial_marking, final_marking = pm4py.discovery.discover_petri_net_heuristics(log, 0.5, 0.65, 0.5, "activity",
                                                                                        "timestamp", "case ID")
    return net, initial_marking, final_marking


def petri_net_by_ilp(log):
    net, initial_marking, final_marking = pm4py.discovery.discover_petri_net_ilp(log, 1.0, "activity", "timestamp",
                                                                                 "case ID")
    return net, initial_marking, final_marking


def print_petri_net(net, initial_marking, final_marking):
    pm4py.write_pnml(net, initial_marking, final_marking, "createdPetriNet1.pnml")
    pm4py.view_petri_net(net, initial_marking, final_marking)


def print_confermance(log, net, initial_marking, final_marking):
    dict_of_results = pm4py.conformance_diagnostics_token_based_replay(log, net, initial_marking, final_marking,
                                                                       "activity", "timestamp", "case ID")
    print(dict_of_results)


def dfg(log):
    dfg, start_activity, end_activity = pm4py.discover_directly_follows_graph(log, "activity", "timestamp", "case ID")
    pm4py.view_dfg(dfg, start_activity, end_activity)


def create_new_process_tree(process_tree):
    pass


def evaluation_1(log_path):
    log = import_csv(log_path)
    pro_tree = pm4py.discover_process_tree_inductive(log, 0.0, True, "activity", "timestamp", "case ID")
    pm4py.view_process_tree(pro_tree)
    net_1, initial_marking_1, final_marking_1 = petri_net_by_inductive(log)
    print_petri_net(net_1, initial_marking_1, final_marking_1)
    net_2, initial_marking_2, final_marking_2 = petri_net_by_alpha(log)
    # print_petri_net(net_2, initial_marking_2, final_marking_2)
    net_3, initial_marking_3, final_marking_3 = petri_net_by_ilp(log)
    # print_petri_net(net_2, initial_marking_3, final_marking_3)
    net_4, initial_marking_4, final_marking_4 = petri_net_by_heuristics(log)
    # print_petri_net(net_4, initial_marking_4, final_marking_4)
    print_confermance(log, net_4, initial_marking_4, final_marking_4)
    # dfg(log)
    # process_tree = pm4py.discover_process_tree_inductive(log, 0.0, True, "activity", "timestamp", "case ID")
    # pm4py.view_process_tree(process_tree)
    # net, initial_marking, final_marking = pm4py.objects.conversion.process_tree.variants.to_petri_net.apply(
    # process_tree)

    # pm4py.write_pnml(net, initial_marking, final_marking, "createdPetriNet1.pnml")
    # pm4py.view_petri_net(net, initial_marking, final_marking)
    fitness = pm4py.fitness_token_based_replay(log, net_4, initial_marking_4, final_marking_4, "activity", "timestamp",
                                               "case ID")
    prec = pm4py.precision_token_based_replay(log, net_4, initial_marking_4, final_marking_4, "activity", "timestamp",
                                              "case ID")
    # gen = generalization_evaluator.apply(log, net, initial_marking, final_marking)
    simp = simplicity_evaluator.apply(net_4)
    print(fitness)
    print("prec: " + str(prec))
    # print("gen: " + gen)
    print("simp: " + str(simp))


def evaluation(log, net, initial_marking, final_marking):
    # replayed_traces = pm4py.conformance_diagnostics_token_based_replay(log, net, initial_marking, final_marking, "activity", "timestamp",
    #                                           "case ID")
    # for trace in replayed_traces:
    #      if trace['missing_tokens'] > 0:
    #          print(trace)
    #print(pm4py.analysis.check_is_workflow_net(net))
#    print(pm4py.analysis.check_soundness(net,initial_marking,final_marking))
    fitness = pm4py.fitness_token_based_replay(log, net, initial_marking, final_marking, "activity", "timestamp",
                                            "case ID")
    prec = pm4py.precision_token_based_replay(log, net, initial_marking, final_marking, "activity", "timestamp",
                                              "case ID")
    # gen = generalization_evaluator.apply(log, net, initial_marking, final_marking)
    simp = simplicity_evaluator.apply(net)
    print(fitness)
    print("prec: " + str(prec))
    # print("gen: " + gen)
    print("simp: " + str(simp))


# Function that check for each transition if we can do it
def check_if_can_do_transition(transition: PetriNet.Transition, dict_of_tokens):
    arcs_in = transition.in_arcs
    for arc in arcs_in:
        if dict_of_tokens[arc.source] == 0:
            return False
    return True


# Function that return set of the None transitions that we can do
def group_of_can_do_transitions(transitions, dict_of_tokens):
    set_of_None_can_do_transitions = set()
    for transition in transitions:
        if transition.label == None:
            if check_if_can_do_transition(transition, dict_of_tokens):
                set_of_None_can_do_transitions.add(transition)
    return set_of_None_can_do_transitions


# Function that activate the transition
def activate_transition(transition: PetriNet.Transition, dictionary_of_tokens_copy):
    arcs_in = transition.in_arcs
    for arc in arcs_in:
        dictionary_of_tokens_copy[arc.source] = dictionary_of_tokens_copy[arc.source] - 1
    arcs_out = transition.out_arcs
    for arc in arcs_out:
        dictionary_of_tokens_copy[arc.target] = dictionary_of_tokens_copy[arc.target] + 1


def return_final_place(places):
    for place in places:
        if place.name == 'sink' or place.name == 'sink0':
            return place


# Function that return the label of the transition (activity name)
def return_label_transition(transitions, label):
    for transition in transitions.copy():
        if transition.label == label:
            return transition


# Function that return if a trace is in the net
def check_if_trace_in_net(net, trace, final_marking, dict_of_tokens):
    trace_in_net = False
    set_of_activate_None_transitions = group_of_can_do_transitions(net.transitions, dict_of_tokens)
    for None_activate_transition in set_of_activate_None_transitions:
        dictionary_of_tokens_copy = dict_of_tokens.copy()
        activate_transition(None_activate_transition, dictionary_of_tokens_copy)
        trace_in_net = trace_in_net or check_if_trace_in_net(net, trace, final_marking, dictionary_of_tokens_copy)
    if len(trace) == 0:
        trace_in_net = trace_in_net or dict_of_tokens[return_final_place(net.places)] == 1
    else:
        label_transition = return_label_transition(net.transitions, trace[0])
        if check_if_can_do_transition(label_transition, dict_of_tokens):
            dictionary_of_tokens_copy = dict_of_tokens.copy()
            activate_transition(label_transition, dictionary_of_tokens_copy)
            trace_in_net = trace_in_net or check_if_trace_in_net(net, trace[1:], final_marking,
                                                                 dictionary_of_tokens_copy)
    return trace_in_net


def compute_TN_FP(net, initial, final, test_log):
    TN = 0
    FP = 0
    dict_of_tokens = {}
    for place in net.places:
        if place.name != 'source' and place.name != 'source0':
            dict_of_tokens[place] = 0
        else:
            dict_of_tokens[place] = 1
    for trace in test_log:
        if check_if_trace_in_net(net, trace, final, dict_of_tokens):
            TN = TN + 1
        else:
            FP = FP + 1
    return TN, FP


def compute_TP_FN(net, initial, final, test_log):
    TP = 0
    FN = 0
    dict_of_tokens = {}
    for place in net.places:
        if place.name != 'source':
            dict_of_tokens[place] = 0
        else:
            dict_of_tokens[place] = 1
    for trace in test_log:
        if check_if_trace_in_net(net, trace, final, dict_of_tokens):
            FN = FN + 1
        else:
            TP = TP + 1
    return TP, FN


def generate_for_inductive(net, initial, final, test_log):
    print("Inductive Results: \n")
    TN, FP = compute_TN_FP(net, initial, final, test_log[:10000])
    TP, FN = compute_TP_FN(net, initial, final, test_log[10000:])
    print("TP = " + str(TP) + " TN = " + str(TN) + " FP = " + str(FP) + " FN = " + str(FN) + "\n")
    precision = (TP) / (TP + FP)
    recall = (TP) / (TP + FN)
    f1_measure = (2 * precision * recall) / (precision + recall)
    print("Precision = " + str(precision) + " Recall = " + str(recall) + " F1 measure = " + str(f1_measure) + "\n")


def generate_for_heuristic(net, initial, final, test_log):
    print("Heuristic Results: \n")
    TN, FP = compute_TN_FP(net, initial, final, test_log[:15000])
    TP, FN = compute_TP_FN(net, initial, final, test_log[15000:])
    print("TP = " + str(TP) + " TN = " + str(TN) + " FP = " + str(FP) + " FN = " + str(FN) + "\n")
    precision = (TP) / (TP + FP)
    recall = (TP) / (TP + FN)
    f1_measure = (2 * precision * recall) / (precision + recall)
    print("Precision = " + str(precision) + " Recall = " + str(recall) + " F1 measure = " + str(f1_measure) + "\n")


def get_test_log(log_path):
    file = open(log_path)
    csvreader = csv.reader(file)
    rows = []
    for row in csvreader:
        rows.append(row)
    return rows


def year_plus_one_hundred(year):
    int_year = int(year)
    int_year = int_year + 100
    return str(int_year)


def change_year_in_log(log_path):
    event_log = pandas.read_csv(log_path, sep=';')
    index = 0
    for date in event_log['timestamp']:
        date = year_plus_one_hundred(date[:4]) + date[4:]
        event_log.at[index, 'timestamp'] = date
        index = index + 1
    event_log.to_csv(log_path, index=False)


def count_c(trace):
    if occurs_in_trace(trace, 'c') < 3:
        return True
    return False


def less_six(trace):
    return len(trace) < 6


def last_activity_is_c(trace):
    return len(trace) == 0 or trace[len(trace) - 1] == 'c'


def occurs_in_trace(trace, activity):
    index = 0
    for action in trace:
        if action == activity:
            index = index + 1
    return index


def true_func(trace):
    return True


def print_traces_nice(traces, min_length, max_length):
    print("start printing")
    for i in range(max_length - min_length + 1):
        counter = 0
        for trace in traces:
            length = len(trace)
            if length == min_length + i:
                print(trace)
                counter = counter + 1
        if counter>0:
            print("number of traces in length of " + str(min_length + i) + " is: " + str(counter))
            print("===========================================================================")


def count_in_trace(activity, trace):
    counter = 0
    for action in trace:
        if action == activity:
            counter = counter + 1
    return counter

def convert_xes_to_csv(input_file_path, output_file_path):
    # Write to Pandas Dataframe
    log = pm4py.read_xes(input_file_path)  # Input Filename
    df = pm4py.convert_to_dataframe(log)
    df
    df.to_csv(output_file_path)


def build_names_of_transitions(transitions):
    transitions_names = []
    for transition in transitions:
        if transition.label!=None:
            transitions_names.append(transition.label)
    return transitions_names


def build_pre(place):
    pre = []
    for arc in place.in_arcs:
        pre.append(arc.source)
    return pre


def build_recursive_names_of_transitions_not_under_loop(process_tree_Inductive, names_of_transitions_under_loop):
    if len(process_tree_Inductive.children) == 0 :
        if process_tree_Inductive.label!=None:
            names_of_transitions_under_loop.append(process_tree_Inductive.label)
    else :
        if process_tree_Inductive.operator.value!="*":
            for children in process_tree_Inductive.children:
                child_names_of_transitions_under_loop = build_names_of_transitions_not_under_loop(children)
                for children_of_children in child_names_of_transitions_under_loop:
                    names_of_transitions_under_loop.append(children_of_children)
    return names_of_transitions_under_loop



def build_names_of_transitions_not_under_loop(process_tree_Inductive):
    return build_recursive_names_of_transitions_not_under_loop(process_tree_Inductive,[])

def transition_under_tree(process_tree, transition):
    if process_tree.label == transition:
        return -1
    if process_tree.children == []:
        return -2
    index_of_children = 0
    for children in process_tree.children:
        if transition_under_tree(children,transition)>=-1:
            return index_of_children
        index_of_children = index_of_children + 1
    return -2


def build_names_of_transitions_under_tree(process_tree):
    list_of_transitions = []
    if process_tree.children == []:
        if process_tree.label!=None:
            return [process_tree.label]
    for children in process_tree.children:
        list_of_transitions_for_children = build_names_of_transitions_under_tree(children)
        list_of_transitions.extend(list_of_transitions_for_children)
    return list_of_transitions



def build_transition_neighboors_under_loop(process_tree_Inductive, transition_not_under_loop):
    list_of_good_transitions = []
    if process_tree_Inductive.label != transition_not_under_loop:
        children_with_transition_index = transition_under_tree(process_tree_Inductive, transition_not_under_loop)
        children_with_transition = process_tree_Inductive.children[children_with_transition_index]
        if process_tree_Inductive.operator.value == "->":
            for index_of_child in range(children_with_transition_index):
                list_of_children_transition = build_names_of_transitions_under_tree(process_tree_Inductive.children[index_of_child])
                list_of_good_transitions.extend(list_of_children_transition)
        if  process_tree_Inductive.operator.value == "+":
            for index_of_child in range(len(process_tree_Inductive.children)):
                if index_of_child != children_with_transition_index:
                    list_of_children_transition = build_names_of_transitions_under_tree(process_tree_Inductive.children[index_of_child])
                    list_of_good_transitions.extend(list_of_children_transition)
        list_of_children_transition = build_transition_neighboors_under_loop(children_with_transition,transition_not_under_loop)
        list_of_good_transitions.extend(list_of_children_transition)
    return list_of_good_transitions


def build_dict_of_xor_and_not_under_loop(process_tree_Inductive, names_of_transitions_not_under_loop):
    dictionary_of_transitions = {}
    for transition_not_under_loop in names_of_transitions_not_under_loop:
        dictionary_of_transitions[transition_not_under_loop] = build_transition_neighboors_under_loop(process_tree_Inductive,transition_not_under_loop)
    return dictionary_of_transitions


#
# def find_transitions_for_xor(process_tree_Inductive):
#     if process_tree_Inductive.label!=None:
#         return [process_tree_Inductive.label]
#     if len(process_tree_Inductive.children) == 0:
#         return []
#     transitions_names = []
#     xor_node = (process_tree_Inductive.operator.value == "X")
#     xor_loop_node_left_is_empty_transition = (process_tree_Inductive.operator.value =="*" and process_tree_Inductive.children[0].name == "tau")
#     if xor_loop_node_left_is_empty_transition:
#         return []
#     if xor_node and has_empty_child(process_tree_Inductive):
#         return []
#     for children in process_tree_Inductive.children:
#         children_transition_names = find_transitions_for_xor(children)
#         transitions_names.extend(children_transition_names)
#     return transitions_names
#
#
#
def has_empty_child(process_tree_Inductive):
    for children in process_tree_Inductive.children:
        if len(children.children) == 0 and children.label == None:
            return True
    return False

# def build_names_of_transitions_under_xor_with_empty_trnasitions_recursive(process_tree_Inductive, dictionary_of_problematic_nodes):
#     if len(process_tree_Inductive.children)>0 and process_tree_Inductive.operator.value == "X":
#         transitions_that_at_least_of_them_happen = find_transitions_for_xor(process_tree_Inductive)
#         if len(transitions_that_at_least_of_them_happen)>0:
#             dictionary_of_problematic_nodes[process_tree_Inductive] = transitions_that_at_least_of_them_happen
#     for children in process_tree_Inductive.children:
#         build_names_of_transitions_under_xor_with_empty_trnasitions_recursive(children,dictionary_of_problematic_nodes)
#
# def build_names_of_transitions_under_xor_with_empty_trnasitions(process_tree_Inductive):
#     dictionary_of_problematic_nodes = {}
#     return build_names_of_transitions_under_xor_with_empty_trnasitions_recursive(process_tree_Inductive,dictionary_of_problematic_nodes)

def check_if_has_empty_transition_another_way_helper(process_tree):
    has_empty_transition_another_way = False
    if process_tree.label!=None:
        return False
    children_empty = len(process_tree.children) == 0 and process_tree.label == None
    if children_empty:
        return True
    xor_node = (process_tree.operator.value == "X")
    seq_node =  (process_tree.operator.value == "->")
    loop_node =  (process_tree.operator.value == "*")
    parallel_node =  (process_tree.operator.value == "+")
    if xor_node:
        for children in process_tree.children:
            has_empty_transition_another_way = has_empty_transition_another_way or check_if_has_empty_transition_another_way_helper(children)
    if seq_node or parallel_node:
        all_children = True
        for children in process_tree.children:
            all_children = all_children and check_if_has_empty_transition_another_way_helper(
                children)
        has_empty_transition_another_way = all_children
    if loop_node:
        has_empty_transition_another_way = check_if_has_empty_transition_another_way_helper(process_tree.children[0])
    return has_empty_transition_another_way

def check_if_has_empty_transition_another_way(process_tree):
    for children in process_tree.children:
        children_empty = len(children.children) == 0 and children.label == None
        if children_empty == False:
            has_by_another = check_if_has_empty_transition_another_way_helper(children)
            if has_by_another:
                return True
    return False

def delete_empty_transition(xor_node):
    for children in xor_node.children:
        if len(children.children) == 0 and children.label == None:
            xor_node.children.remove(children)


def remove_not_need_nodes(process_tree):
    if process_tree.children!=[]:
        xor_node = (process_tree.operator.value == "X")
        if xor_node and has_empty_child(process_tree):
            has_empty_tranisition_another_way = check_if_has_empty_transition_another_way(process_tree)
            if has_empty_tranisition_another_way:
                delete_empty_transition(process_tree)
                if len(process_tree.children) == 1:
                    if process_tree.parent == None:
                        process_tree = process_tree.children[0]
                    else:
                        index_of_child = process_tree.parent.children.index(process_tree)
                        process_tree.parent.children.remove(process_tree)
                        process_tree.parent.children.insert(index_of_child,process_tree.children[0])
                        process_tree.children[0].parent = process_tree.parent
        for children in process_tree.children:
            remove_not_need_nodes(children)


def copy_process_tree(process_tree_Inductive, parent):
    if len(process_tree_Inductive.children) == 0:
        copy_process_tree_ret = ProcessTree()
        copy_process_tree_ret.children = []
        copy_process_tree_ret.label = process_tree_Inductive.label
        copy_process_tree_ret.operator = process_tree_Inductive.operator
        copy_process_tree_ret.parent = parent
        return copy_process_tree_ret
    else:
        copy_process_tree_ret = ProcessTree()
        copy_process_tree_ret.label = None
        copy_process_tree_ret.operator = process_tree_Inductive.operator
        copy_process_tree_ret.parent = parent
        for child in process_tree_Inductive.children:
            copy_child = copy_process_tree(child,copy_process_tree_ret)
            copy_process_tree_ret.children.append(copy_child)
        return copy_process_tree_ret



if __name__ == "__main__":
    log = import_csv("C:/Users/עידו שפירא/Downloads/RequestForPayment.csv")
    #train_log = import_csv("C:/Users/עידו שפירא/Downloads/ski_train_log.csv")
    Decision_Tree_To_Guards.split_csv_to_train_test(log)
    train_log = import_csv("C:/Users/עידו שפירא/PycharmProjects/play/train_log.csv")
    test_log = import_csv("C:/Users/עידו שפירא/PycharmProjects/play/test_log.csv")
    #convert_xes_to_csv("C:/Users/עידו שפירא/Downloads/PrepaidTravelCost.xes","C:/Users/עידו שפירא/Downloads/PrepaidTravelCost.csv")
    #print_traces_nice(traces)
    process_tree_Inductive =  pm4py.discover_process_tree_inductive(train_log,0.0,True,"activity","timestamp","case ID")
    #pm4py.view_process_tree(process_tree_Inductive)
    pm4py.view_process_tree(process_tree_Inductive)
    net,im,fm = petri_net_by_inductive(train_log)
    evaluation(test_log, net, im, fm)
    remove_not_need_nodes(process_tree_Inductive)
    names_of_transitions = build_names_of_transitions(net.transitions)
    #names_of_transitions_not_under_loop = build_names_of_transitions_not_under_loop(process_tree_Inductive)
    #dictio = build_dict_of_xor_and_not_under_loop(process_tree_Inductive,names_of_transitions_not_under_loop)
    # print(names_of_transitions_not_under_loop)
    # print(dictio)
    #evaluation(train_log,net,im,fm)
    # pm4py.view_process_tree(process_tree_Inductive)
    process_tree_Inductive_before = copy_process_tree(process_tree_Inductive,None)
    Decision_Tree_To_Guards.delete_empty_transitions(process_tree_Inductive,  train_log, names_of_transitions)
    pm4py.view_process_tree(process_tree_Inductive)
    names_of_transitions = build_names_of_transitions(net.transitions)
    #names_of_transitions_under_xor_with_empty_trnasitions = build_names_of_transitions_under_xor_with_empty_trnasitions(process_tree_Inductive)
    #print(names_of_transitions_under_xor_with_empty_trnasitions)
    #tree = pm4py.convert_to_process_tree(net, im, fm)
    #pm4py.view_process_tree(tree)
    # Decision_Tree_To_Guards.create_ec_kitty_tree(net,train_log,names_of_transitions)
    print("Without Guards \n")
    Decision_Tree_To_Guards.add_xor_guards(process_tree_Inductive_before,net,train_log,names_of_transitions)
    print("\n==============================================================================================================================\nWith Guards\n")
    #Decision_Tree_To_Guards.add_xor_guards(tree,net,train_log)
    #print_petri_net(net,im,fm)

    evaluation(test_log,net,im,fm)
