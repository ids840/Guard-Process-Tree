import csv
import pm4py
import pandas
from datetime import datetime
from pm4py import ProcessTree
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator
import random
import datetime

from pm4py.objects.petri_net.utils import petri_utils

import Decision_Tree_To_Guards
import LogSplit


def import_csv(file_path, seperator):
    event_log = pandas.read_csv(file_path, sep=seperator)
    event_log['case ID'] = event_log['case ID'].astype(str)
    event_log['activity'] = event_log['activity'].astype(str)
    event_log['timestamp'] = pandas.to_datetime(event_log['timestamp'],format='mixed')
    return event_log



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

def evaluation(log, net, initial_marking, final_marking):
    replayed_traces = pm4py.conformance_diagnostics_token_based_replay(log, net, initial_marking, final_marking, "activity", "timestamp",
                                              "case ID")
    for trace in replayed_traces:
         if trace['missing_tokens'] > 0:
             print(trace['transitions_with_problems'])
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


def not_under_loop(process_tree_Inductive):
    if process_tree_Inductive.parent==None:
        return True
    if process_tree_Inductive.operator.value == "*":
        return False
    return not_under_loop(process_tree_Inductive.parent)


def build_nodes_for_transition(process_tree_Inductive,list_of_xor_and_seq_not_under_loop):
    if process_tree_Inductive.parent !=None:
        if process_tree_Inductive.parent.operator.value == "->" or process_tree_Inductive.parent.operator.value == "X":
            if not_under_loop(process_tree_Inductive.parent):
                index = process_tree_Inductive.parent.children.index(process_tree_Inductive)
                list_of_xor_and_seq_not_under_loop.append((process_tree_Inductive.parent,index))
        build_nodes_for_transition(process_tree_Inductive.parent, list_of_xor_and_seq_not_under_loop)


def add_for_list_of_not_depend(list_of_not_depend, list_of_xor_and_seq_not_under_loop):
    for node in list_of_xor_and_seq_not_under_loop:
        type = node[0]
        child_index = node[1]
        if type.operator.value == "X":
            for index in range(len(type.children)):
                if child_index!=index:
                    transitions = build_names_of_transitions_under_tree(type.children[index])
                    for transition in transitions:
                        list_of_not_depend.append(transition)
        else:
            for index in range(child_index+1, len(type.children)):
                transitions = build_names_of_transitions_under_tree(type.children[index])
                for transition in transitions:
                    list_of_not_depend.append(transition)


def build_not_depend_for_transition(transition_node):
    list_of_xor_and_seq_not_under_loop=[]
    build_nodes_for_transition(transition_node,list_of_xor_and_seq_not_under_loop)
    list_of_not_depend=[]
    add_for_list_of_not_depend(list_of_not_depend,list_of_xor_and_seq_not_under_loop)
    return list_of_not_depend

def build_dictionary_for_transitions(process_tree, dictionary):
    if len(process_tree.children) == 0:
        if process_tree.label != None:
            list_not_depend = build_not_depend_for_transition(process_tree)
            dictionary[process_tree.label] = list_not_depend
    else:
        for children in process_tree.children:
            build_dictionary_for_transitions(children,dictionary)

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

def build_traces():
    traces = []
    for _ in range(500):
        trace = []
        for i in range(3):
            if i<2:
                random_sign = random.randint(0,1)
                if random_sign==0:
                    trace.append("a")
                else:
                    trace.append("b")
            else:
                if count_in_trace("b",trace) == 2:
                    trace.append("b")
                else:
                    trace.append("a")
        traces.append(trace)
    return traces

def build_process_tree_gera_initial_example():
    process_tree = ProcessTree()
    process_tree.operator= "->"
    for i in range(3):
        xor = ProcessTree()
        child_a = ProcessTree()
        child_a.label = "a"
        child_a.parent = xor
        child_b = ProcessTree()
        child_b.label = "b"
        child_b.parent = xor
        xor.operator = "X"
        xor.parent = process_tree
        xor.children.append(child_a)
        xor.children.append(child_b)
        process_tree.children.append(xor)
    return process_tree

