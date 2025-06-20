import csv
import pm4py
import pandas
from pm4py import PetriNet
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator
from pm4py.objects.petri_net.utils import petri_utils
import ApplyPonyGuard
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
def petri_net_by_ilp(log):
    net, initial_marking, final_marking = pm4py.discovery.discover_petri_net_ilp(log,1.0, "activity",
                                                                                        "timestamp", "case ID")
    return net, initial_marking, final_marking
def print_petri_net(net, initial_marking, final_marking):
    pm4py.write_pnml(net, initial_marking, final_marking, "createdPetriNet1.pnml")
    pm4py.view_petri_net(net, initial_marking, final_marking)
def evaluation(log, net, initial_marking, final_marking):
    fitness = pm4py.fitness_token_based_replay(log, net, initial_marking, final_marking, "activity", "timestamp",
                                            "case ID")
    prec = pm4py.precision_token_based_replay(log, net, initial_marking, final_marking, "activity", "timestamp",
                                              "case ID")
    simp = simplicity_evaluator.apply(net)
    print(fitness)
    print("prec: " + str(prec))
    print("simp: " + str(simp))
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
    if process_tree.label!=None:
        list_of_transitions.append(process_tree.label)
    if process_tree.children == []:
        return list_of_transitions
    for children in process_tree.children:
        list_of_transitions_for_children = build_names_of_transitions_under_tree(children)
        list_of_transitions.extend(list_of_transitions_for_children)
    return list_of_transitions

def build_names_of_transitions_under_tree_without_special(process_tree):
    list_of_transitions = []
    if process_tree.label!=None and process_tree.children == []:
        list_of_transitions.append(process_tree.label)
    if process_tree.children == []:
        return list_of_transitions
    for children in process_tree.children:
        list_of_transitions_for_children = build_names_of_transitions_under_tree_without_special(children)
        list_of_transitions.extend(list_of_transitions_for_children)
    return list_of_transitions

def not_under_loop(process_tree_Inductive):
    if process_tree_Inductive.parent==None:
        return True
    if process_tree_Inductive.children==[]:
        return not_under_loop(process_tree_Inductive.parent)
    if process_tree_Inductive.operator.value == "*":
        return False
    return not_under_loop(process_tree_Inductive.parent)


def build_nodes_for_transition(process_tree_Inductive,list_of_xor_and_seq_not_under_loop):
    if process_tree_Inductive.parent !=None:
        if process_tree_Inductive.parent.operator.value == "->" or process_tree_Inductive.parent.operator.value == "X" or process_tree_Inductive.parent.operator.value == "+":
            if not_under_loop(process_tree_Inductive.parent):
                index = process_tree_Inductive.parent.children.index(process_tree_Inductive)
                list_of_xor_and_seq_not_under_loop.append((process_tree_Inductive.parent,index))
        build_nodes_for_transition(process_tree_Inductive.parent, list_of_xor_and_seq_not_under_loop)


def add_for_list_of_not_depend(process_tree,list_of_not_depend, list_of_xor_and_seq_not_under_loop):
    for node in list_of_xor_and_seq_not_under_loop:
        type = node[0]
        child_index = node[1]
        if type.operator.value == "X" or type.operator.value == "+" and not_under_loop(process_tree):
            for index in range(len(type.children)):
                # if child_index!=index:
                transitions = build_names_of_transitions_under_tree_without_special(type.children[index])
                for transition in transitions:
                    if not list_of_not_depend.__contains__(transition):
                        list_of_not_depend.append(transition)
        else:
            plus_one = (not not_under_loop(process_tree))
            for index in range(child_index+plus_one, len(type.children)):
                transitions = build_names_of_transitions_under_tree_without_special(type.children[index])
                for transition in transitions:
                    if not list_of_not_depend.__contains__(transition):
                        list_of_not_depend.append(transition)


def build_not_depend_for_transition(transition_node):
    list_of_xor_and_seq_not_under_loop=[]
    transition_node_copy = transition_node
    build_nodes_for_transition(transition_node,list_of_xor_and_seq_not_under_loop)
    list_of_not_depend=[]
    add_for_list_of_not_depend(transition_node_copy,list_of_not_depend,list_of_xor_and_seq_not_under_loop)
    return list_of_not_depend


def build_not_depend_for_node(process_tree):
    list_of_xor_and_seq_not_under_loop = []
    process_tree_copy = process_tree
    build_nodes_for_transition(process_tree, list_of_xor_and_seq_not_under_loop)
    list_of_not_depend = []
    if not_under_loop(process_tree):
        list_of_not_depend.extend(build_names_of_transitions_under_tree_without_special(process_tree))
    add_for_list_of_not_depend(process_tree_copy,list_of_not_depend, list_of_xor_and_seq_not_under_loop)
    return list_of_not_depend


def build_not_depend_not_under_loop(process_tree):
    list_of_not_depend = []
    process_tree_copy = process_tree
    index_of_child = -1
    while process_tree_copy.parent!=None:
        index_of_child = process_tree_copy.parent.children.index(process_tree_copy)
        process_tree_copy = process_tree_copy.parent
    if process_tree_copy.operator.value == "->":
        for children in process_tree_copy.children[index_of_child:]:
            list_of_transitions_under_children = build_names_of_transitions_under_tree_without_special(children)
            list_of_not_depend.extend(list_of_transitions_under_children)
    else:
        for children in process_tree_copy.children:
            list_of_transitions_under_children = build_names_of_transitions_under_tree_without_special(children)
            list_of_not_depend.extend(list_of_transitions_under_children)
    return list_of_not_depend


