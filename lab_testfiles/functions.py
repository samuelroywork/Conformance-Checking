import os;
from pm4py.objects.petri.importer import versions

from pm4py.visualization.petrinet import factory as pn_vis_factory
import pm4py
from pm4py.objects.petri.petrinet import PetriNet
from pm4py.objects.petri import utils
from pm4py.objects.log.util import log as log_utils
from pm4py.objects.petri.petrinet import Marking
from pm4py.algo.conformance.alignments.versions import state_equation_a_star  as align
from pm4py.objects.log.log import EventLog, Trace
from pm4py.algo.filtering.log.variants import variants_filter

from pm4py.objects.log.importer.xes import factory as xes_importer

def DecomposeModel(net, initial_marking, final_marking):
    availablePlaces = net.places.copy();
    
    duplicateTransitions = {}
    for transition in net.transitions:
        if transition.label == None:
            continue
        if transition.label in duplicateTransitions:
            duplicateTransitions[transition.label].append(transition);
        else:
            duplicateTransitions[transition.label] = [transition];

    duplicateTransitions = { k:v for k, v in duplicateTransitions.items() if len(v) > 1 }
    subnets = []
    while len(availablePlaces) > 0:
        places = set()
        transitions = set()
        arcs = set()
        
        pendingPlaces = [availablePlaces.pop()]
        while len(pendingPlaces) > 0:
            place = pendingPlaces.pop();
            places.add(place)
            if place in availablePlaces:
                availablePlaces.remove(place)
            discoveredTransitions = set()
            
            for arc in place.out_arcs:
                arcs.add(arc)
                if arc.target not in transitions:
                    discoveredTransitions.add(arc.target)
                
            for arc in place.in_arcs:
                arcs.add(arc) 
                if arc.source not in transitions:
                    discoveredTransitions.add(arc.source)
            
            while len(discoveredTransitions) > 0:
                transition = discoveredTransitions.pop()
                transitions.add(transition)
                
                if transition.label == None:
                    for arc in transition.out_arcs:
                        if arc.target not in places:
                            pendingPlaces.append(arc.target)
                    for arc in transition.in_arcs:
                        if arc.source not in places:
                            pendingPlaces.append(arc.source)
                elif transition.label in duplicateTransitions:
                    discoveredTransitions.extend(duplicateTransitions[transition.label])
                    
                    
        subnet = PetriNet("subnet_{}".format(len(subnets) + 1))
        places = { p: PetriNet.Place(p.name) for p in places};
        for k, v in places.items():
            subnet.places.add(v)
        transitions = { t: PetriNet.Transition(t.name, t.label) for t in transitions};
        for k, v in transitions.items():
            subnet.transitions.add(v)

        for arc in arcs:
            utils.add_arc_from_to(places[arc.source] if arc.source in places else transitions[arc.source],
                                  places[arc.target] if arc.target in places else transitions[arc.target], subnet)

        initialMarking = Marking()
        for place, count in initial_marking.items():
            if place in places:
                initialMarking[places[place]] = count

        finalMarking = Marking()
        for place, count in final_marking.items():
            if place in places:
                finalMarking[places[place]] = count
        subnets.append([subnet, initialMarking, finalMarking])
    return subnets


from collections import defaultdict

def GetAlignmentParameters(subnets):
    transitionCost = {}
    subnets = [e[0] for e in subnets]
    for net in subnets:
        for transition in net.transitions:
            if transition.label == None:
                continue
            if transition.label in transitionCost:
                transitionCost[transition.label] += 1
            else:
                transitionCost[transition.label] = 1
    
    for t in transitionCost:
        transitionCost[t] = 1 / transitionCost[t]
    
    def cost_handler(trace, costs, trace_name_key=log_utils.xes_util.DEFAULT_NAME_KEY, activity_key=log_utils.xes_util.DEFAULT_NAME_KEY):
        costs = [transitionCost[e[activity_key]] for e in trace]
        return align.construct_trace_net_cost_aware(trace, costs, trace_name_key=trace_name_key, activity_key=activity_key)
        
    parameters = {}
    for net in subnets:
        net_parameters = dict()
        cost_function = dict()
        for t in net.transitions:
            if t.label == None:
                cost_function[t] = 0
            elif t.label in transitionCost:
                cost_function[t] = transitionCost[t.label]
        
        net_parameters[pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_MODEL_COST_FUNCTION] = cost_function
        net_parameters[pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_SYNC_COST_FUNCTION] = defaultdict(lambda: 0)
        net_parameters[pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_TRACE_COST_FUNCTION] = []
        net_parameters[pm4py.algo.conformance.alignments.versions.state_equation_a_star.TRACE_NET_COST_AWARE_CONSTR_FUNCTION] = cost_handler
        net_parameters[pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_TRACE_NET_COSTS] = cost_function
        
        parameters[net]= net_parameters
    return parameters



def ProjectVariant(variant, subnets):
    result = {net:[] for net, i, f in subnets}
    events = variant.split(',')
    for event in events:
        for net in result:
            for t in net.transitions:
                if t.label != None and t.label == event:
                    result[net].append(event)
    for net in result:            
        result[net] =  ",".join(result[net])
    return result
    

def PrefromAlignment(variants, subnets, parameters):
    result = {net:[] for net, i, f in subnets}
    
    for variant in variants:
        projectedVariant = ProjectVariant(variant, subnets)
        for net, initial_marking, final_marking in subnets:
            if len(projectedVariant[net]) > 0:
                result[net].append(align.apply_from_variant(projectedVariant[net], net, initial_marking, final_marking, parameters[net]))
            else:
                result[net].append(None)
    return result
        


# net, initial_marking, final_marking = versions.pnml.import_net(("../../lab_testfiles/petrinet.pnml"))
# subnets = DecomposeModel(net, initial_marking, final_marking)
# parameters = GetAlignmentParameters(subnets)
# log = xes_importer.import_log("../../lab_testfiles/running-example.xes")
# variants = list(variants_filter.get_variants_from_log_trace_idx(log).keys())
# variants = ['sdds,dsdsde,frew']
# alignments = PrefromAlignment(variants, subnets, parameters)


# cost = 0
# for k,v in alignments.items():
#     cost += v[0]['cost']
#     if (v[0]['cost'] != 0):
#         print(str(v[0]['alignment'])+  " , cost = "+str( v[0]['cost']))
    
# print("Total cost for the first trace: {}".format(cost))

# # for visualization
# os.environ["PATH"] += os.pathsep + "C:\\Program Files (x86)\\Graphviz2.38\\bin"
# gviz = pn_vis_factory.apply(net, initial_marking, final_marking, parameters={"format":"svg"})
# pn_vis_factory.save(gviz, "nets\\main.svg")
# for i in range(len(subnets)): 
#     net, initial_marking, final_marking = subnets[i]
#     gviz = pn_vis_factory.apply(net, initial_marking, final_marking, parameters={"format":"svg"})
#     pn_vis_factory.save(gviz, "nets\\subnet-{}.svg".format(i+1))




