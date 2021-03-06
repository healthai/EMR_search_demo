#encoding=utf8
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("../mining/entity_tag/src/")
from bottle import route, run, template, static_file, request, redirect
import json
import commands
from entity_dict import *
from entity_tag import *

global etagger
etagger = None

def getSearchResult(keywords):
    """
    @input keywords
    @return search List
    """
    global etagger

    (pos_tag, neg_tag, polarity_res, mk_str) = etagger.tag(keywords)

    print "keywords", keywords
    print "pos tag", u" ".join(list(pos_tag))
    print "neg tag", u" ".join(list(neg_tag))
    for key in polarity_res:
        print "search.py", key + "\t" + polarity_res[key]

    req = ' curl -s -XGET http://127.0.0.1:9200/20160518/case/_search -d \'%s\''
    query_dict = {}
    query_dict["query"] = {}
    query_dict["query"]["bool"] = {}
    match_text = {}
    match_text["match_phrase"] = {}
    match_text["match_phrase"]["symp_text"] = {}
    match_text["match_phrase"]["symp_text"]["query"] = keywords
    match_text["match_phrase"]["symp_text"]["slop"] = 2
    polarity_flag = True
    for key in polarity_res:
        if polarity_res != "":
            polarity_falg = False
    if len(pos_tag | neg_tag) == 0 and polarity_flag:
        query_dict["query"]["bool"]["must"] = match_text
    else:
        query_dict["query"]["bool"]["should"] = []
        #query_dict["query"]["bool"]["should"].append(match_text)
        query_dict["query"]["bool"]["should"].append({})
        tag_bool_query = query_dict["query"]["bool"]["should"][-1]
        tag_bool_query["bool"] = {}
        tag_bool_query["bool"]["must"] = []
        for tag in pos_tag:
            tag_bool_query["bool"]["must"].append({})
            s = tag_bool_query["bool"]["must"][-1]
            s["match"] = {}
            s["match"]["symp_pos_tag"] = tag.encode("utf8")
        for tag in neg_tag:
            tag_bool_query["bool"]["must"].append({})
            s = tag_bool_query["bool"]["must"][-1]
            s["match"] = {}
            s["match"]["symp_neg_tag"] = tag.encode("utf8")
        for key in polarity_res:
            if polarity_res[key] == "":
                continue
            print "search.py polarity_res[key]", len(polarity_res[key])
            tag_bool_query["bool"]["must"].append({})
            s = tag_bool_query["bool"]["must"][-1]
            s["match"] = {}
            s["match"][key] = polarity_res[key].encode("utf8")


    print json.dumps(query_dict)
        
    '''
    query = {
        "query":{
            "bool":{
                "must": { "match": {"symp_tag":must}},
                "must_not": {"match": {"symp_text": must_not}},
                "should": [
                    {"match":{"symp_text":should_1}},
                    {"match":{"symp_text":should_2}}
                ]
            }
        }
    }
    '''
    cmd = req % (json.dumps(query_dict))
    ret, res = commands.getstatusoutput(cmd)
    
    res = json.loads(res)
    return res['hits']
 

@route('/')
def index():
    return template('view/index')

@route('/search')
def index():
    keywords = request.query.get('keywords')
    results = getSearchResult(keywords)
    return template('view/search', keywords = keywords, results= results)

@route('/show/<id>')
def index(id):
    return static_file(id.split(".")[0] +'.html', root='./html')


@route('/bootstrap/css/<filename>')
def server_static(filename):
    return static_file(filename, root='./bootstrap/css')

@route('/bootstrap/js/<filename>')
def server_static(filename):
    return static_file(filename, root='./bootstrap/js')

@route('/etagger', method='POST')
def index():
    print request.json


if __name__ == "__main__":
    edict = EntityDict("symp")
    edict.load_file("../mining/entity_tag/data/zhichangai_symp.csv")
    patternList = Pattern().getPattern()
    etagger = EntityTagger(edict, patternList, "../mining/entity_tag/dict/wordseg_dict/", "query")

    run(host='0.0.0.0', port=8080)
