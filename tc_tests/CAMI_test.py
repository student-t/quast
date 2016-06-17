#!/usr/bin/python

from __future__ import with_statement
import os
from common import *

name = os.path.basename(__file__)[:-3]

run_quast(name, contigs=['/acestorage/data/contigs/PAPERS/MetaQUAST/CAMI/CAMI/Gold_Assembly.fasta',
                         '/acestorage/data/contigs/PAPERS/MetaQUAST/CAMI/CAMI/SPAdes.fasta'],
                         params=' -t 4 --no-plots ', meta=True)

check_report_files(name, ['icarus.html',
                          'icarus_viewers/contig_size_viewer.html',
                          'icarus_viewers/alpha_proteobacterium_LLX12A.html',
                          'krona_charts/summary_taxonomy_chart.html',
                          'report.html',
                          'runs_per_reference/Brevibacterium_casei_S18/report.tsv'])

assert_metric(name, 'N50', ['24752', '16577'], 'combined_reference/report.tsv')
assert_metric_comparison(name, 'Reference length', '>=', value='70000000', fname='combined_reference/report.tsv')
assert_metric_comparison(name, 'gamma_proteobacterium_SCGC_AAA076-D02', '>=', value='1.05', fname='summary/TSV/Duplication_ratio.tsv')
assert_metric_comparison(name, 'gamma_proteobacterium_SCGC_AAA076-D02', '<=', value='1.2', fname='summary/TSV/Duplication_ratio.tsv')