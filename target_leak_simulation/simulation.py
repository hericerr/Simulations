import datetime
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from joblib import Parallel, delayed


class TargetLeakageSimulation(object):
    """Simulation that demonstrates the importance of proper model validation
    
    Simulates two ways of approaching the modelling:
        - correct one: using only train sample to build the whole pipeline
        - incorrect one: using the whole development sample (train+test)
          to build part of the pipeline (e.g. fitting transformers, preselecting
          features etc.) which can cause a severe target leakage and is, sadly, 
          quite a common mistake.
          
    Each round, data (simulated using the provided data generator) is split into
    train, test and production. One pipeline is build using the train test only,
    second uses train+test to fit the transformer and train to fit the estimator,
    both pipelines are then tested on unseen data to simulate production.
    
    :param transformer: sklearn transformer
    :param estimator: sklearn estimator
    :param data_generator: callable returning data as a tuple (X, y)
    """

    def __init__(self,
                 transformer,
                 estimator,
                 data_generator
				):
				 
        self.transformer = transformer
        self.estimator = estimator
        self.data_generator = data_generator
        
    def _run(self, kwargs):
        """Runs one round of simulation
		"""
        X_full, y_full = self.data_generator(**kwargs)
        X_dev, X_prod, y_dev, y_prod = train_test_split(X_full,
                                                        y_full,
                                                        test_size=0.2)
        X_train, X_test, y_train, y_test = train_test_split(X_dev,
                                                            y_dev,
                                                            test_size=0.25)
        # correct
        model_correct = Pipeline([('transformer', self.transformer),
                                  ('estimator', self.estimator)])
        model_correct.fit(X_train, y_train)
        correct_train = model_correct.score(X_train, y_train)
        correct_test = model_correct.score(X_test, y_test)
        correct_prod = model_correct.score(X_prod, y_prod)
        
        # leakage
        self.transformer.fit(X_dev, y_dev)
        self.estimator.fit(self.transformer.transform(X_train), y_train)
        model_leakage = Pipeline([('transformer', self.transformer),
                                  ('estimator', self.estimator)])
        leakage_train = model_leakage.score(X_train, y_train)
        leakage_test = model_leakage.score(X_test, y_test)
        leakage_prod = model_leakage.score(X_prod, y_prod)
       
        return correct_train, correct_test, correct_prod, \
                leakage_train, leakage_test, leakage_prod
    
    def run(self, n_simul=100, n_jobs=-1, verbose=True, **kwargs):
        """Runs the simulation `n_simul` number of times
        
        :param n_simul: number of simulation rounds
        :param n_jobs: number of parallel jobs
        :param verbose: whether to print out the results
        :Keyword Arguments: arguments of the data generator 
        
        :returns: np.ndarray of results of shape (n_simul, 6),
            columns are ordered: correct train score, correct test score,
            correct prod score, leakage train score, leakage test score,
            leakage prod score
        """
        start = datetime.datetime.now()
        
        results = Parallel(n_jobs=n_jobs) \
        (delayed(self._run)(kwargs) for _ in range(n_simul))
        results = np.asarray(results)
        
        duration = datetime.datetime.now() - start
        
        if verbose:
            self._report(results, duration)
            
        return results
        
    def _report(self, results, duration):
        """Prints textual report of the simulation results
        """
        print("Correct approach:")
        print("Train accuracy: {}".format(round(np.mean(results[:,0]), 4)))
        print("Test accuracy: {}".format(round(np.mean(results[:,1]), 4)))
        print("Production accuracy: {}".format(round(np.mean(results[:,2]), 4)))
        print("")
        print("Leakage approach:")
        print("Train accuracy: {}".format(round(np.mean(results[:,3]), 4)))
        print("Test accuracy: {}".format(round(np.mean(results[:,4]), 4)))
        print("Production accuracy: {}".format(round(np.mean(results[:,5]), 4)))
        print("")
        print("Simulation run in: {}".format(duration))