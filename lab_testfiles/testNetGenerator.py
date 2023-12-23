from pm4py.objects.petri.petrinet import PetriNet, Marking
net = PetriNet("new_petri_net")


places = [PetriNet.Place("dummy")]
transitions = [PetriNet.Transition("dummy")]

for i in range(1,20):
    place = PetriNet.Place("p"+str(i))
    # Add the places to the Net
    net.places.add(place)
    places.append(place)

# Create transitions
for i in range (1, 10):
    transition = PetriNet.Transition("t"+str(i), chr(96+i))
    # Add the transitions to the Petri Net
    print(transition.label, transition.name)
    net.transitions.add(transition)
    transitions.append(transition)

transition = PetriNet.Transition("t10", "")
net.transitions.add(transition)
transitions.append(transition)
for i in range(11, 19):
    transition = PetriNet.Transition("t"+str(i), chr(95+i))
    # Add the transitions to the Petri Net
    net.transitions.add(transition)
    transitions.append(transition)



# Add arcs
from pm4py.objects.petri import utils
print(transitions)
print(places)
#p1
utils.add_arc_from_to(places[1], transitions[1], net)
#t1
utils.add_arc_from_to(transitions[1], places[2], net)
utils.add_arc_from_to(transitions[1], places[3], net)
#p2
utils.add_arc_from_to(places[2], transitions[2], net)
utils.add_arc_from_to(places[2], transitions[3], net)
#p3
utils.add_arc_from_to(places[3], transitions[4], net)
#t2
utils.add_arc_from_to(transitions[2], places[4], net)
#t3
utils.add_arc_from_to(transitions[3], places[5], net)
#t4
utils.add_arc_from_to(transitions[4], places[6], net)
utils.add_arc_from_to(transitions[4], places[7], net)
#p4 - 18
utils.add_arc_from_to(places[4], transitions[5], net)
utils.add_arc_from_to(places[5], transitions[6], net)
utils.add_arc_from_to(places[6], transitions[7], net)
utils.add_arc_from_to(places[7], transitions[8], net)
utils.add_arc_from_to(places[8], transitions[9], net)
utils.add_arc_from_to(places[9], transitions[14], net)
utils.add_arc_from_to(places[10], transitions[11], net)
utils.add_arc_from_to(places[11], transitions[12], net)
utils.add_arc_from_to(places[12], transitions[13], net)
#utils.add_arc_from_to(places[13], transitions[14], net)
utils.add_arc_from_to(places[14], transitions[15], net)
utils.add_arc_from_to(places[15], transitions[15], net)
utils.add_arc_from_to(places[16], transitions[17], net)
utils.add_arc_from_to(places[17], transitions[17], net)
utils.add_arc_from_to(places[18], transitions[16], net)
utils.add_arc_from_to(places[18], transitions[18], net)

#t5 - t18
utils.add_arc_from_to(transitions[5], places[8], net)
utils.add_arc_from_to(transitions[6], places[9], net)
utils.add_arc_from_to(transitions[7], places[10], net)
utils.add_arc_from_to(transitions[8], places[11], net)
utils.add_arc_from_to(transitions[9], places[12], net)
#utils.add_arc_from_to(transitions[10], places[13], net)
utils.add_arc_from_to(transitions[11], places[14], net)
utils.add_arc_from_to(transitions[12], places[15], net)
utils.add_arc_from_to(transitions[13], places[16], net)
utils.add_arc_from_to(transitions[14], places[16], net)
utils.add_arc_from_to(transitions[15], places[17], net)
utils.add_arc_from_to(transitions[16], places[2], net)
utils.add_arc_from_to(transitions[16], places[3], net)
utils.add_arc_from_to(transitions[17], places[18], net)
utils.add_arc_from_to(transitions[18], places[19], net)









initial_marking = Marking()
initial_marking[places[1]] = 1
final_marking = Marking()
final_marking[places[-1]] = 1
from pm4py.objects.petri.exporter import pnml as pnml_exporter
pnml_exporter.export_net(net, initial_marking, "paperNet.pnml", final_marking=final_marking)

from pm4py.visualization.petrinet import factory as pn_vis_factory
gviz = pn_vis_factory.apply(net, initial_marking, final_marking, parameters= {"format":"svg"})
pn_vis_factory.view(gviz)

# from functions import DecomposeModel
# subnets = DecomposeModel(net, initial_marking, final_marking)


# for subnet in subnets:
#     gviz = pn_vis_factory.apply(subnet[0], initial_marking, final_marking, parameters= {"format":"svg"})
#     pn_vis_factory.view(gviz)