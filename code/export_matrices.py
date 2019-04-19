import json
import pandas as pd
import numpy as np

def export_confusion_matrix(confusion_dict, fname):
    # Compute dimensions
    key_set = set()
    for key in confusion_dict:
        head, tail = key.split('->')
        key_set.add(head)
        key_set.add(tail)
    size = len(key_set)
    index = sorted(key_set)
    df = pd.DataFrame(np.zeros((size, size), int))
    df.index = index
    df.columns = index
    # Populate
    for key, val in confusion_dict.items():
        head, tail = key.split('->')
        df.loc[head][tail] = val
    df.to_csv(fname)

with open('stats.json', 'r') as inp:
    pos, edges = json.load(inp)
export_confusion_matrix(pos, 'pos_df.csv')
export_confusion_matrix(edges, 'edges_df.csv')