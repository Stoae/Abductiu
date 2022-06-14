for m_name in 'ebm' 'ebm-bf' 'ebm-bf-o16-i16' 'ebm-bf-o8' 'ebm-o16-i16' 'ilr' 'lr' 'mlr' ; do
    python -u main.py --identifier 082319_datasets --model_name ${m_name} --d_name "calhousing"  &> logs/090119_calhousing_${m_name}.log &
done

# 2nd batch
for m_name in 'rf-n1000' 'skgbt' 'skgbt-o8' 'spline' 'xgb-d1' 'xgb-d1-o16' 'xgb-d3' 'xgb-d3-o16'; do
    python -u main.py --identifier 082319_datasets --model_name ${m_name} --d_name "calhousing"  &> logs/083119_calhousing_ ${m_name}.log &
done



for m_name in 'ilr' 'lr' 'mlr'; do
    python -u main.py --identifier 082319_datasets --model_name ${m_name} --overwrite 1 --d_name  "calhousing" &> logs/090119_${m_name}.log &
done



## Now rerun things in the dataset
# for m_name in 'ebm' 'ebm-bf' 'ebm-bf-o16-i16' 'ebm-bf-o8' 'ebm-o16-i16' 'ilr' 'lr' 'mlr' ; do
for m_name in 'rf-n1000' 'skgbt' 'skgbt-o8' 'spline' 'xgb-d1' 'xgb-d1-o16' 'xgb-d3' 'xgb-d3-o16'; do
    python -u main.py --identifier 082319_datasets --model_name ${m_name} --d_name "calhousing"  &> logs/090119_rerun_${m_name}.log &
done


for d_name in  "calhousing"; do
    python feature_importances.py --identifier 0905 --d_name ${d_name} &> logs/090219_fimp_${d_name}.log &
done


for d_name in  "calhousing"; do
    python feature_importances.py --identifier 0905 --d_name ${d_name} --model_name ebm-bf  &> logs/090219_fimp_ebmbf_${d_name}.log &
done

for d_name in  "calhousing"; do
    python feature_importances.py --identifier 0905_one_at_a_time --exp_mode OneAddATimeExp --d_name ${d_name}  &> logs/090319_fimp_${d_name}.log &
done


for m_name in ebm-o8 xgb-d1-o8; do
    python -u main.py --identifier 082319_datasets --model_name ${m_name} --d_name "calhousing"  &> logs/083119_calhousing_diabetes${m_name}.log &
done

# testing
m_name=ebm-o8
python -W error -u main.py --identifier 082319_datasets --model_name ${m_name} --d_name "calhousing" 

# run the script to cache all the df (except the diabetes.... not finish yet.)
python -u summarize.py --identifier 0906 --d_name calhousing --data_path results/082319_datasets.csv &> logs/0907_summarize.log &




# Analyze SS
python -u summarize.py --identifier 0906 --data_path results/090619_semi_synthetic.csv

# Rerun to cache the df....but keeps crashing 
python -u summarize.py --identifier 0906 --d_name bikeshare calhousing credit --data_path results/082319_datasets.csv &> logs/0907_summarize.log &

