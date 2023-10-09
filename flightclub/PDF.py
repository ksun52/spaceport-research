# script to try to get a smooth probability distribution function

import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV
import pdb 
from scipy.stats import laplace

# launch angles as gotten from US_probability_dist function in plot_all_trajectories
launch_angles = np.array([
[-0.26145078],
[-0.34086389],
[ 0.        ],
[ 0.        ],
[-0.34119829],
[ 0.        ],
[-0.34064702],
[-0.4646022 ],
[-0.34086389],
[-0.34105372],
[-0.34086389],
[-0.34105372],
[-0.34086389],
[-0.34064702],
[-0.34064702],
[-0.34086389],
[-0.34086389],
[ 2.80788606],
[-0.34105372],
[-0.34105372],
[-0.27961655],
[-0.4646022 ],
[-0.4646022 ],
[-0.34086389],
[-0.27961655],
[-0.34105372],
[-0.34064702],
[-0.34064702],
[-0.34105372],
[-0.34105372],
[-0.34064702],
[-0.27961655],
[-0.34064702],
[-0.34064702],
[ 2.86165681],
[-0.34105372],
[-0.27961655],
[ 1.57079633],
[-0.34064702],
[-0.34105372],
[-0.34105372],
[-0.34064702],
[-0.34105372],
[-0.27961655],
[-0.34064702],
[-0.34064702],
[-0.34064702],
[-0.34086389],
[-0.27961655],
[-0.34064702],
[-0.27961655],
[-0.34105372],
[-0.34086389],
[-0.34064702],
[-0.34105372],
[-0.34064702],
[-0.34064702],
[-0.27961655],
[-0.34064702],
[-0.34105372],
[-0.34064702],
[-0.2791901 ],
[-0.27961655],
[-0.34064702],
[-0.34086389],
[-0.34064702],
[-0.34105372],
[-0.34064702],
[-0.4646022 ],
[-0.34064702],
[-0.34105372],
[-0.34064702],
[-0.46459097],
[-0.34064702],
[-0.34105372],
[-0.34105372],
[-0.27961655],
[-0.34064702],
[-0.34064702],
[-0.27961655],
[-0.34064702],
[-0.34105372],
[-3.12804786],
[-0.34064702],
[-0.34064702],
[-0.34064702],
[-0.34105372],
[-0.34105372],
[-0.34064702],
[-0.27961655],
[-0.34064702],
[-0.34064702],
[-0.27961655],
[-0.27961655],
[-0.27961655],
[-0.34064702],
[-0.27961655],
[-0.34064702],
[-0.34105372],
[-0.34064702],
[-0.34008337],
[-0.46459097],
[ 2.81395306],
[-0.27961655],
[-0.34064702],
[-0.34064702],
[-0.34064702],
[-0.27961655],
[-0.26145078]])

weights = np.ones(launch_angles.shape[0])
for i, _ in enumerate(launch_angles):
    if launch_angles[i][0] < -0.5 and launch_angles[i][0] > 0.5:
        weights[i] = -100

launch_angles_positive = np.abs(launch_angles)

launch_angles = np.sort(launch_angles, axis=0)
#pdb.set_trace()

fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
counts, bins = np.histogram(launch_angles, bins=20)
ax1.stairs(counts, bins, fill=True)

#ax2.hist(launch_angles_positive, bins=20)
#pdb.set_trace()

location, scale = laplace.fit(launch_angles)
print(location)
print(scale)
ax2.plot(launch_angles, laplace.pdf(launch_angles, loc=location, scale=scale), 'r-', lw=5, alpha=0.6, label='laplace pdf')

'''model = KernelDensity(bandwidth=1, kernel="exponential").fit(launch_angles, y=None, sample_weight=weights)
logprob = model.score_samples(launch_angles)
#ax2.scatter(launch_angles, np.exp(logprob))
ax2.fill_between(launch_angles.flatten(), np.exp(logprob))
#pdb.set_trace()
'''
'''bandwidth = np.arange(0.05, 2, 0.05)
model = KernelDensity(kernel="gaussian")
grid = GridSearchCV(model, {'bandwidth': bandwidth})
grid.fit(launch_angles)
model = grid.best_estimator_
logprob = model.score_samples(launch_angles)
#pdb.set_trace()
ax2.fill(launch_angles.flatten(), np.exp(logprob))'''

ax1.set_title("Histogram of Launch Angle Frequency (US)")
ax1.set_xlabel("Launch Angle (rad)")
ax1.set_ylabel("Frequency")

ax2.set_title("PDF of Launch Angles (US)")
ax2.set_xlabel("Launch Angle (rad)")
ax2.set_ylabel("Probability")
plt.show()
#pdb.set_trace()

'''
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
plt.subplot(121)
plt.scatter(np.arange(len(launch_angles)), launch_angles, c='red')
plt.xlabel('Sample no.')
plt.ylabel('Value')
plt.title('Scatter plot')
plt.subplot(122)
plt.hist(launch_angles, bins=20)
plt.title('Histogram')
fig.subplots_adjust(wspace=.3)
plt.show()

model = KernelDensity(bandwidth=1, kernel="gaussian")
model.fit(launch_angles)
logprob = model.score_samples(launch_angles)
#plt.scatter(launch_angles, np.exp(logprob))
#plt.plot(launch_angles, np.exp(logprob))
plt.fill_between(launch_angles.flatten(), np.exp(logprob))
plt.show()'''