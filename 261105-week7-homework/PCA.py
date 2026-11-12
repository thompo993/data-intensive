import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

X, y = fetch_openml(data_id=41082, as_frame=False, return_X_y=True, parser='liac-arff')
X = MinMaxScaler().fit_transform(X)
X_train, X_test, y_train, y_test = 	train_test_split(X, y, stratify=y, 							random_state=0, 
					train_size=1_000, 
					test_size=100)


# 2. Fit PCA using all components
pca = PCA()
pca.fit(X_train)


# 2. Calculate individual and cumulative variance percentages
exp_var_ind = pca.explained_variance_ratio_ * 100
exp_var_cum = np.cumsum(exp_var_ind)

# 3. Create the dual-axis plot
fig, ax1 = plt.subplots(figsize=(9, 5))

# Plot Individual Variance as Bars (Scree Plot)
color = '#1f77b4'
ax1.set_xlabel('Principal Component')
ax1.set_ylabel('Individual Explained Variance (%)', color=color)
bars = ax1.bar(range(1, 21), exp_var_ind[:20], color=color, alpha=0.6, label='Individual')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_xticks(range(1, len(exp_var_ind) + 1))

# Instantiates a second axes that shares the same x-axis
ax2 = ax1.twinx()  

# Plot Cumulative Variance as a Line
color = 'black'
ax2.set_ylabel('Cumulative Explained Variance (%)', color=color)
line = ax2.plot(range(1, 21), exp_var_cum[:20], color=color, marker='o', linewidth=2, label='Cumulative')
ax2.tick_params(axis='y', labelcolor=color)

# Add a threshold line (e.g., 90% variance target)
ax2.axhline(y=90, color=color, linestyle=':', alpha=0.7, label='90% Threshold')

plt.title('PCA Explained Variance: Individual vs. Cumulative')
fig.tight_layout()  
plt.grid(True, alpha=0.3)
plt.show()
