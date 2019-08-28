"""
Script visualizing bias-variance tradeoff
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error as mse


LR_FOLDER = 'LR/'
TREE_FOLDER = 'Tree/'


NUM_DATASETS = 50
NOISE_VARIANCE = 0.5
MAX_POLY = 12
N = 25
Ntrain = int(0.9*N)

np.random.seed(42)


def make_poly(x, D):
    """Polynomials of x up to D degree
    """
    N = len(x)
    X = np.empty((N, D+1))
    for d in range(D+1):
        X[:,d] = x**d
        if d > 1:
            X[:,d] = (X[:,d] - X[:,d].mean()) / X[:,d].std()
    return X


def true_f(x):
    """Ground truth
    """
    return np.sin(x)


def plot_prediction_curves(x_axis, prediction_curves, param, folder):
    """Plot and save all prediction curves for all model complexities
    """
    for d in range(MAX_POLY):
        for k in range(NUM_DATASETS):
            plt.plot(x_axis, prediction_curves[:,k,d], color="green", alpha=0.5)
        plt.plot(x_axis, prediction_curves[:,:,d].mean(axis=1), color="blue", linewidth=2.0, label='average prediction')
        plt.plot(x_axis, true_f(x_axis), color="orange", label='ground truth')
        plt.title(f"All prediction curves for {param} = %d" % (d+1))
        plt.legend()
        plt.savefig(folder+f'/curves{d}.png')
        plt.close()
    

def plot_bias_variance_tradeoff(X, train_predictions, train_scores, test_scores, folder):
    """Plot and save train vs test scores and bias-variance decomposition
    """
    average_train_prediction = np.zeros((Ntrain, MAX_POLY))
    squared_bias = np.zeros(MAX_POLY)
    f_Xtrain = true_f(X)[:Ntrain]
    for d in range(MAX_POLY):
        for i in range(Ntrain):
            average_train_prediction[i,d] = train_predictions[i,:,d].mean()
        squared_bias[d] = ((average_train_prediction[:,d] - f_Xtrain)**2).mean()
        
    variances = np.zeros((Ntrain, MAX_POLY))
    for d in range(MAX_POLY):
        for i in range(Ntrain):
            delta = train_predictions[i, :, d] - average_train_prediction[i,d]
            variances[i,d] = delta.dot(delta) / N
        variance = variances.mean(axis=0)
        
    degrees = np.arange(MAX_POLY) + 1
    best_degree = np.argmin(test_scores.mean(axis=0)) + 1
        
    plt.plot(degrees, train_scores.mean(axis=0), label="train score")
    plt.plot(degrees, test_scores.mean(axis=0), label="test score")
    plt.axvline(x=best_degree, label= "best coplexity", color="black")
    plt.legend()
    plt.savefig(folder+'train_test.png')
    plt.close()
    
    plt.plot(degrees, squared_bias, label = "squared bias")
    plt.plot(degrees, variance, label = "variance")
    plt.plot(degrees, test_scores.mean(axis=0), label="test score")
    plt.plot(degrees, squared_bias+variance, label="squared bias + variance")
    plt.axvline(x=best_degree, label= "best coplexity", color="black")
    plt.xlabel("Degree")
    plt.ylabel("Average score (MSE)")
    plt.legend()
    plt.savefig(folder+'bias_var.png')
    plt.close()
    
    
def main():
    x_axis = np.linspace(-np.pi, np.pi, 100)
    
    X = np.linspace(-np.pi, np.pi, N)
    np.random.shuffle(X)
    f_X = true_f(X)
    
    Xpoly = make_poly(X, MAX_POLY)
    
    train_scores_lr = np.zeros((NUM_DATASETS, MAX_POLY))
    test_scores_lr = np.zeros((NUM_DATASETS, MAX_POLY))
    train_predictions_lr = np.zeros((Ntrain, NUM_DATASETS, MAX_POLY))
    prediction_curves_lr = np.zeros((100, NUM_DATASETS, MAX_POLY))
    
    train_scores_dt = np.zeros((NUM_DATASETS, MAX_POLY))
    test_scores_dt = np.zeros((NUM_DATASETS, MAX_POLY))
    train_predictions_dt = np.zeros((Ntrain, NUM_DATASETS, MAX_POLY))
    prediction_curves_dt = np.zeros((100, NUM_DATASETS, MAX_POLY))
    
    lr = LinearRegression()
    
    for k in range(NUM_DATASETS):
        Y = f_X + np.random.randn(N)*NOISE_VARIANCE
        
        Xtrain = Xpoly[:Ntrain]
        Ytrain = Y[:Ntrain]
        
        Xtest = Xpoly[Ntrain:]
        Ytest = Y[Ntrain:]
        
        for d in range(MAX_POLY):
            lr.fit(Xtrain[:,:d+2],Ytrain)
            predictions_lr = lr.predict(Xpoly[:,:d+2])
            
            x_axis_poly = make_poly(x_axis, d+1)
            prediction_axis = lr.predict(x_axis_poly)
            
            prediction_curves_lr[:, k, d] = prediction_axis
            train_prediction_lr = predictions_lr[:Ntrain]
            test_prediction_lr = predictions_lr[Ntrain:]
            
            train_predictions_lr[:,k,d] = train_prediction_lr
            
            train_score_lr = mse(train_prediction_lr, Ytrain)
            test_score_lr = mse(test_prediction_lr, Ytest)
            
            train_scores_lr[k,d] = train_score_lr
            test_scores_lr[k,d] = test_score_lr
			
        for d in range(MAX_POLY):
            tree = DecisionTreeRegressor(max_depth=d+1)
            tree.fit(Xtrain[:,1].reshape(-1, 1) ,Ytrain)
            prediction_axis = tree.predict(x_axis.reshape(-1, 1))
            predictions_dt = tree.predict(Xpoly[:,1].reshape(-1, 1))
            
            prediction_curves_dt[:, k, d] = prediction_axis
            train_prediction_dt = predictions_dt[:Ntrain]
            test_prediction_dt = predictions_dt[Ntrain:]
            
            train_predictions_dt[:,k,d] = train_prediction_dt
            
            train_score_dt = mse(train_prediction_dt, Ytrain)
            test_score_dt = mse(test_prediction_dt, Ytest)
            
            train_scores_dt[k,d] = train_score_dt
            test_scores_dt[k,d] = test_score_dt
			
            
    plot_prediction_curves(x_axis, prediction_curves_lr, 'degree', LR_FOLDER)
    plot_bias_variance_tradeoff(X, train_predictions_lr, train_scores_lr, test_scores_lr, LR_FOLDER)
    
    plot_prediction_curves(x_axis, prediction_curves_dt, 'max_depth', TREE_FOLDER)
    plot_bias_variance_tradeoff(X, train_predictions_dt, train_scores_dt, test_scores_dt, TREE_FOLDER)
    
if __name__ == '__main__':
    main()
