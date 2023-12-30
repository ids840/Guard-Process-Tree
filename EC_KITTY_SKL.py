from sklearn.datasets import make_regression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from eckity.genetic_encodings.gp.tree.functions import *
from eckity.algorithms.simple_evolution import SimpleEvolution
from eckity.creators.gp_creators.full import FullCreator
from eckity.genetic_encodings.gp.tree.utils import create_terminal_set
from eckity.sklearn_compatible.regression_evaluator import RegressionEvaluator
from eckity.sklearn_compatible.sk_regressor import SKRegressor
from eckity.subpopulation import Subpopulation

def create_train_test(csv_file,col_names):
    feature_columns = col_names[:-1]
    labeled_column = col_names[len(col_names) - 1:]
    features = csv_file[feature_columns][1:]
    labeled = csv_file[labeled_column][1:]
    return features, labeled
def ec_kitty_tree(csv,column):
    data_of_csv = create_train_test(csv,column)
    features = data_of_csv[0]
    target = data_of_csv[1]
    terminal_set = []
    function_set = [f_add, f_sub, f_ifgt, f_if_then_else, f_iflte]
    for i in range(len(column)-1):
        terminal_set.append('x' + str(i))
        terminal_set.append(i)
    algo = SimpleEvolution(Subpopulation(creators=FullCreator(terminal_set=terminal_set,function_set=function_set),
                                     evaluator=RegressionEvaluator()))
    regressor = SKRegressor(algo)

    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2)
    regressor.fit(X_train, y_train.values.ravel())
    return regressor
    #print('MAE on test set:', mean_absolute_error(y_test, regressor.predict(X_test)))