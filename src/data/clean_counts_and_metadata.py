#!/usr/bin/env python
"""
This file cleans up the raw counts and metadata tables and
writes datasetID.counts_table.clean datasetID.metadata.clean.
"""

import argparse
import yaml
import os
import sys
import subprocess
import pandas as pd
import feather
from pyarrow.compat import pdapi


src_dir = os.path.normpath(os.path.join(os.getcwd(), 'src/util'))
sys.path.append(src_dir)
from FileIO import read_yaml


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('raw_data_dir', help='directory with raw results folders')
    p.add_argument('yaml_file', help='yaml file. Should have datasetID as the main key. Can include "condition" to indicate subset of samples to keep.')
    p.add_argument('counts_out', help='clean count table output file')

    # Optional args below. Makefile just uses defaults
    p.add_argument('--n-reads-sample', help='minimum reads per sample (default: %(default)s)', default=100)
    p.add_argument('--n-reads-counts', help='minimum reads per count (default: %(default)s)', default=10)
    p.add_argument('--perc-samples', help='minimum percent of samples an counts is found in (default: %(default)s)', default=0.01)

    return p.parse_args()


def read_raw_files(countsfile, metafile):
    df = pd.read_csv(countsfile, sep='\t', index_col=0)
    meta = pd.read_csv(metafile, sep='\t', index_col=0)
    # If either index wasn't read as a string, explicitly do so
    if meta.index.dtype != 'O':
        meta.index = pd.read_csv(y[dataset_id]['metadata_file'], sep='\t', dtype=str).iloc[:, 0]

    if df.index.dtype != 'O':
        df.index = pd.read_csv(clean_otu_file, sep='\t', dtype=str).iloc[:,0]

    return df.T, meta


if __name__ == "__main__":
    args = parse_args()

    dataset_id = args.counts_out.split('/')[-1].split('.')[0]
    y = read_yaml(args.yaml_file, args.raw_data_dir)

    df, meta = read_raw_files(y[dataset_id]['counts_table'],
                              y[dataset_id]['metadata_file'])

    # Add some study-wise metadata, like sequencer and region
    meta = add_info_to_meta(meta, y[dataset_id], dataset_id)
    df, meta = clean_up_samples(df, meta, y[dataset_id])
    df, meta = clean_up_tables(df, meta, args.n_reads_counts, args.n_reads_sample, args.perc_samples)
    