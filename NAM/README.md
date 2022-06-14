## NAM

<img src=https://user-images.githubusercontent.com/42652705/173630643-1a0aa804-83ae-4c2a-832b-58c5abc7d66e.png width="600">


## EBM
EBM is a glassbox model indented to have comparable accuracy to machine learning models such as Random Forest and Boosted Trees as well as interpretability capabilities. EBM is a Generalized Additive Model (GAM) which is very similar to linear models.EBM offers some improvements to traditional GAMs: each feature function is learned using modern machine learning technique such as bagging and boosting. Training is carried out in many iterations where each iteration consists of constructing a boosting procedure separately for each feature. As this is done with low learning rates, the order of the features does not matter. The high number of iterations aims to mitigate the effects of co-linearity in order to learn best what is the contribution of each feature to the model’s prediction. Furthermore, EBM can automatically detect and include pairwise interaction terms, this increases the accuracy of the model while preserving its explainability. Since EBM is an additive model, the contribution of each feature can be captured and visualized, and therefore enhance explainability.

<img src=https://user-images.githubusercontent.com/42652705/173630390-811a6580-59f2-4e33-bd88-c8e527ae7e95.png width="600">

## XGB

<img src=https://user-images.githubusercontent.com/42652705/173631133-384c2175-fde8-4f75-a856-a79ef5e9b28e.png width="600">

## Spline

<img src=https://user-images.githubusercontent.com/42652705/173635130-5121d4ff-74ff-40d7-a616-dc2a1d409414.png width="600">


## Reference

> Agarwal, R., Melnick, L., Frosst, N., Zhang, X., Lengerich, B., Caruana,
> R., & Hinton, G. E. (2021). Neural additive models: Interpretable machine > learning with neural nets. Advances in Neural Information Processing
> Systems, 34.
