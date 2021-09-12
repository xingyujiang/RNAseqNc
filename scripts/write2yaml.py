"""
通过从NCBI上下载的sraruntable.txt文件与ENA上下载的filereport文件写入summary.yaml文件中
filereport 应包含run_accession, fastq_md5, study_accession, fastq_aspera
确保两个文件PRJ唯一并相同
"""

import yaml
import pandas as pd
from terminalOD import *

class AddDataset2Yaml():
    def __init__(self, summary_file, filereport, sraruntable):
        self.summary_file = summary_file
        self.filereport = filereport
        self.sraruntable = sraruntable
        self.datasetD = self.GetDataSetD()
        self.loadYaml2Dict = loadYaml2Dict(self.summary_file)

    def GetDataSetD(self):
        df_rep = pd.read_csv(self.filereport, sep="\t", encoding="UTF8")
        df_sra = pd.read_csv(self.sraruntable, sep=",", encoding="UTF8")
        df_rep.rename({'run_accession': 'Run'}, axis='columns', inplace=True)
        # check BioProject and study_accession, then merge
        if len(df_rep['study_accession'].unique()) == 1 and len(df_sra['BioProject'].unique()) == 1 and df_rep['study_accession'].unique() == df_sra['BioProject'].unique():
            datasetD = pd.merge(df_sra, df_rep, on='Run')
            return datasetD
        else:
            print("Are there multi-BioProject or the two input files are not uniform? Please check input files!")
            return None

    def GetDatasetN(self):
        while True:
            datasetN = str(input("Please enter dataset name：")).replace(" ", "")
            if len(datasetN) > 0 and datasetN not in self.loadYaml2Dict.keys():
                return datasetN
            elif len(datasetN) == 0:
                print("DataSet can't be none!")
            elif datasetN in self.loadYaml2Dict.keys():
                print("{dataset} is exist!".format(dataset=datasetN))

    def GetListNum(self, li):
        li = list(li)
        set1 = set(li)
        dict1 = {}
        for item in set1:
            dict1.update({item: li.count(item)})
        return dict1

    def SrrDict(self, srr):
        srr_dic = {}
        target = ['disease', 'disease_state', 'disease_stage', 'age', 'sex', 'organism', 'librarylayout', 'cell_type',
                  'source_name', 'fastq_md5', 'fastq_aspera', 'severity', 'timepoint', 'status', 'patient_diagnosis', 'disease_status']
        for i in target:
            if i in self.datasetD.columns:
                if i == 'disease':
                    srr_dic.update({'group': self.datasetD.loc[srr]['disease']})
                elif i == 'severity':
                    srr_dic.update({'group': self.datasetD.loc[srr]['severity']})
                elif i == 'status':
                    srr_dic.update({'group': self.datasetD.loc[srr]['status']})
                elif i == 'patient_diagnosis':
                    srr_dic.update({'group': self.datasetD.loc[srr]['patient_diagnosis']})
                elif i == 'disease_status':
                    srr_dic.update({'disease_status': self.datasetD.loc[srr]['disease_status']})
                elif i == 'disease_state':
                    srr_dic.update({'group': self.datasetD.loc[srr]['disease_state']})
                elif i == 'timepoint':
                    srr_dic.update({'timepoint': self.datasetD.loc[srr]['timepoint']})
                elif i == 'disease_stage':
                    srr_dic.update({'disease_stage': self.datasetD.loc[srr]['disease_stage']})
                elif i == 'age':
                    srr_dic.update({'age': str(self.datasetD.loc[srr]['age'])})
                elif i == 'sex':
                    srr_dic.update({'sex': self.datasetD.loc[srr]['sex']})
                elif i == 'organism':
                    srr_dic.update({'Organism': self.datasetD.loc[srr]['organism']})
                elif i == 'librarylayout':
                    srr_dic.update({'LibraryLayout': self.datasetD.loc[srr]['librarylayout']})
                elif i == 'cell_type':
                    srr_dic.update({'cell_type': self.datasetD.loc[srr]['cell_type']})
                elif i == 'source_name':
                    srr_dic.update({'cell_type': self.datasetD.loc[srr]['source_name']})
                elif i == 'fastq_md5':
                    srr_dic.update({'fastq_md5': self.datasetD.loc[srr]['fastq_md5']})
                elif i == 'fastq_aspera':
                    srr_dic.update({'fastq_aspera': self.datasetD.loc[srr]['fastq_aspera']})
        return srr_dic

    def GetDataset(self):
        self.datasetD.set_index('Run', inplace=True)
        for col in self.datasetD.columns:
            self.datasetD.rename({col: col.lower()}, axis='columns', inplace=True)
        metadata_list = {}
        manual_cols = ['years', 'analysis_tools', 'analyses', 'download', 'proceed', 'paper_title', 'paper_doi', 'rna_extraction_text', 'rna_extraction', 'reverse_transcriptase', 'cdna_amplification']
        for col in manual_cols:
            if col in ['download', 'proceed']:
                metadata_list.update({col: False})
            else:
                metadata_list.update({col: None})
        val_cols = ['Assay Type', 'AvgSpotLen', 'SRA Study', 'BioProject', 'Instrument']
        for val in val_cols:
            if len(self.datasetD[val.lower()].unique()) == 1:
                val_d = self.datasetD[val.lower()].unique()[0]
                try:
                    val_d = int(val_d)
                except:
                    val_d = str(val_d)
                metadata_list.update({val: val_d})
            else:
                metadata_list.update({val: 'UNCONFIRMED'})
                print("There is multi-{a} in this project!".format(a=val))
        if 'disease_stage' in self.datasetD.columns:
            metadata_list.update({'sample_size': self.GetListNum(self.datasetD['disease_stage'])})
        elif 'disease' in self.datasetD.columns:
            metadata_list.update({'sample_size': self.GetListNum(self.datasetD['disease'])})
        elif 'disease_state' in self.datasetD.columns:
            metadata_list.update({'sample_size': self.GetListNum(self.datasetD['disease_state'])})
        elif 'severity' in self.datasetD.columns:
            metadata_list.update({'sample_size': self.GetListNum(self.datasetD['severity'])})
        elif 'status' in self.datasetD.columns:
            metadata_list.update({'sample_size': self.GetListNum(self.datasetD['status'])})
        elif 'patient_diagnosis' in self.datasetD.columns:
            metadata_list.update({'sample_size': self.GetListNum(self.datasetD['patient_diagnosis'])})
        else:
            print("Group info missing, please check raw file!")
        SRR = {}
        for srr in self.datasetD.index:
            SRR.update({srr: self.SrrDict(srr)})
        metadata_list.update({'metadata_list': SRR})
        return metadata_list

    def wSraRun2Yaml(self):
        datasetN = self.GetDatasetN()
        with open(self.summary_file, 'r', encoding="utf-8") as f:
            content = yaml.load(f, Loader=yaml.FullLoader)
        if datasetN is None:
            print("{dataset} is not create!".format(dataset=datasetN))
            return
        else:
            if content['DataSets'] is None:
                content['DataSets'] = []
                content['DataSets'].append(datasetN)
                content[datasetN] = self.GetDataset()
            else:
                content['DataSets'].append(datasetN)
                content[datasetN] = self.GetDataset()
            print("{dataset} is created!".format(dataset=datasetN))
        # up config
        with open(self.summary_file, 'w', encoding="utf-8") as nf:
            yaml.dump(content, nf)
        return datasetN