# Deep learning-based recalibration of CUETO and EORTC prediction tools for recurrence and progression in non-muscle-invasive bladder cancer.

**Paper:** https://euoncology.europeanurology.com/article/S2588-9311(21)00112-7/fulltext

**Abstract:** Despite being standard tools for decision making, the EORTC, EAU, and CUETO risk groups provide moderate performance in predicting recurrence-free (RFS) and progression-free (PFS) survival in non-muscle-invasive bladder cancer (NMIBC). In this retrospective combined cohort data-mining study, the training group consisted of 3570 patients with de novo diagnosed NMIBC. Predictors included: gender, age, T stage, histopathological grading, tumor burden and diameter, EORTC and CUETO scores, and type of intravesical treatment. The developed models were externally validated on an independent cohort of 322 patients. Models were trained using Cox proportional hazards deep neural networks (deep learning; DeepSurv) with proprietary grid search of hyperparameters. For only surgical and BCG-treated patients, deep-learning-based models achieved c-indices of 0.650 for RFS (95%CI:0.649-0.650) and 0.878 for PFS (95%CI:0.873-0.874) in the training group. In the validation group, c-indices were estimated as 0.651 for RFS (95%CI:0.648-0.654) and 0.881 for PFS (95%CI:0.878-0.885). After inclusion of patients treated with mitomycin, RFS models' c-indices were 0.6415 (95%CI:0.6412-0.6417) and 0.660 (95%CI:0.657-0.664) for training and validation groups, respectively. Models for PFS achieved c-index of 0.885 (95%CI:0.885-0.885) in training set and 0.876 (95%CI:0.873-0.880) at validation. Tool outperformed standard-of-care risk stratification tools and showed no evidence of overfitting.  Application is open-source and available at https://biostat.umed.pl/deepNMIBC/.

**Patient summary:** We have created and validated a new tool to predict early-stage bladder cancer recurrence and progression. The application uses advanced artificial intelligence to combine state-of-the-art scales, outperforms them, and is freely available online.


## Application

[![Run on Ainize](https://ainize.ai/images/run_on_ainize_button.svg)](https://ainize.web.app/redirect?git_repo=https://github.com/kstawiski/jobczyk2020-app)

Link: https://biostat.umed.pl/deepNMIBC

Alternative: https://main-jobczyk2020-app-kstawiski.endpoint.ainize.ai/

## Build

Build:

```
docker build . -t jobczyk2020-app
```

Run:

![Docker Push](https://github.com/kstawiski/jobczyk2020-app/workflows/Docker%20Push/badge.svg)

```
docker run --name jobczyk2020-app -d --restart always -p 28810:80 kstawiski/jobczyk2020-app
```

App will be running at http://localhost:28810
