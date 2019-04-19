import sqlite3
from queue import Queue


def conll2tree(record):
    'Returns a UD tree together with the index of the root node.'
    tree = {}
    root = None
    for line in record.splitlines():
        if line.startswith('#'):
            continue
        fields = line.strip().split('\t')
        pos = fields[3]
        if pos == 'PUNCT':
            continue
        key = fields[0]
        # wordform = fields[1] 
        parent = fields[6]
        relation = fields[7]
        if relation == 'root':
            root = key
        # Children are always added in their linear order
        tree[parent] = tree.get(parent, []) + [(key, relation)]
    return (tree, root)


def linearise_tree(conll_tree, root_index):
    q = Queue()
    q.put((root_index, 'root', 0))
    q.put((-1, '|', None))
    current_depth = 0
    # Single pipes separate children of a particular node.
    # Double pipes separate tree levels.
    result = []
    while not q.empty():
        current_node, relation, new_depth = q.get()
        if relation == '|':
            result.append(relation)
            continue
        if new_depth != current_depth:
            result.append('||')
            current_depth = new_depth
        result.append(relation)
        # Check if we reached a leaf
        if current_node in conll_tree:
            for key, relation in conll_tree[current_node]:
                q.put((key, relation, current_depth+1))
            q.put((-1, '|', None))
    return result

conn = sqlite3.connect('../gec.sqlite')
cursor = conn.cursor()

blocks_unc = [el[0] for el in cursor.execute('select `en` from `en-en`;')]
blocks_cor = [el[0] for el in cursor.execute('select `ru` from `en-en`;')]
assert len(blocks_cor) == len(blocks_unc)

same = different = 0
for i, b_unc in enumerate(blocks_unc):
    b_cor = blocks_cor[i]
    tree_unc, root_unc = conll2tree(b_unc)
    tree_cor, root_cor = conll2tree(b_cor)
    if linearise_tree(tree_unc, root_unc) == linearise_tree(tree_cor, root_cor):
        same += 1
    else:
        different += 1

print(same, different, same / (same+different)*100)