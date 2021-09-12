import hashlib
import yaml
import gzip


def get_key_list(data):
    key_list = []
    try:
        if isinstance(data, dict):
            for key in data.keys():
                key_list.append(key)
            return key_list
    except TypeError as e:
        print(e)

def get_key_info(summary_fid, key_name, default=None):
    for k, v in summary_fid.items():
        if k == key_name:
            return v
        else:
            if isinstance(v, dict):
                ret = get_key_info(v, key_name, default=None)
                if ret is not default:
                    return ret
    return default

def DownloadStr(fastqadr, fastqdir):
    ascp = 'ascp -QT -k 1 -l 300m -P33001 -i ~/.aspera/connect/etc/asperaweb_id_dsa.openssh era-fasp@'
    downloadstr = ascp + fastqadr + ' ' + fastqdir
    return downloadstr

def md5sum(file):
    with open(file, "rb") as fp:
        data = fp.read()
    fmd5 = hashlib.md5(data).hexdigest()
    return fmd5

def GetPhred(file):
    with gzip.open(file, "r") as f:
        counts = 0
        while True:
            score = []
            for line in f:
                if counts == 100000:
                    break
                counts += 1
                if counts % 4 == 0:
                    for i in line:
                        score.append(i)
            temp_max = max(score)
            temp_min = min(score)
            if temp_max <= 126 and temp_min < 59:
                return "33"
            elif temp_max > 73 and temp_min >= 64:
                return "64"
            elif temp_min > 59 and temp_min < 64 and temp_max > 73:
                return "unknown"

def loadYaml2Dict(summary_file):
    with open(summary_file, "r", encoding="utf-8") as summary_file:
        summary_fid = yaml.load(summary_file, Loader=yaml.Loader)
        return summary_fid