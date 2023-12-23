import pm4pycvxopt
import requests
import json
from pm4py.objects.petri.importer.versions import pnml as pnml_importer
from pm4py.objects.petri.exporter.versions import pnml as pnml_exporter
import sys
from pm4py.objects.petri import utils
import time

print("Assigning Log")
r = requests.get("http://localhost:5001/doLogAssignment?keyphrase=hello")

# load petri net from file
print("Loading Net")
# net, im, fm = pnml_importer.import_net("paperNet.pnml")
#net, im, fm = pnml_importer.import_net("petri_bpi19.pnml")
net, im, fm = pnml_importer.import_net("petrinet_karl.pnml")

petri_str = pnml_exporter.export_petri_as_string(net, im, final_marking=fm)

# Use this block of code to get the var list for the bpi19 log!
r = requests.get("http://localhost:5001/getVariants?keyphrase=hello&process=bpi19")
variants = r.json()
var_list = [[x["variant"], x["count"]] for x in variants["variants"]]
print(len(var_list))

# Log from the recomposing paper. Used for testing purposes:
# costs should be 0, 2, 1 times the cost function
var_list_paper = []
var_list_paper.append(["a,b,e,i,l,d,g,j,h,k,n,p,q", 1])
var_list_paper.append(["a,c,f,m,d,g,j,k,h,n,p,q", 1])
var_list_paper.append(["a,e,i,l,d,g,j,h,k,n,p,q", 1])

# data that is sent with the post request. we use a dict in order to be able to acces the variables with the keys on the master

params = {'petri_string' : petri_str, 'var_list': var_list}

print("Alignment algorithm starting now.")
timea = time.perf_counter()
r = requests.post("http://localhost:5001/calculateDecompAlignments?keyphrase=hello", json=json.dumps(params))
time_decomp = time.perf_counter() - timea
with open('Implemented-result.json', 'w+') as f:
    json.dump(r.json(), f, indent=1)
print(r.json())
print(f"Time needed for the decomposed method: {time_decomp:.5f}")


#This is the classical algorithm in a distributed manner. Uncomment to compare
130447
params["max_align_time"] = sys.maxsize
params['max_align_time_trace'] =  sys.maxsize
timea = time.perf_counter()
r = requests.post("http://localhost:5001/performAlignments?keyphrase=hello", json=json.dumps(params))
with open('Classical.json', 'w+') as f:
    json.dump(r.json(), f, indent=1)
print(r.json())
time_classical = time.perf_counter() - timea
print(f"Time needed for the classical method: {time_classical:.5f}")

print(f"Time needed for the decomposed method: {time_decomp:.5f}")

time_diff = time_classical-time_decomp
print(f"Time gain: {time_diff:.5f}")

