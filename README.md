# JBFD — Japan Branded Food Database (classification results)

Box-level classification results of a database of branded processed foods sold in Japan, built by web crawling and classified into food-type units ("boxes") that are mapped onto the Standard Tables of Food Composition in Japan 2020 (8th edition, "JFCT-8").

**Status: preliminary release (v0.1).** The accompanying paper is under review. Entries may change on acceptance; please check the version history below before citing specific values.

## Overview

JBFD was constructed from the private-brand product pages of three Japanese retailers (anonymised as A, B and C, as in the paper). Products were assigned to *classification boxes*, each representing one kind of food. Boxes are of two types:

* **P boxes** — boxes that correspond one-to-one to a food item of JFCT-8. Each P box carries the 5-digit JFCT-8 item code.
* **Q boxes** — boxes newly created for foods that have no corresponding item in JFCT-8 (e.g. carbonated water, mixed nuts, cut-vegetable mixes). A subset of Q boxes that receive several kinds of food under a generic name ("other teas", "assorted sets", …) is flagged as *residual* Q boxes.

The box set was built from source A (LLM proposals adjudicated by the authors, without reference to nutrient values), and was then extended source by source: products of B and C were assigned to existing boxes by an LLM choosing among TF-IDF candidates, with "no match" as an explicit option; unassigned products were clustered and new boxes were adjudicated by the authors. Nutrient values were never used for building boxes or assigning products, so that the agreement between box representative values and JFCT-8 values can serve as an independent validation of the classification.

Key figures (see the paper for details):

| | |
|---|---|
| Products collected | 10,288 |
| Products assigned to a box | 9,952 (96.7%) |
| Boxes | 866 (P 707, Q 159; 11 residual Q) |
| Boxes shared by ≥2 sources | 587 (67.8%) |
| JFCT-8 items covered by P boxes | 707 / 2,478 (28.5%) |
| Records in P boxes / Q boxes | 7,848 / 2,104 |

## Data

### `data/jbfd_boxes_v0.1.csv`

One row per classification box (866 rows), UTF-8 with BOM. Note that `box_id` and `jfct_code` have leading zeros; read them as strings (spreadsheet software may strip the zeros).

| Column | Description |
|---|---|
| `box_id` | Box identifier. P boxes: JFCT-8 5-digit item code. Q boxes: the Japanese box name. |
| `box_type` | `P` or `Q` (see Overview). |
| `box_name_ja` | Box name in Japanese. For P boxes this is the JFCT-8 item name. |
| `jfct_code` | JFCT-8 item code (P boxes only). |
| `jfct_group_no`, `jfct_group_ja` | JFCT-8 food group (1–18) and its Japanese name (P boxes only). |
| `residual_q` | 1 if the box is a residual Q box (11 boxes, 300 records), else 0. |
| `n_records` | Number of products assigned to the box. |
| `n_source_A`, `n_source_B`, `n_source_C` | Number of products from each source. |
| `n_layer_A`, `n_layer_B`, `n_layer_C` | Number of products by correspondence layer. Layer A: product corresponds directly to the JFCT-8 item; B: product approximated by a near item; C: product in a Q box. All products in Q boxes are layer C. |
| `energy_kcal_*`, `protein_g_*`, `fat_g_*`, `carbohydrate_g_*`, `salt_equiv_g_*` | For each of the five mandatory label items (per 100 g or 100 mL as labelled; mL-denominated labels were converted to 100 g assuming specific gravity 1.0 for beverages and alcoholic drinks only): `_n` number of products with a value, `_mean` mean of the labelled values (the box representative value used in the paper), `_sd` sample standard deviation (blank if n < 2). Physically impossible values were treated as missing before aggregation. |

Nutrient values are the values *declared on labels* by the retailers, not analytical values.

### Planned additions

* Adjudication records (the authors' decisions on LLM proposals for boxes and clusters).
* The user dictionary added to the morphological analyser (MeCab/IPAdic) for food-specific compound words.
* The list of national-brand names used to confirm that the sources contain private-brand products only.

## What is not released, and why

The following are **not** included, as stated in the paper (Methods 10): JAN codes, crawled URLs, retailer names and product names, and the crawlers written for each retailer's site. They contain information related to the retailers' business, and site structures change so that released crawlers could be misused. For the same reason the sources are referred to as A, B and C throughout.

## Methods

See the paper. In brief: (1) preliminary survey of 38 manufacturers and one retailer; (2) collection of product name, retailer category, nutrient declaration and its denominator, ingredients, legal food name and JAN code from three retailers' product pages (July 30 – August 9, 2026); (3) cleaning (JAN-based de-duplication, conversion to 100 g, screening of impossible values); (4) construction of the box set from source A; (5) two-stage assignment of sources B and C with "no match" as an explicit option; (6) clustering of unassigned products and adjudicated creation of new boxes; (7) validation by lexical similarity between sources, correlation with JFCT-8 values, agreement between sources, sharing of boxes across sources, and within-box consistency of Q boxes.

The script `scripts/build_box_table.py` produces `data/jbfd_boxes_v0.1.csv` from the record-level working file (not distributed) and is included for transparency of the aggregation.

## Limitations

* The box set was extended incrementally; earlier sources were not re-assigned against the final box set.
* The starting point of the box set is retailer A's own product categorisation.
* Author adjudication contributes substantially to the result; adjudication records will be released to allow inspection.
* Only private-brand products of three retailers are covered; national brands are not, so JBFD does not represent the Japanese market as a whole.
* Product variants (size, count, flavour) are separate records and are not weighted.
* Residual Q boxes are heterogeneous and are candidates for splitting as the database grows.

## Version history

* **v0.1 (2026-09)** — Box-level table (866 boxes) at manuscript submission. Preliminary; values may be revised on acceptance.

## Citation

Nakagawa S, Yamamoto A. Webクローリングと大規模言語モデルを用いた市販加工食品データベースの構築―日本食品標準成分表2020年版（八訂）に基づく分類方式の提案と妥当性の検討―. 日本栄養・食糧学会誌 (under review).

A Zenodo DOI will be added on acceptance.

Related: Nakagawa S, Yamamoto A. Bidirectional correspondence table between JFCT-8 and USDA FoodData Central. https://github.com/shnkgw-rincom/jbfd-correspondence-table (DOI 10.5281/zenodo.20103327).

## Data sources

* Ministry of Education, Culture, Sports, Science and Technology (MEXT). Standard Tables of Food Composition in Japan 2020 (Eighth Revised Edition). https://www.mext.go.jp/a_menu/syokuhinseibun/mext_01110.html
* Nutrient declarations published on the product-information websites of three Japanese retailers (not identified; see above).

## License

The dataset in `data/` and the script in `scripts/` are released under CC0 1.0 Universal (see `LICENSE`). Attribution by citing the paper is appreciated.

## Contact

Shin-ichi Nakagawa, Research Institute of Info-Communication Medicine (RinCOM), Tokyo — sn@ngi-lab.jp