def build_events(trace, case_id):
    case_id_str = f"Case_{case_id}"
    trace_log = []
    for activity in trace:
        event = {
            "case_id": case_id_str,
            "activity": activity,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        trace_log.append(event)
    return trace_log

def build_log():
    log = []
    traces = build_traces()
    for i in range(len(traces)):
        trace_log = build_events(traces[i],i+1)
        log.extend(trace_log)
    return log


def create_train_log(log):
    timestamp = ''
    last_case_id = 0
    list_of_events_for_log = []
    for event in log:
        case_id = event.get("case_id")[5:]
        activity = event.get("activity")
        if int(case_id) != last_case_id:
            timestamp = '1700-12-01'
            last_case_id = int(case_id)
        else:
            timestamp = Decision_Tree_To_Guards.add_one_year(timestamp)
        event_for_log = []
        event_for_log.append(case_id)
        event_for_log.append(activity)
        event_for_log.append(timestamp)
        list_of_events_for_log.append(event_for_log)


def create_csv_file(headlines, data, csv_name):
    with open(csv_name, 'w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(headlines)

        for row in data:
            writer.writerow(row)


def generate_bnf_file(number_of_transitions):
    with open("C:/Users/עידו שפירא/PycharmProjects/play/PonyGE2/grammars/supervised_learning/decision_tree.bnf", 'w') as bnf_file:
        bnf_file.write('<b> ::= np.less(<e>,<e>)|\n')
        bnf_file.write('        np.greater(<e>,<e>)|\n')
        bnf_file.write('        np.logical_and(<b>,<b>)|\n')
        bnf_file.write('        np.logical_or(<b>,<b>)|\n')
        # bnf_file.write('        np.where(<b>,<e>,<e>)|\n')
        bnf_file.write('        np.equal(<e>,<e>)\n\n')

        bnf_file.write('<e> ::= x[:, 0]|\n')
        for i in range(1, number_of_transitions):
            bnf_file.write(f'        x[:, {i}]|\n')

        bnf_file.write('        np.subtract(<e>,<e>)|\n')
        bnf_file.write('        np.add(<e>,<e>)|\n')
        bnf_file.write('        <c>\n\n')

        bnf_file.write('<c> ::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9\n')


def define_empty_transitions(transitions):
    for transition in transitions:
        if transition.label != None and transition.label.startswith("empty transition"):
            transition.label = None


def add_back_transitions(net):
    tranitions = net.transitions
    for tranition in tranitions:
        in_arcs = tranition.in_arcs
        for in_arc in in_arcs:
            source = in_arc.source
            source_name = source.name
            if source_name.startswith("less") or source_name.startswith("greater"):
                petri_utils.add_arc_from_to(tranition, source, net)


if __name__ == "__main__":

    log = import_csv("C:/Users/עידו שפירא/Downloads/p2p_event_log.csv", ",")
    #train_log = import_csv("C:/Users/עידו שפירא/Downloads/ski_train_log.csv")
    LogSplit.split_csv_to_train_test(log)
    train_log = import_csv("C:/Users/עידו שפירא/PycharmProjects/play/train_log.csv", ",")
    test_log = import_csv("C:/Users/עידו שפירא/PycharmProjects/play/test_log.csv", ",")
    # convert_xes_to_csv("C:/Users/עידו שפירא/Downloads/PrepaidTravelCost.xes","C:/Users/עידו שפירא/Downloads/PrepaidTravelCost.csv")
    process_tree_Inductive =  pm4py.discover_process_tree_inductive(train_log,0.0,True,"activity","timestamp","case ID")
    dictionary_for_transitions = {}
    build_dictionary_for_transitions(process_tree_Inductive,dictionary_for_transitions)
    #pm4py.view_process_tree(process_tree_Inductive)
    net,im,fm = petri_net_by_inductive(train_log)
    print("Without Guards \n")
    evaluation(test_log, net, im, fm)
    remove_not_need_nodes(process_tree_Inductive)
    names_of_transitions = build_names_of_transitions(net.transitions)
    print("\n==============================================================================================================================\nWith Guards\n")
    Decision_Tree_To_Guards.add_xor_guards_ponyG(process_tree_Inductive,net,train_log,names_of_transitions,im,fm, dictionary_for_transitions)
    #print_petri_net(net,im,fm)
    define_empty_transitions(net.transitions)
    add_back_transitions(net)
    evaluation(test_log,net,im,fm)
