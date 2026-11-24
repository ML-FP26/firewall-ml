# Internet Firewall Data: Multiclass Classification

Group 6 project for Pembelajaran Mesin (Machine Learning).

## Problem

A firewall decides what to do with every network connection it sees. This project predicts that decision, the `action` column, from the other 11 columns of the connection record. It is a multiclass classification task, and it uses classical machine learning only (no deep learning).

Some classes are much rarer than others. For that reason the main metric is **macro-F1**, which gives every class the same weight. Accuracy, weighted-F1, balanced accuracy, MCC, per-class precision and recall, and the confusion matrix are reported as well.

## Dataset

UCI Machine Learning Repository, *Internet Firewall Data* (id 542), DOI [10.24432/C5131M](https://doi.org/10.24432/C5131M), licensed under CC BY 4.0. We thank UCI and the dataset creators for making it available.

## Team

| Slice | Name | NRP | GitHub |
|---|---|---|---|
| Captain: repo, runner, integration, submission | Muhamad Nafi' Mulyo | 5054251005 | [nafi-mly](https://github.com/nafi-mly) |
| A: data, freeze, leakage audit | Bima Satriawan | 5054251031 | [Bima-031](https://github.com/Bima-031) |
| B: Random Forest, top features | Ahmad Zaki Fauzan Nabil | 5054251044 | [ahmadnabil000](https://github.com/ahmadnabil000) |
| C: CV protocol, Gradient Boosting, imbalance test | Muhammad Nazwar Fakhrurrozy | 5054251040 | [najwarjombi](https://github.com/najwarjombi) |
| D: metrics, Logistic Regression, error analysis | Rayyan Binar Ramadhan | 5054251025 | [rayyanbr](https://github.com/rayyanbr) |
