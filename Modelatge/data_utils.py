"""Data reader for regression dataset."""

import gzip
import os.path as osp
import tarfile
from typing import Tuple, Dict, Union, Iterator, List

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import KFold
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import OneHotEncoder
import tensorflow.compat.v1 as tf
gfile = tf.gfile

DATA_PATH = 'gs://nam_datasets/data'
DatasetType = Tuple[np.ndarray, np.ndarray]


def save_array_to_disk(filename,
                       np_arr,
                       allow_pickle = False):
  """Saves a np.ndarray to a specified file on disk."""
  with gfile.Open(filename, 'wb') as f:
    with gzip.GzipFile(fileobj=f) as outfile:
      np.save(outfile, np_arr, allow_pickle=allow_pickle)


def read_dataset(dataset_name,
                 header = 'infer',
                 names = None,
                 delim_whitespace = False):
  dataset_path = osp.join(DATA_PATH, dataset_name)
  with gfile.Open(dataset_path, 'r') as f:
    df = pd.read_csv(
        f, header=header, names=names, delim_whitespace=delim_whitespace)
  return df


def load_california_housing_data(
):
  """Loads the California Housing dataset.
  California  Housing  dataset is a canonical machine learning dataset derived
  from the 1990 U.S. census to understand the influence of community
  characteristics on housing prices. The task is regression to predict the
  median price of houses (in million dollars) in each district in California.
  For more info, refer to
  https://scikit-learn.org/stable/datasets/index.html#california-housing-dataset.
  Returns:
    A dict containing the `problem` type (i.e. regression) and the
    input features `X` as a pandas.Dataframe and the regression targets `y` as
    np.ndarray.
  """
  feature_names = [
      'MedInc', 'HouseAge', 'AveRooms', 'AveBedrms', 'Population', 'AveOccup',
      'Latitude', 'Longitude'
  ]

  archive_path = osp.join(DATA_PATH, 'cal_housing.tgz')
  with gfile.Open(archive_path, 'rb') as fileobj:
    with tarfile.open(fileobj=fileobj, mode='r:gz') as f:
      cal_housing = np.loadtxt(
          f.extractfile('CaliforniaHousing/cal_housing.data'), delimiter=',')
      # Columns are not in the same order compared to the previous
      # URL resource on lib.stat.cmu.edu
      columns_index = [8, 7, 2, 3, 4, 5, 6, 1, 0]
      cal_housing = cal_housing[:, columns_index]

  target, data = cal_housing[:, 0], cal_housing[:, 1:]

  # avg rooms = total rooms / households
  data[:, 2] /= data[:, 5]

  # avg bed rooms = total bed rooms / households
  data[:, 3] /= data[:, 5]

  # avg occupancy = population / households
  data[:, 5] = data[:, 4] / data[:, 5]

  # target in units of 100,000
  target = target / 100000.0

  return {
      'problem': 'regression',
      'X': pd.DataFrame(data, columns=feature_names),
      'y': target,
  }


class CustomPipeline(Pipeline):
  """Custom sklearn Pipeline to transform data."""

  def apply_transformation(self, x):
    """Applies all transforms to the data, without applying last estimator.
    Args:
      x: Iterable data to predict on. Must fulfill input requirements of first
        step of the pipeline.
    Returns:
      xt: Transformed data.
    """
    xt = x
    for _, transform in self.steps[:-1]:
      xt = transform.fit_transform(xt)
    return xt


def transform_data(df):
  """Apply a fixed set of transformations to the pd.Dataframe `df`.
  Args:
    df: Input dataframe containing features.
  Returns:
    Transformed dataframe and corresponding column names. The transformations
    include (1) encoding categorical features as a one-hot numeric array, (2)
    identity `FunctionTransformer` for numerical variables. This is followed by
    scaling all features to the range (-1, 1) using min-max scaling.
  """
  column_names = df.columns
  new_column_names = []
  is_categorical = np.array([dt.kind == 'O' for dt in df.dtypes])
  categorical_cols = df.columns.values[is_categorical]
  numerical_cols = df.columns.values[~is_categorical]
  for index, is_cat in enumerate(is_categorical):
    col_name = column_names[index]
    if is_cat:
      new_column_names += [
          '{}: {}'.format(col_name, val) for val in set(df[col_name])
      ]
    else:
      new_column_names.append(col_name)
  cat_ohe_step = ('ohe', OneHotEncoder(sparse=False, handle_unknown='ignore'))

  cat_pipe = Pipeline([cat_ohe_step])
  num_pipe = Pipeline([('identity', FunctionTransformer(validate=True))])
  transformers = [('cat', cat_pipe, categorical_cols),
                  ('num', num_pipe, numerical_cols)]
  column_transform = ColumnTransformer(transformers=transformers)

  pipe = CustomPipeline([('column_transform', column_transform),
                         ('min_max', MinMaxScaler((-1, 1))), ('dummy', None)])
  df = pipe.apply_transformation(df)
  return df, new_column_names


