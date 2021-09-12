"""

OVERVIEW:

Master Script that checks a given dataset directory for any processing requests.

"""

from optparse import OptionParser
from Operate_master import *

# Read in arguments
usage = "%prog -i DATASET_DIR"
parser = OptionParser(usage)
parser.add_option("-i", "--datadir", type="string", dest="datadir")
(options, args) = parser.parse_args()

if options.datadir is None:
    parser.error("No directory specified for the data.")

# Pipe stdout and stderr to logfiles in the new directory
working_directory = options.datadir
operate = Operate_master(working_directory)
operate.MkSourceDir()
operate.CheckCreateDataSet()
operate.downtooperate()









