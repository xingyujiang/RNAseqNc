## Make file to reproduce data

all: data analysis reviewer_analysis figuers tables supp_files
# All of the files associated with the RF parameter search
rf_params: rf_param_search rf_param_figures


### User inputs -these files are not made, they should already exist!
### 这里包含了用户输入文档
# List of tar files to download and process into data.（从Zenodo下载的tar文件目录）
tar_files = data/user_input/list_of_tar_files.txt
# Master yaml file. All tar_files should be in dataset_id: folder: entries（数据汇总，暂时还不清楚作用）
yaml_file = data/user_input/results_folders.yaml
# List of datasets to perform separate analyses for each type of case patients（好像是对多组数据的分析，后面看）
split_datasets = data/user_input/split_cases_datasets.txt
# Manual curation of reported results in papers（从文中获取的数据分析）
manual_meta_analysis = data/lit_search/literature_based_meta_analysis.txt


###############################################
#                                             #
#         DOWNLOAD TO CLEAN DATA              #
#                                             #
###############################################

### Define target data files
# define the tar files from the list_of_tar_files.txt file
raw_SRR_files := $(addprefix data/raw_otu_tables/,$(shell cat data/user_input/list_of_tar_files.txt))
# define the clean OTU table names from the dataset IDs in the results_folders.yaml
clean_otu_tables := $(shell grep -v '^    ' $(yaml_file) | grep -v '^\#' | sed 's/:/.otu_table.clean.feather/g' | sed 's/^/data\/clean_tables\//g')
# define the metadata file names from the dataset IDs in the results_folders.yaml
clean_metadata_files := $(shell grep -v '^    ' $(yaml_file) | grep -v '^\#' | sed 's/:/.metadata.clean.feather/g' | sed 's/^/data\/clean_tables\//g')

# Tables with information about each dataset
dataset_info = data/analysis_results/datasets_info.txt
split_dataset_info = data/analysis_results/datasets_info.split_cases.txt

raw_data: $(raw_tar_files)
clean_data: $(clean_otu_tables) $(clean_metadata_files)
data: raw_data clean_data $(manual_meta_analysis) $(dataset_info)

## 1. Download the raw tar.gz files from Zenodo into data/raw_otu_tables,
## only if the file doesn't already exist. Also extract the files.
# Note: when I download from Zenodo, the file date corresponds to the day
# I uploaded the data to Zenodo (May 3). Need to touch the file to update the
# modified date so that make doesn't re-make these files all the time.
$(raw_tar_files): data/user_input/list_of_tar_files.txt src/data/download_tar_folders.sh
	src/data/download_tar_folders.sh $@

## 2. Clean the raw OTU tables and metadata files
# Note: technically these clean files should depend on the raw_tar_files,
# but because the stem of the files doesn't necessarily match, including
# raw_tar_files as a prerequisite means that make can no longer parallelize
# the cleaning steps. So if you changed the raw data for one of the OTU tables,
# you need to delete it so that make knows to re-process it.
# If my results_folders were better labeled, I could simply
# write a rule like %.otu_table.clean : clean.py raw_data/%.tar.gz

# This code cleans both the OTU and metadata files,
# and writes both *.otu_table.clean and *.metadata.clean
# Technically it also depends on one function in FileIO.py
$(clean_otu_tables): src/data/clean_otu_and_metadata.py $(yaml_file)
	python $< data/raw_otu_tables $(yaml_file) $@

# Recover from the removal of $@
# i.e. if the metadata file is deleted but the OTU table still is unchanged
$(clean_metadata_files): $(clean_otu_tables)
	@if test -f $@; then :; else \
		rm -f $(subst metadata,otu_table,$@); \
		make $(subst metadata,otu_table,$@); \
  	fi

## 3. Manual meta-analysis
# This file is manually made, and provided with the repo
$(manual_meta_analysis):
	echo -e "You can find the manual meta analysis files in data/lit_search"

## 4. Dataset info - table with basic information about the datasets
$(dataset_info): src/data/dataset_info.py $(yaml_file) $(clean_otu_tables) $(clean_metadata_files)
	python $< $(yaml_file) data/raw_otu_tables data/clean_tables $@

# Same as above, but with case patients split into separate groups
$(split_dataset_info): src/data/dataset_info.py $(yaml_file) $(clean_otu_tables) $(clean_metadata_files) $(split_datasets)
	python $< $(yaml_file) data/raw_otu_tables data/clean_tables $@ --split-cases --subset $(split_datasets)