def load_dataset(dataset_name):
  """Loads the dataset according to the `dataset_name` passed.
  Args:
    dataset_name: Name of the dataset to be loaded.
  Returns:
    data_x: np.ndarray of size (n_examples, n_features) containining the
      features per input data point where n_examples is the number of examples
      and n_features is the number of features.
    data_y: np.ndarray of size (n_examples, ) containing the label/target
      for each example where n_examples is the number of examples.
    column_names: A list containing the feature names.
  """
    dataset_name == 'Housing':
    dataset = load_california_housing_data()
  else:
    raise ValueError('{} not found!'.format(dataset_name))

  data_x, data_y = dataset['X'].copy(), dataset['y'].copy()
  problem_type = dataset['problem']
  data_x, column_names = transform_data(data_x)
  data_x = data_x.astype('float32')
  if (problem_type == 'classification') and \
      (not isinstance(data_y, np.ndarray)):
    data_y = pd.get_dummies(data_y).values
    data_y = np.argmax(data_y, axis=-1)
  data_y = data_y.astype('float32')
  return data_x, data_y, column_names


def get_train_test_fold(
    data_x,
    data_y,
    fold_num,
    num_folds,
    stratified = True,
    random_state = 42):
  """Returns a specific fold split for K-Fold cross validation.
  Randomly split dataset into `num_folds` consecutive folds and returns the fold
  with index `fold_index` for testing while the `num_folds` - 1 remaining folds
  form the training set.
  Args:
    data_x: Training data, with shape (n_samples, n_features), where n_samples
      is the number of samples and n_features is the number of features.
    data_y: The target variable, with shape (n_samples), for supervised learning
      problems.  Stratification is done based on the y labels.
    fold_num: Index of fold used for testing.
    num_folds: Number of folds.
    stratified: Whether to preserve the percentage of samples for each class in
      the different folds (only applicable for classification).
    random_state: Seed used by the random number generator.
  Returns:
    (x_train, y_train): Training folds containing 1 - (1/`num_folds`) fraction
      of entire data.
    (x_test, y_test): Test fold containing 1/`num_folds` fraction of data.
  """
  if stratified:
    stratified_k_fold = StratifiedKFold(
        n_splits=num_folds, shuffle=True, random_state=random_state)
  else:
    stratified_k_fold = KFold(
        n_splits=num_folds, shuffle=True, random_state=random_state)
  assert fold_num <= num_folds and fold_num > 0, 'Pass a valid fold number.'
  for train_index, test_index in stratified_k_fold.split(data_x, data_y):
    if fold_num == 1:
      x_train, x_test = data_x[train_index], data_x[test_index]
      y_train, y_test = data_y[train_index], data_y[test_index]
      return (x_train, y_train), (x_test, y_test)
    else:
      fold_num -= 1


def split_training_dataset(
    data_x,
    data_y,
    n_splits,
    stratified = True,
    test_size = 0.125,
    random_state = 1337):
  """Yields a generator that randomly splits data into (train, validation) set.
  The train set is used for fitting the DNNs/NAMs while the validation set is
  used for early stopping.
  Args:
    data_x: Training data, with shape (n_samples, n_features), where n_samples
      is the number of samples and n_features is the number of features.
    data_y: The target variable, with shape (n_samples), for supervised learning
      problems.  Stratification is done based on the y labels.
    n_splits: Number of re-shuffling & splitting iterations.
    stratified: Whether to preserve the percentage of samples for each class in
      the (train, validation) splits. (only applicable for classification).
    test_size: The proportion of the dataset to include in the validation split.
    random_state: Seed used by the random number generator.
  Yields:
    (x_train, y_train): The training data split.
    (x_validation, y_validation): The validation data split.
  """
  if stratified:
    stratified_shuffle_split = StratifiedShuffleSplit(
        n_splits=n_splits, test_size=test_size, random_state=random_state)
  else:
    stratified_shuffle_split = ShuffleSplit(
        n_splits=n_splits, test_size=test_size, random_state=random_state)
  split_gen = stratified_shuffle_split.split(data_x, data_y)

  for train_index, validation_index in split_gen:
    x_train, x_validation = data_x[train_index], data_x[validation_index]
    y_train, y_validation = data_y[train_index], data_y[validation_index]
    assert x_train.shape[0] == y_train.shape[0]
    yield (x_train, y_train), (x_validation, y_validation)
