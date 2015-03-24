#!/usr/bin/env python3

from bottle import route, run, Bottle, get, post, request, static_file
import os.path
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
import yaml
import sys

conf = {}

def find_static():
    cwd = None
    try:
        cwd = os.path.dirname(__file__)
    except NameError:
        cwd = "."
    return os.path.abspath(os.path.join(cwd, "static"))

static_root = find_static()


es=None
def elasticsearch():
    global es
    if es is not None:
        return es
    es_hosts = conf.get("elasticsearch")
    print(es_hosts)
    es = Elasticsearch(es_hosts)
    return es

def es_search(query):
    search = { "query": {
                  "query_string": {
                          "query": query,
                          "default_operator": "AND"
                        },
                    },
                    "size": 25,
             }
    return elasticsearch().search(body = search)

@get("/")
def index():
    return static_file("index.html", static_root)

@get("/search/:query")
def search(query):
    json = { "@context": {"@vocab": "http://example.com/"}, "@id": "/search/%s" % query, "query": query, "hits": [] }
    hits = json["hits"]
    search = es_search(query)
    for hit in search["hits"]["hits"]:
        hits.append({"@id": hit["_id"]})
    return json


def main(config_file, *args):
    global conf
    with open(config_file) as f:
        conf = yaml.load(f)
    run(host='localhost', port=8839, reloader=True)

if __name__ == "__main__":
   main(*sys.argv[1:])
