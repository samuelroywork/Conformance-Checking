from pm4py.objects.log.importer.xes import factory as xes_importer
log = xes_importer.apply("log_IEEE.xes_/log_IEEE.xes")

# 2) Export the partitioned dataset with the desidered number of columns:

from pm4py.objects.log.exporter.parquet import factory as parquet_exporter
parquet_exporter.apply(log, "bpi19", parameters={"auto_partitioning": True, "num_partitions": 128})