# Internet Firewall Data: Multiclass Classification
Owner: nafi
Source files: docs/00-shared-contracts.md, docs/prd/PRD-nafi-captain.md

## On the slide (max 5 bullets)
- Group 6 · Pembelajaran Mesin (Machine Learning)
- Task: predict the firewall action of a network connection, using classical machine learning only
- Dataset: UCI Internet Firewall Data (id 542), CC BY 4.0, DOI 10.24432/C5131M
- Models: Random Forest, Gradient Boosting, Logistic Regression
- Members:
  - Muhamad Nafi' Mulyo (5054251005), captain
  - Bima Satriawan (5054251031), data
  - Ahmad Zaki Fauzan Nabil (5054251044), Random Forest
  - Muhammad Nazwar Fakhrurrozy (5054251040), Gradient Boosting and protocol
  - Rayyan Binar Ramadhan (5054251025), baseline and error analysis

## Figure
none

## Say out loud (3-5 sentences)
Hello, we are Group 6, and our project uses the Internet Firewall Data from the UCI repository. Each row is a network connection, and the goal is to predict the action the firewall took on it. We use only classical machine learning, with three models: Random Forest, Gradient Boosting and Logistic Regression. Each of the five of us owns one slice of the pipeline, so everyone can explain their own part.

## If the lecturer asks
Q: Why did you choose this dataset?
A: It is a real multiclass problem with a rare class, so it shows why accuracy alone is not enough and why we report macro-F1.