def build_not_depend_under_loop(process_tree):
    list_not_depend = []
    process_tree_copy = process_tree
    while process_tree_copy.parent!=None:
        index_of_child = process_tree_copy.parent.children.index(process_tree_copy)
        process_tree_copy = process_tree_copy.parent
        if process_tree_copy.operator.value == "->" and not_under_loop(process_tree_copy):
            for children in process_tree_copy.children[index_of_child+1:]:
                list_of_transitions_under_children = build_names_of_transitions_under_tree_without_special(children)
                list_not_depend.extend(list_of_transitions_under_children)
        if process_tree_copy.operator.value == "X" and not_under_loop(process_tree_copy):
            for index in range(len(process_tree_copy.children)):
                if index != index_of_child:
                    children = process_tree_copy.children[index]
                    list_of_transitions_under_children = build_names_of_transitions_under_tree_without_special(children)
                    list_not_depend.extend(list_of_transitions_under_children)
    return list_not_depend
def build_not_depend_helper(process_tree, under_loop):
    if not under_loop:
        list_of_not_depend = build_not_depend_not_under_loop(process_tree)
    else:
        list_of_not_depend = build_not_depend_under_loop(process_tree)
    return list_of_not_depend

def build_not_depend(process_tree):
    parent_copy = process_tree.parent
    under_loop = not not_under_loop(parent_copy)
    list_of_not_depend = build_not_depend_helper(process_tree, under_loop)
    return list_of_not_depend


def build_dictionary_for_transitions(process_tree, dictionary, with_nodes):
    if with_nodes:
        if process_tree.label != None:
            if process_tree.parent != None:
                list_not_depend = build_not_depend(process_tree)
            else:
                list_not_depend = build_names_of_transitions_under_tree_without_special(process_tree)
            dictionary[process_tree.label] = list_not_depend
            if len(process_tree.children) != 0:
                for children in process_tree.children:
                    build_dictionary_for_transitions(children, dictionary, with_nodes)
    else:
        if len(process_tree.children) == 0:
            if process_tree.label != None:
                list_not_depend = build_not_depend_for_transition(process_tree)
                dictionary[process_tree.label] = list_not_depend
        else:
            for children in process_tree.children:
                build_dictionary_for_transitions(children, dictionary,with_nodes)

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
def has_empty_child(process_tree_Inductive):
    for children in process_tree_Inductive.children:
        if len(children.children) == 0 and children.label == None:
            return True
    return False

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


def swap_start_transitions(source, place_of_initialized):
    arcs_from_source = source.out_arcs
    for arc in arcs_from_source.copy():
        net.arcs.remove(arc)
        arc.target.in_arcs.remove(arc)
        source.out_arcs.remove(arc)
        petri_utils.add_arc_from_to(place_of_initialized, arc.target, net)


def add_initialize_to_net(net):
    source = ApplyPonyGuard.found_place(net,"source")
    initial_transition_name = "initial transition"
    initial_transition = PetriNet.Transition(initial_transition_name, None)
    net.transitions.add(initial_transition)
    place_of_initialized = PetriNet.Place("initial place")
    net.places.add(place_of_initialized)
    swap_start_transitions(source, place_of_initialized)
    petri_utils.add_arc_from_to(source, initial_transition, net)
    petri_utils.add_arc_from_to(initial_transition,place_of_initialized, net)


def change_source_sink_name(net):
    for place in net.places:
        if place.name.startswith("source") or place.name.startswith("start"):
            place.name="source"
        if place.name.startswith("sink") or place.name.startswith("end"):
            place.name="sink"

def petri_net_by_miner(train_log, miner):
    if miner == "1":
        net, im, fm = petri_net_by_inductive(train_log)
    elif miner == "2":
        net, im, fm = petri_net_by_heuristics(train_log)
    elif miner == "3":
        net, im, fm = petri_net_by_alpha(train_log)
    elif miner == "4":
        net, im, fm = petri_net_by_ilp(train_log)
    else:
        raise ValueError(f"Unknown miner: {miner}. Choose from 'inductive', 'heuristic', 'alpha' or 'ilp'.")
    return net, im, fm

if __name__ == "__main__":
    log = import_csv("C:/Users/עידו שפירא/Downloads/bank_log.csv", ",")
    LogSplit.split_csv_to_train_test(log)
    train_log = import_csv("C:/Users/עידו שפירא/PycharmProjects/play/train_log.csv", ",")
    test_log = import_csv("C:/Users/עידו שפירא/PycharmProjects/play/test_log.csv", ",")
    print("Choose a process mining algorithm:")
    print("1 - Inductive Miner")
    print("2 - Heuristic Miner")
    print("3 - Alpha Miner")
    print("4 - ILP Miner")
    choice = input("Enter the number of your choice: ").strip()
    net, im, fm = petri_net_by_miner(train_log, choice)
    change_source_sink_name(net)
    process_tree_Inductive = pm4py.discover_process_tree_inductive(train_log, 0.0, True, "activity", "timestamp",
                                                                   "case ID")
    dictionary_for_transitions = {}
    build_dictionary_for_transitions(process_tree_Inductive, dictionary_for_transitions, 0)
    pm4py.view_process_tree(process_tree_Inductive)
    print("Without Guards \n")
    evaluation(test_log, net, im, fm)
    remove_not_need_nodes(process_tree_Inductive)
    names_of_transitions = build_names_of_transitions(net.transitions)
    add_initialize_to_net(net)
    print(
        "\n==============================================================================================================================\nWith Guards\n")
    Decision_Tree_To_Guards.add_guards_ponyG(process_tree_Inductive, net, train_log, names_of_transitions,
                                                 dictionary_for_transitions)
    # print_petri_net(net,im,fm)
    define_empty_transitions(net.transitions)
    add_back_transitions(net)
    evaluation(test_log, net, im, fm)
