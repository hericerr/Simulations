import numpy as np
import math
from sklearn.base import BaseEstimator, TransformerMixin

class WoETransformer(BaseEstimator, TransformerMixin):
	"""Simple, scikit-learn compatible Weight of Evidence transformer

	:param cat_feats: List of categorical features to be encoded
		(All features are treated as categorical by default)
	:param event: name of possitive class
	:param WOE_MIN: nimimum to clip the woe values to
	:param WOE_MAX: maximum to clip the woe values to
	"""
	def __init__(self, cat_feats=None, event=1, WOE_MIN=-10, WOE_MAX=10):
		self._WOE_MIN = WOE_MIN
		self._WOE_MAX = WOE_MAX
		self.cat_feats = cat_feats
		self.event = event

	def fit(self, X, y):
		"""Fits the transformer
		
		:param X: two dimentional np.ndarray of input features
		:param y: one dimentional np.ndarray of target variable
		"""
		X_ = X.copy()       
		res_woe_dict = {}
		res_iv_dict = {}
		
		if self.cat_feats == None:
			self.cat_feats = [i for i in range(X.shape[1])]
		for feat in self.cat_feats:
			X_[:,feat] = X_[:,feat].astype(str)
			woe_dict, iv1 = self._woe_single_x(X_[:,feat], y, self.event)
			res_woe_dict[feat] = woe_dict
			res_iv_dict[feat] = iv1
        
		self.woe = res_woe_dict
		self.iv = res_iv_dict
		return self
        
	def transform(self, X):
		"""Encode categorical columns to woe
		
		:param X: two dimentional np.ndarray of data to be encoded
		"""
		X_ = X.copy()
		for feat in self.cat_feats:
			X_[:,feat] = X_[:,feat].astype(str)
			X_[:,feat] = np.array([self.woe[feat][x] if x in self.woe[feat].keys() else 0 for x in X_[:,feat]])
		return X_

	def _woe_single_x(self, x, y, event):
		"""Compute woe for a single feature
		"""
		event_total, non_event_total = self._count_binary(y, event=event)
		x_labels = np.unique(x)
		woe_dict = {}
		iv = 0
		for x1 in x_labels:
			y1 = y[np.where(x == x1)[0]]
			event_count, non_event_count = self._count_binary(y1, event=event)
			rate_event = 1.0 * event_count / event_total
			rate_non_event = 1.0 * non_event_count / non_event_total
			if rate_event == 0:
				woe1 = self._WOE_MIN
			elif rate_non_event == 0:
				woe1 = self._WOE_MAX
			else:
				woe1 = math.log(rate_event / rate_non_event)
			woe_dict[x1] = woe1
			iv += (rate_event - rate_non_event) * woe1
		return woe_dict, iv
        
	def _count_binary(self, a, event):
		"""Counts events in given array
		"""
		event_count = (a == event).sum()
		non_event_count = a.shape[-1] - event_count
		return event_count, non_event_count