import os
import sys
from write2yaml import *
from SummaryParser import *
from conole_log import *
import re

class Operate_master():
    def __init__(self, path):
        self.path = path
        # Parse summary file
        self.summary_file = Path(path, '../1.yaml')
        self.summary_obj = SummaryParser(self.summary_file)
        self.summary_fid = self.summary_obj.LoadYaml2Dict
        if self.W2Ymal() is None:
            self.summary_obj.DataSetConfig()
        else:
            self.summary_file = Path(path, '../1.yaml')
            self.summary_obj = SummaryParser(self.summary_file)
            self.summary_fid = self.summary_obj.LoadYaml2Dict
            self.summary_obj.DataSetConfig()
        self.log = Loggers(self.path)

    def MkSourceDir(self):
        # check SOURCE in workdir
        sourcedir = Path(self.path, 'SOURCE')
        if sourcedir.is_dir() is False:
            print("SOURCE is missing,please check!")
            print("Create SOURCE file!")
            os.system("mkdir {file}".format(file=sourcedir))
            for filen in self.summary_fid['SOURCE'].keys():
                filenname = os.path.join(sourcedir, filen)
                os.system("mkdir {filename}".format(filename=filenname))

    def W2Ymal(self):
        # whether update a new dataset
        while True:
            As = str(input("Press yes or no to create new dataset!('e' or 'q' to quit)  "))
            if As.lower() == 'yes' or As.lower() == 'y':
                filereport = Path(self.path, str(input("Please input report_file!===> ")))
                sraruntable = Path(self.path, str(input("Please input sraruntable!===> ")))
                # try:
                AddDataset2Yaml(self.summary_file, filereport, sraruntable).wSraRun2Yaml()
                    # return
                # except:
                #     print("Input file is not exist, please check!")
            elif As.lower() == 'n' or As.lower() == 'no':
                return None
            elif As.lower() == 'e' or As.lower() == 'q' or As.lower() == 'quit' or As.lower() == 'exit':
                sys.exit()

    def CheckCreateDataSet(self):
        # operate dataset
        datasetID = self.summary_obj.datasetID
        datasetdir = Path(self.path, datasetID)
        os.system("mkdir -p {file}".format(file=datasetdir))
        os.system("mkdir -p {file}/{files}".format(file=datasetdir, files='{fastq/{raw,trimed},rmdup,clean,align,peaks,qc,aticle}'))
        # os.system("mkdir -p {file}/{files}".format(file=datasetdir, files='{fastq}'))

    def Down2Check(self, dataset):
        try:
            SRR_list = self.summary_obj.get_key_list(self.summary_fid[dataset]['metadata_list'])
            while SRR_list:
                for srr in SRR_list:
                    self.summary_obj.SrrConfig(srr)
                    if ';' not in self.summary_obj.md5:
                        filename = srr + '.fastq.gz'
                        fastqfile = Path(self.path, dataset, 'fastq', 'raw', filename)
                        fastqfiledir = os.path.join(self.path+'/'+dataset+'/'+'fastq'+'/'+'raw')
                        if fastqfile.is_file():
                            print("{SRR} is exit!".format(SRR=srr))
                            # check md5sum
                            if md5sum(fastqfile) != self.summary_obj.md5:
                                os.system(DownloadStr(self.summary_obj.fastq_aspera, fastqfiledir))
                            else:
                                print("{SRR} download complete!".format(SRR=srr))
                                SRR_list.remove(srr)
                        else:
                            os.system(DownloadStr(self.summary_obj.fastq_aspera, fastqfiledir))
                    else:
                        fastq_s = self.summary_obj.fastq_aspera
                        md5_s = self.summary_obj.md5
                        f_1 = fastq_s.split(';')[0]
                        f_2 = fastq_s.split(';')[1]
                        fn_1 = srr + '_1.fastq.gz'
                        fn_2 = srr + '_2.fastq.gz'
                        m_1 = md5_s.split(';')[0]
                        m_2 = md5_s.split(';')[1]
                        fastqfile_1 = Path(self.path, dataset, 'fastq', 'raw', fn_1)
                        fastqfile_2 = Path(self.path, dataset, 'fastq', 'raw', fn_2)
                        fastqfiledir = os.path.join(self.path + '/' + dataset + '/' + 'fastq' + '/' + 'raw')
                        if fastqfile_1.is_file() and fastqfile_2.is_file():
                            print("{SRR} is exit!".format(SRR=srr))
                            # check md5sum
                            if md5sum(fastqfile_1) != m_1:
                                os.system(DownloadStr(f_1, fastqfiledir))
                            elif md5sum(fastqfile_2) != m_2:
                                os.system(DownloadStr(f_2, fastqfiledir))
                            else:
                                print("{SRR} download complete!".format(SRR=srr))
                                SRR_list.remove(srr)
                        else:
                            os.system(DownloadStr(f_1, fastqfiledir))
                            os.system(DownloadStr(f_2, fastqfiledir))
            print(("{dataset} RAW SRA is downloaded.".format(dataset=dataset)))
        except TypeError as e:
            print("There is a {e} error when download raw data!".format(e=e))

    def Trim(self, dataset):
        try:
            SRR_list = self.summary_obj.get_key_list(self.summary_fid[dataset]['metadata_list'])
            ipath = os.path.join(self.path, dataset, 'fastq', 'raw')
            opath = os.path.join(self.path, dataset, 'fastq', 'trimed')
            qcpath = Path(self.path, dataset, 'qc')
            fileEnd1 = '_1.fastq.gz'
            fileEnd2 = '_2.fastq.gz'
            fileEnd = '.fastq.gz'
            for srr in SRR_list:
                self.summary_obj.SrrConfig(srr)
                if self.summary_obj.LibraryLayout == 'PAIRED':
                    inFile1 = ipath + '/' + srr + fileEnd1
                    inFile2 = ipath + '/' + srr + fileEnd2
                    outFile1 = opath + '/' + srr + fileEnd1
                    outFile2 = opath + '/' + srr + fileEnd2
                    if GetPhred(inFile1) == "33" and GetPhred(inFile2)== "33":
                        os.system(f'fastp -i {inFile1} -I {inFile2} -o {outFile1} -O {outFile2} -h {qcpath}/{srr}.html -j {qcpath}/{srr}.json -z 4 -q 20 -u 30 -w 8 -5 3 -3 3 -W 4 -M 15')
                    elif GetPhred(inFile1) == "64" and GetPhred(inFile2)== "64":
                        os.system(f'fastp -i {inFile1} -I {inFile2} -6 -o {outFile1} -O {outFile2} -h {qcpath}/{srr}.html -j {qcpath}/{srr}.json -z 4 -q 20 -u 30 -w 8 -5 3 -3 3 -W 4 -M 15')
                    else:
                        sys.exit(1)
                elif self.summary_obj.LibraryLayout == 'SINGLE':
                    inFile = ipath + '/' + srr + fileEnd
                    outFile = opath + '/' + srr + fileEnd
                    if GetPhred(inFile) == "33":
                        os.system(f'fastp -i {inFile} -o {outFile}  -h {qcpath}/{srr}.html -j {qcpath}/{srr}.json -z 4 -q 20 -u 30 -w 8 -5 3 -3 3 -W 4 -M 15')
                    elif GetPhred(inFile) == "64":
                        os.system(f'fastp -i {inFile}  -6 -o {outFile}  -h {qcpath}/{srr}.html -j {qcpath}/{srr}.json -z 4 -q 20 -u 30 -w 8 -5 3 -3 3 -W 4 -M 15')
                    else:
                        sys.exit(1)
            print("Trim accomplished!!")
            return 1
        except TypeError as e:
            print(e)

    def downtooperate(self):
        # check download
        datasetID = self.summary_obj.datasetID
        if self.summary_obj.download is True:
            print("{dataset} RAW SRA is downloaded.".format(dataset=datasetID))
            # check if SRR files are provided.
        else:
            print(("{dataset} RAW SRA is downloading.".format(dataset=datasetID)))
            self.Down2Check(datasetID)
            self.summary_obj.UpDownLoadConf()
        # check proceed
        if self.summary_obj.proceed is True:
            print("{dataset} analysis is accomplish.".format(dataset=datasetID))
        else:
            print(("{dataset} RAW SRA is proceeding.".format(dataset=datasetID)))
            print("Check fastq trimed file...")
            # SRR_list = self.summary_obj.get_key_list(self.summary_fid[dataset]['metadata_list'])
            # trim_path = os.path.join(self.path + dataset + 'fastq', 'trimed')
            # trimed_list = os.listdir(trim_path)
            self.Trim(datasetID)


