import pm4py
from pm4py.objects.petri.petrinet import PetriNet
from pm4py.objects.petri import utils
from pm4py.objects.log.util import log as log_utils
from pm4py.objects.petri.petrinet import Marking
from pm4py.algo.conformance.alignments.versions import state_equation_a_star  as align
from collections import defaultdict
from collections import Counter

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
        subnets.append((subnet, initialMarking, finalMarking))
    return subnets



def GetAlignmentParameters(subnets):
    transitionCost = {}
    for net in subnets:
        for transition in net[0].transitions:
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
        for t in net[0].transitions:
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
    result = {net:[] for net in subnets}
    events = variant.split(',')
    for event in events:
        for net in result:
            for t in net[0].transitions:
                if t.label != None and t.label == event:
                    result[net].append(event)
    for net in result:            
        result[net] =  ",".join(result[net])
    return result
    

def PrefromAlignment(variants, subnets, parameters):
    result = {net:[] for net in subnets}
    
    for variant in variants:
        projectedVariant = ProjectVariant(variant, subnets)
        for net in subnets:
            if len(projectedVariant[net]) > 0:
                alignment = align.apply_from_variant(projectedVariant[net], net[0], net[1], net[2], parameters[net])
                if alignment == None:
                    alignment = align.apply_from_variant(projectedVariant[net], net[0], [], [], parameters[net])
                result[net].append(alignment)
            else:
                result[net].append(None)
    return result
        

def MergeModels(subnets):
    net = PetriNet("merged_net")
    initialMarking = Marking()
    finalMarking = Marking()
    mapping = dict()

    for n, im, fm in subnets:
        for p in n.places:
            newPlace = PetriNet.Place(p.name)
            mapping[p.name] = newPlace
            net.places.add(newPlace)

        for t in n.transitions:
            if t.label is not None and t.label not in [x.label for x in net.transitions]:
                newTransition = PetriNet.Transition(t.name, t.label)
                mapping[t.name] = newTransition
                net.transitions.add(newTransition)

        for place, count in im.items():
            initialMarking[mapping[place.name]] = count

        for place, count in fm.items():
            finalMarking[mapping[place.name]] = count

    for n, im, fm in subnets:   
        for a in n.arcs:
            try:
                utils.add_arc_from_to(mapping[a.source.name], mapping[a.target.name], net)
            except :
                continue
            

    return (net, initialMarking, finalMarking)

def GetTransition(v):
    if v[0] == v[1]:
        return v[0]
    elif v[0] == '>>' and v[1] != None:
        return v[1]
    elif v[1] == '>>':
        return v[0]
    return None
            

import os
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.objects.petri.exporter import pnml as pnml_exporter

import uuid
def BorderAgreement(alignments, index, trace):
    transInfo = {}
    borders = []
    subnets = []
    for net, alignment in alignments.items():
        if alignment[index] == None:
            continue
        subnets.append(net)
        alignment_list = alignment[index]['alignment']
        counter = Counter(alignment_list)
        for k, v in counter.items():
            transition = GetTransition(k)
            if (transition) == None:
                continue
            info = (net, k, v)
            if transition in transInfo:
                transInfo[transition].append(info)
            else:
                transInfo[transition] = [info]
                
        borders.append((net, alignment_list[0], counter[alignment_list[0]]))
        if len(alignment_list) > 1:
            borders.append((net, alignment_list[-1], counter[alignment_list[-1]]))
    
    merge_net = []
    for border in borders:
        transition = GetTransition(border[1])
        if transition == None:
            continue
        info = transInfo[transition]
        isConflict = False
        for i in info:
            if i[0] != border[0] and (border[1] != i[1] or border[2] != i[2]):
                isConflict = True
                break
        
        if not isConflict:
            continue
        conflicts = list(set([i[0] for i in info]))
        if len(conflicts) > len(merge_net):
            merge_net = conflicts
        
#    for k,v in alignments.items():   
#        if v [0] == None:
#            continue
#        path = "nets\\subnet-{}.".format(uuid.uuid4())
#        print(v[0]['alignment'], "->", path)
#        gviz = pn_vis_factory.apply(k[0], k[1], k[2], parameters={"format":"svg"})
#        pn_vis_factory.save(gviz, path+"svg")
#        pnml_exporter.export_net(k[0], k[1], path, final_marking=k[2])
    #print('===================================================')
    if len(merge_net) == 0:
        return alignments
    subnets = list(set(subnets) - set(merge_net))
    subnets.append(MergeModels(merge_net))
    alignments = PrefromAlignment([trace], subnets, GetAlignmentParameters(subnets))

    return BorderAgreement(alignments, index, trace)

