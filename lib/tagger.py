#encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("../mining/entity_tag/src/")
sys.path.append("../webserver/")
import json
import os
import zerorpc
from entity_tag import *
from entity_dict import *
from emr_preprocessor import EMRPreproc
import traceback

class Tagger(object):
    def __init__(self):
        self.emr_preproc = EMRPreproc()
        self.emr_preproc.load_yx_title("../mining/entity_tag/data/yx_seg_title.txt")
        self.emr_preproc.load_messy_code("../mining/entity_tag/data/messy_code.txt")
        edict = EntityDict("symp")
        edict.load_file("../mining/entity_tag/data/class_term.dict.gbk")
        patternList = Pattern().getPattern_bak()
        self.tagger = EntityTagger(edict, patternList, "../mining/entity_tag/dict/wordseg_dict/")

    def tag(self, txt):
        return self.tagger.tag(txt)

if __name__ == "__main__":
    pool_size = 6
    server = zerorpc.Server(Tagger(), pool_size = pool_size)
    server.bind("tcp://0.0.0.0:9999")
    print 'tagger service start....'
    server.run()
    server.close()
