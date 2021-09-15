#!/usr/bin/env python
"""
Functions to interface with the reads and metadata files.
"""

import os, sys
import yaml
import pandas as pd

# Add this repo to the path
src_dir = os.path.normpath(os.path.join(os.getcwd(), 'src/util'))
sys.path.insert(0, src_dir)