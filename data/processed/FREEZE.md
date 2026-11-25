# Data freeze summary

Frozen on: 2026-11-25  
Random state: 42  
Test size: 0.2  

## Row counts

| Stage | Rows |
|---|---|
| Raw (before dedupe) | 65,532 |
| After removing exact duplicates | 57,170 |
| Removed as duplicates | 8,362 |
| Train (80 %) | 45,736 |
| Test (20 %) | 11,434 |

Conflicting feature groups (same features, different labels): 9

## Class distribution after dedupe

| Class | After dedupe | Train | Test |
|---|---|---|---|
| allow | 37,439 | 29,951 | 7,488 |
| deny | 8,042 | 6,434 | 1,608 |
| drop | 11,635 | 9,308 | 2,327 |
| reset-both | 54 | 43 | 11 |

Rare-class policy: keep_all_4_classes

## SHA-256 checksums

| File | SHA-256 |
|---|---|
| train.csv | `3d648a7cb32932dbf1b9426e64a740b29a2ad50fed28f6ccc75f2ebb0afece72` |
| test.csv  | `b2f92ed3ba5362e7d7ba8d098b4f3720798f32949fe17ae6ee93821e775f4ed8` |