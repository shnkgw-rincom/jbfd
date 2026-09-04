"""Build the box-level JBFD table (data/jbfd_boxes_v0.1.csv) from the
record-level working file.  The record-level file is NOT distributed
(it contains JAN codes, URLs, retailer names and product names; see
README "What is not released").  Sources are anonymised as A/B/C in
the same way as in the paper.
"""
import re, sys
import pandas as pd, numpy as np

SRC = sys.argv[1] if len(sys.argv) > 1 else 'JBFD20260810.xlsx'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'data/jbfd_boxes_v0.1.csv'

# Mapping from the internal source identifiers to the anonymised labels
# A/B/C used in the paper.  The mapping itself is not distributed; supply it
# as a small JSON file {"<internal id>": "A", ...} via the third argument.
import json
SOURCE_MAP = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {}
NUT = {'kcal_100': 'energy_kcal', 'protein_g_100': 'protein_g', 'fat_g_100': 'fat_g',
       'carb_g_100': 'carbohydrate_g', 'salt_g_100': 'salt_equiv_g'}
RESIDUAL_Q = ['その他茶', 'その他調味料', 'その他乾物', '干物（その他）', 'セット・詰め合わせ',
              'おかずセット', 'ワンプレート食事', 'おせち惣菜', '和惣菜（その他）',
              '肉惣菜（その他）', 'ドライフルーツ（その他・ミックス）']
JFCT_GROUP = {1: '穀類', 2: 'いも及びでん粉類', 3: '砂糖及び甘味類', 4: '豆類', 5: '種実類', 6: '野菜類',
              7: '果実類', 8: 'きのこ類', 9: '藻類', 10: '魚介類', 11: '肉類', 12: '卵類', 13: '乳類',
              14: '油脂類', 15: '菓子類', 16: 'し好飲料類', 17: '調味料及び香辛料類', 18: '調理済み流通食品類'}

df = pd.read_excel(SRC)
a = df[df.box_status == '割当'].copy()
a['box_key'] = a.box_key.astype(str)
a['src'] = a.source.map(SOURCE_MAP)
assert a.src.notna().all()
a['isP'] = a.box_key.str.fullmatch(r'\d{5}')

rows = []
for key, g in a.groupby('box_key', sort=False):
    isP = bool(g.isP.iloc[0])
    label = g.box_label.iloc[0]
    if isP:
        m = re.match(r'(\d{5})　(.*?)　\d+kcal', label)
        name = m.group(2) if m else label.split('　', 1)[1]
        name = name.replace('　', ' ')
        code = key
        grp_no = int(key[:2])
        grp = JFCT_GROUP[grp_no]
    else:
        name = label.replace('独自新設：', '')
        code = ''
        grp_no = ''
        grp = ''
    r = {'box_id': key, 'box_type': 'P' if isP else 'Q', 'box_name_ja': name,
         'jfct_code': code, 'jfct_group_no': grp_no, 'jfct_group_ja': grp,
         'residual_q': int((not isP) and key in RESIDUAL_Q),
         'n_records': len(g)}
    for s in 'ABC':
        r[f'n_source_{s}'] = int((g.src == s).sum())
    for l in 'ABC':
        r[f'n_layer_{l}'] = int((g.box_layer == l).sum())
    for col, nm in NUT.items():
        v = g[col].dropna()
        r[f'{nm}_n'] = len(v)
        r[f'{nm}_mean'] = round(v.mean(), 2) if len(v) else ''
        r[f'{nm}_sd'] = round(v.std(ddof=1), 2) if len(v) >= 2 else ''
    rows.append(r)

out = pd.DataFrame(rows)
out = out.sort_values(['box_type', 'box_id']).reset_index(drop=True)
out.to_csv(OUT, index=False, encoding='utf-8-sig')
print(len(out), 'boxes;', (out.box_type == 'P').sum(), 'P;', (out.box_type == 'Q').sum(), 'Q;',
      out.n_records.sum(), 'records;', out.residual_q.sum(), 'residual Q boxes')
