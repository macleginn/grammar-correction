import json
import sqlite3
import os

DATAPATH = '../data 2'

def extract_blocks(fobj):
    blocks = []
    tmp = []
    for line in fobj:
        # Either a block has just ended or we are between blocks
        stripped = line.strip()
        if not stripped:
            if not tmp:
                continue
            else:
                blocks.append('\n'.join(tmp))
                tmp = []
        else:
            tmp.append(stripped)
    if tmp:
        blocks.append('\n'.join(tmp))
    return blocks


conn = sqlite3.connect('../gec.sqlite')
with open(f'{DATAPATH}/en_esl-ud-train.conllu', 'r') as inp:
    blocks_uncorrected = extract_blocks(inp)
with open(f'{DATAPATH}/corrected/en_cesl-ud-train.conllu', 'r') as inp:
    blocks_corrected = extract_blocks(inp)
with open(f'{DATAPATH}/en_esl-ud-train.conllu.align.json', 'r') as inp:
    alignments = json.load(inp)

# Test associations between blocks and alignments using sentence ids
triple_dict = {}
for b in blocks_uncorrected:
    first_line = b.splitlines()[0]
    sent_id = first_line.split('sent_id = ')[1].strip()
    triple_dict[sent_id] = {}
    triple_dict[sent_id]['uncorrected'] = b
for b in blocks_corrected:
    first_line = b.splitlines()[0]
    sent_id = first_line.split('sent_id = ')[1].strip()
    triple_dict[sent_id]['corrected'] = b
for a in alignments:
    sent_id = a[0].strip()
    try:
        triple_dict[sent_id]['alignment'] = a[1][1]
    except KeyError:
        print(sent_id)

cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS `en-en`')
cursor.execute(
    '''
    CREATE TABLE `en-en` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `en` TEXT,
        `ru` TEXT,
        `alignment` TEXT
    )
    '''
)


for key, val in triple_dict.items():
    if 'corrected' not in val or 'alignment' not in val:
        print(f'Incomplete record: {key}')
    cursor.execute(
        '''
        INSERT INTO `en-en`
        (`en`,`ru`,`alignment`)
        VALUES (?,?,?)
        ''',
        (
            val['uncorrected'],
            val['corrected'],
            json.dumps(val['alignment'])
        ))

conn.commit()