#%%
from pythonping import ping
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
#%% ping responsen 
N = 210
response_list = ping('cloud-broker-mactat.cloud.okteto.net', size=40, count=N)
responses = response_list._responses
time = [res.time_elapsed_ms for res in responses]
#%% setup plot
colors = ['#7ea6e0','#f19c99','#9c99f1','#99f19c']
sns.set(rc={'figure.figsize':(11.7,6.27)})
plt.rcParams.update({'font.size': 16})
sns.set(font_scale=2)
sns.set_style("whitegrid")
#%% plot responses
def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w
avg_points = 10
time_avg = moving_average(time, 10)
fig, ax = plt.subplots(1,1)
ax = sns.lineplot(y = time_avg, x = (np.arange(0,N-avg_points+1)+1), linewidth = 4, color = colors[0])
ax.hlines(np.mean(time_avg), xmin = 0, xmax = 200, color = colors[1], label = 'Mean time', lw = 4, linestyles='--')
ax.set_ylabel('Response time [ms]')
ax.set_xlabel('Ping')
plt.legend()
plt.tight_layout()
plt.savefig(f'ResponseTime.png', bbox_inches='tight')