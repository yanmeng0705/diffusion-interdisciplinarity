# Data and code for the main-text figures

This repository contains the derived data and plotting code needed to reproduce Figures 1–3 of

> Xing Y., Wang Y., Bu Y., Zhou Z., Dong K., Ma Y. *A U-shaped trajectory of diffusion-based interdisciplinarity in science: a recovery carried by applied fields toward which AI realigns.*

The underlying bibliographic data come from OpenAlex (https://openalex.org; snapshot retrieved in September 2024). The files below are the aggregated outputs of our analysis pipeline, which works on subfield-level citation networks built from that snapshot (252 subfields in 26 fields).

## Layout

```
code/
  figstyle.py                 shared plotting style (colors, font sizes, label abbreviations)
  fig1_phenomenon.py          Figure 1
  fig2_mechanism.py           Figure 2
  fig3_reconfiguration.py     Figure 3
output/final/
  s1/s1_RI_timeseries.csv
  s2/s2_12_quadrant.csv
  s2/s2_14_established.csv
  s3/s3_20_indegree_share_change.csv
  s3/s3_22_bidirectional.csv
  s3/s3_23_ai_stats_inout.csv
  s3/s3_24_ai_stats_cited_subfields.csv
  s4/s4_30_decline_vs_rise.csv
```

## Files and the figure panels they produce

| File | Panel | Columns used |
|---|---|---|
| `s1/s1_RI_timeseries.csv` | Fig. 1A | `year` (five-year window), `RI_mean`, `RI_se` (s.e.m. across subfields) |
| `s4/s4_30_decline_vs_rise.csv` | Fig. 1B | `field_name`, `contrib_decline`, `contrib_rise` (field contributions to the aggregate ΔRI of each segment) |
| `s2/s2_12_quadrant.csv` | Fig. 2A, 2B | `subfield_id`, `subfield_name`, `RI_end` (RI in 2014–2023), `delta_RI` (2004–2013 to 2014–2023), `quadrant` |
| `s2/s2_14_established.csv` | Fig. 2B | `subfield_id`, `RI_end` (mature hubs, used to select the top 10 by RI) |
| `s3/s3_20_indegree_share_change.csv` | Fig. 2B | `subfield_id`, `source_field_name`, `delta_share` (change in in-citation share, percentage points) |
| `s3/s3_22_bidirectional.csv` | Fig. 2C | `tech_field`, `forward_mean`, `reverse_mean`, `forward_se`, `reverse_se` |
| `s3/s3_23_ai_stats_inout.csv` | Fig. 3A | `subfield` (AI or Statistics), `field_name`, `in_delta`, `out_delta` (percentage points) |
| `s3/s3_24_ai_stats_cited_subfields.csv` | Fig. 3B | `exclude_own_field`, `citing_subfield`, `target_subfield_id`, `share_base`, `share_end`, `delta_share` (percentage points) |

Subfield identifiers are OpenAlex subfield IDs (e.g., 1702 = Artificial Intelligence, 2613 = Statistics and Probability). Quadrant labels in `s2_12_quadrant.csv` are `core_driver`, `established` (mature hub), `riser` and `stable_low`.

## Running

Requirements: Python 3, `numpy`, `pandas`, `matplotlib`.

Run from the repository root, so that the scripts find `./output/final/`:

```
python code/fig1_phenomenon.py
python code/fig2_mechanism.py
python code/fig3_reconfiguration.py
```

Figures are written as PNG and PDF to `code/output/`. Each script also accepts `--demo`, which draws the layout from simulated values and does not read the data files.
