#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一个解析输入的文件，格式还没有想好！抄点代码先理解一下

"""
import os
import os.path
import sys
from pathlib import Path
from terminalOD import *

class SummaryParser():
    def __init__(self, summary_file):
        self.summary_file = summary_file
        self.datasetID = None
        # Check summary file for integrity
        self.LoadYaml2Dict = loadYaml2Dict(self.summary_file)
        self.SummaryFileChceker()

    def sample_num(self, summary_fid, item):
        sInsize = 0
        for i in summary_fid[item]['sample_size'].values():
            sInsize += i
        sInMeta = len(summary_fid[item]['metadata_list'])
        return [sInsize, sInMeta]

    def SummaryFileChceker(self):
        # Chcek summary file for minimal config and appropriate format
        summary_fid = self.LoadYaml2Dict
        if summary_fid is None:
            raise NameError("Summary file appears to be empty. Check its contents before proceeding.")
        elif 'SOURCE' not in summary_fid.keys():
            raise NameError("SOURCE data appears to be missing. Check its contents before proceeding.")
        elif 'DataSets' not in summary_fid.keys():
            raise NameError("DataSets appears to be missing. Check its contents before proceeding.")
        try:
            if summary_fid['SOURCE'] is None:
                raise NameError("SOURCE is empty. Check its contents before proceeding.")
            else:
                for item in ['adapter', 'annotation', 'hisat_index', 'reference']:
                    if item not in list(summary_fid['SOURCE'].keys()):
                        raise NameError("%s is missing. Check its contents before proceeding." % item)
                    else:
                        if summary_fid['SOURCE'][item] is None:
                            raise NameError("%s is empty. Check its contents before proceeding." % item)
            if summary_fid['DataSets'] is None:
                print("DataSets is empty. Check its contents before proceeding.")
            else:
                if type(summary_fid['DataSets']) != list:
                    raise NameError("Change DataSets type to list.")
            # Check DataSets
            dataSets = summary_fid.copy()
            [dataSets.pop(i) for i in ['DataSets', 'SOURCE']]
            for item in summary_fid['DataSets']:
                if item not in list(dataSets.keys()):
                    print("%s is missing, please check." % item)
                else:
                    # check dataset content
                    if summary_fid[item] is None:
                        print('dataset %s is empty, please check!' % item)
                    elif summary_fid[item]['sample_size'] is None:
                        raise NameError("dataset %s smaple_size is Required, please check!" % item)
                    elif summary_fid[item]['metadata_list'] is None:
                        raise NameError("dataset %s metadata_list is Required, please check!" % item)
                    elif summary_fid[item]['download'] is not True and summary_fid[item]['download'] is not False:
                        raise NameError("Datasets %s download parameter set wrong, 'True or False' is suitable!"% item)
                    elif summary_fid[item]['proceed'] is not True and summary_fid[item]['proceed'] is not False:
                        raise NameError("Datasets %s proceed parameter set wrong, 'True or False' is suitable!"% item)
                    # check sample num
                    elif self.sample_num(summary_fid, item)[0] != self.sample_num(summary_fid, item)[1]:
                        raise NameError("Sample num is not equal, please check.")
                    else:
                        for SRR in summary_fid[item]['metadata_list'].keys():
                            for key in get_key_list(summary_fid[item]['metadata_list'][SRR]):
                                if get_key_info(summary_fid[item]['metadata_list'][SRR], key) is None:
                                    raise NameError("{SRR}'s {key} info is missing, please check!".format(SRR=SRR, key=key))
                                elif summary_fid[item]['metadata_list'][SRR]['LibraryLayout'] != 'SINGLE' and summary_fid[item]['metadata_list'][SRR]['LibraryLayout'] != 'PAIRED':
                                    raise NameError("{SRR}'s LibraryLayout parameter set wrong, 'SINGLE or PAIRED' is suitable!" .format(SRR=SRR))
        except TypeError as e:
            print(e)


    def ChooseDB(self):
        summary_fid = self.LoadYaml2Dict
        DataNumlist = []
        for i in range(len(summary_fid['DataSets'])):
            DataNumlist.append("{a}.{b}".format(a=i+1, b=summary_fid['DataSets'][i]))
        while True:
            print("There are %d datasets,include:" % len(summary_fid['DataSets']), *DataNumlist)
            try:
                num = int(input("Please choose one dataset:"))
                dataset = summary_fid['DataSets'][num-1]
                return dataset
            except:
                flag = str(input("Please choose the right number, or enter 'q' or 'e' to quite!"))
                if flag.lower() == 'q' or flag.lower() == 'quit' or flag.lower() == 'e' or flag.lower() == 'exit':
                    break
        return

    def DataSetConfig(self):
        summary_fid = self.LoadYaml2Dict
        self.datasetID = self.ChooseDB()
        if self.datasetID is None:
            print("No dataset choose, exit program!")
            sys.exit()
        self.download = summary_fid[self.datasetID]['download']
        self.proceed = summary_fid[self.datasetID]['proceed']

    def SrrConfig(self, srr):
        summary_fid = self.LoadYaml2Dict
        self.md5 = summary_fid[self.datasetID]['metadata_list'][srr]['fastq_md5']
        self.fastq_aspera = summary_fid[self.datasetID]['metadata_list'][srr]['fastq_aspera']
        self.LibraryLayout = summary_fid[self.datasetID]['metadata_list'][srr]['LibraryLayout']
        try:
            self.age = summary_fid[self.datasetID]['metadata_list'][srr]['age']
        except:
            pass
        try:
            self.sex = summary_fid[self.datasetID]['metadata_list'][srr]['sex']
        except:
            pass
        self.group = summary_fid[self.datasetID]['metadata_list'][srr]['group']
        try:
            self.disease_stage = summary_fid[self.datasetID]['metadata_list'][srr]['disease_stage']
        except:
            pass

    def UpDownLoadConf(self):
        with open(self.summary_file, 'r', encoding="utf-8") as f:
            content = yaml.load(f, Loader=yaml.FullLoader)
            # up config
            content[self.datasetID]['download'] = True
        with open(self.summary_file, 'w', encoding="utf-8") as nf:
            yaml.dump(content, nf)

    def UpProceedConf(self):
        with open(self.summary_file, 'r', encoding="utf-8") as f:
            content = yaml.load(f, Loader=yaml.FullLoader)
            # up config
            content[self.datasetID]['proceed'] = True
        with open(self.summary_file, 'w', encoding="utf-8") as nf:
            yaml.dump(content, nf)

    def delDataSet(self, path):
        dataset = self.ChooseDB()
        print(dataset)
        if dataset is None:
            print("No dataset choose, exit program!")
            sys.exit()
        else:
            datasetdir = Path(path, dataset)
            with open(self.summary_file, 'r', encoding="utf-8") as f:
                content = yaml.load(f, Loader=yaml.FullLoader)
                # up config
                del content[dataset]
                content['DataSets'].remove(dataset)
            with open(self.summary_file, 'w', encoding="utf-8") as nf:
                yaml.dump(content, nf)
            if datasetdir.is_dir():
                os.system(f'rm -r {datasetdir}')

if __name__ == "__main__":
    a = SummaryParser('/home/jy/rnaSeq/test/1.yaml')