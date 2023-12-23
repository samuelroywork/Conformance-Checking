from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.visualization.petrinet import factory as vis_factory
from pm4py.algo.conformance.alignments import factory as alignments_factory
from pm4py.algo.conformance.tokenreplay import factory as token_based_replay
from pm4py.objects.log.importer.parquet import factory as parquet_importer
from pm4py.objects.petri.exporter.versions import pnml as pnml_exporter

#df = parquet_importer.apply("bpic2019")
#print(df)
list_files = parquet_importer.get_list_parquet("C:\\Users\\Mo\\OneDrive - rwth-aachen.de\\Uni\\2.Semester\\Praktikum\\Git Project\\Conformance-Checking-Lab\\master\\bpi19")
#print(list_files)
log = parquet_importer.import_log(list_files[0])
print(log)

net, im, fm = inductive_miner.apply(log)
print(net)




pnml_exporter.export_net(net, im, "petri_bpi19.pnml")