import json
import sqlite3
import os
import sys

from collections import Counter
from queue import SimpleQueue

from report_path_mappings import conll2graph

conn = sqlite3.connect('../gec.sqlite')
cursor = conn.cursor()

POS_stats = {}
edge_stats = {}

POS_stats_unaligned = {}
edge_stats_unaligned = {}


for i, (
        block_source,
        block_target,
        alignment
    ) in enumerate(cursor.execute('select `en`,`ru`,`alignment` from `en-en`')):
    n1, g1 = conll2graph(block_source)
    n2, g2 = conll2graph(block_target)
    alignment_arr = json.loads(alignment)
    for head, tail in alignment_arr:
        # Skip source unaligned
        if head == -1:
            continue
        # Code for target-unaligned stuff
        if tail == -1:
            head = str(head)
            if n1[head]['pos'] == 'PUNCT':
                continue
            pos = n1[head]['pos']
            edge = None
            for e in g1[head]:
                if e[-1] == 'up':
                    edge = e
                    break
            edge_type = edge[1]
            POS_stats_unaligned[pos] = POS_stats_unaligned.get(pos, 0)+1
            edge_stats_unaligned[edge_type] = edge_stats_unaligned.get(edge_type, 0)+1
#             continue
#         head, tail = list(map(str, [head, tail]))
#         try:
#             if n1[head]['pos'] == 'PUNCT':
#                 continue
#         except KeyError:
#             print(i)
#             print(block_source)
#             print(alignment)
#             sys.exit(1)
#         POS_key = f"{n1[head]['pos']}->{n2[tail]['pos']}"
#         POS_stats[POS_key] = POS_stats.get(POS_key, 0) + 1
#         head_relation = None
#         tail_relation = None
#         for edge in g1[head]:
#             if edge[2] == 'up':
#                 head_relation = edge[1]
#         for edge in g2[tail]:
#             if edge[2] == 'up':
#                 tail_relation = edge[1]
#         if head_relation is None:
#             raise ValueError(f'A source node without a parent:\n{block_source}')
#         if tail_relation is None:
#             raise ValueError(f'A target node without a parent:\n{block_target}')
#         edge_key = f'{head_relation}->{tail_relation}'
#         edge_stats[edge_key] = edge_stats.get(edge_key, 0) + 1

# with open('stats.json', 'w') as out:
#     json.dump([POS_stats, edge_stats], out, indent=2)

with open('stats_unaligned.json', 'w') as out:
    json.dump(
        [
            POS_stats_unaligned,
            edge_stats_unaligned
        ], 
        out, 
        indent = 2)