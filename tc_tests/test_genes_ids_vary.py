#!/usr/bin/python

import os
from common import run_quast, contigs_2_1k, reference_1k, assert_metric

name = os.path.basename(__file__)[5:-3]


run_quast(name, contigs=[contigs_2_1k], params='-R ' + reference_1k + ' -G genes_1k_ids_differ.txt')
assert_metric(name, '# genes', ['0 + 1 part'])

