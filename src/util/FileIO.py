#!/usr/bin/env python
"""
Functions to interface with the reads and metadata files.
"""

import os, sys
import yaml
import pandas as pd
import feather
from util import raw2abun

# Add this repo to the path
src_dir = os.path.normpath(os.path.join(os.getcwd(), 'src/util'))
sys.path.insert(0, src_dir)


def read_yaml(yamlfile, batch_data_dir):
    """
    Reads in a yaml file with   {dataset_id: {
                                             folder: <folder name>
                                             region: <16S Region>
                                             sequencer: <DNA sequencer>
                                             condition: <condition_dict>},
                                             disease_label: <label>,
                                             table_type: <'classic' or 'normal'>,
                                 dataset2: {...}, ...}

    Returns a dict with {dataset_id: {
                                otu_table: <path to otu table file>,
                                meta_file: <path to metadata file>,
                                summary_file: <path to summary_file.txt>,
                                sequencer: <DNA sequencer>,
                                region: <16S region>,
                                disease_label: 'label',
                                table_type: <'classic' or 'normal'>,
                                condition: <condition_dict, if given>, ...}
    yaml file can have 'otu_table' and 'metadata_file' keys indicating full paths
        to the respective files.

        Otherwise, it can have a 'folder' key which indicates the results_folder
        name in batch_data_dir.
        If a 'folder' is given, otu_table and metadata files are assumed to be
                              folder/RDP/<folder minus '_results'>.otu_table.100.denovo.rdp_assigned
                              folder/<folder minus '_results'>.metadata.txt

        'table_type' key indicates whether samples or OTUs are in rows.
            'normal' means that OTUs are in columns and samples are in rows
            'classic' means that OTUs are in rows and samples are in columns
        If not given, defaults to 'classic'
    """
    with open(yamlfile, 'r') as f:
        datasets = yamlfile.load(f)

    for dataset in datasets:
        # Grab the sub-dict with just that dataset's info
        # 分别读取数据集的内容
        data = datasets[dataset]

        # Get counts table file, if it's not already specified
        if 'otu_table' not in data:
            try:
                folder = data['folder']
                folderpath = os.path.join(batch_data_dir, folder)
                datasets[dataset]['out_table'] = os.path.relpath(os.path.join())
