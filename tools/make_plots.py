#%% import libraries
import pandas as pd 
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import cmasher as cmr
import sys,json

#%% plot setup
sns.set(rc={'figure.figsize':(11.7,6.27)})
plt.rcParams.update({'font.size': 16})
sns.set(font_scale=1.5)
sns.set_style("whitegrid")

#%% set colors
# TODO change colors!
colors = ['#7ea6e0','#f19c99','#9c99f1','#99f19c']
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", colors)
#%%
data = json.load(sys.stdin)
system = data['metadata']['system']
backend = data['metadata']['backend']
#%% read DataFrame 
df = pd.DataFrame(data['results'])
# clean data
algorithm_names = {'a_star':  'A*', 'a_star_cloud' : 'Cloud A*', 'ca_star':'CA*', 'ca_star_cloud': 'Cloud CA*'}
df['Algorithms'] = df['algo_name'].map(algorithm_names)
df.drop('algo_name', axis = 1, inplace = True)
#%% plot log
color_ = cmr.take_cmap_colors(cmap, len(df['Algorithms'].unique()), return_fmt='hex')
palette = dict(zip(list(df['Algorithms'].unique()), color_ ))
plot1 = df.loc[df['Algorithms'].isin(['CA*', 'Cloud CA*'])]
plot1.reset_index(drop = True, inplace = True )
plot2 = df.loc[df['Algorithms'].isin(['A*', 'Cloud A*'])]
plot2.reset_index(drop = True, inplace = True )
fig, (ax, ax1) = plt.subplots(2,1)
ax = sns.lineplot(data = plot2, y = 'time', x = 'map_name', hue = 'Algorithms', linewidth = 4, palette = palette, ax =ax)
ax.set_ylabel('Time [ms]')
ax.set_xlabel(None)
ax.set(yscale="log")
ax.legend(loc='upper left')
ax1 = sns.lineplot(data = plot1, y = 'time', x = 'map_name', hue = 'Algorithms', linewidth = 4, palette = palette, ax = ax1)
ax1.set_ylabel('Time [ms]')
ax1.set_xlabel(None)
ax1.set(yscale="log")
ax1.legend(loc='upper left')
leg = ax.legend()
# change the line width for the legend
for line in leg.get_lines():
    line.set_linewidth(4)
leg = ax1.legend()
# change the line width for the legend
for line in leg.get_lines():
    line.set_linewidth(4)
plt.tight_layout()
plt.savefig(f'{system}_{backend}_MapName_Algorithms_LOG.png', bbox_inches='tight')
#%% plot linear
fig, (ax, ax1) = plt.subplots(2,1)
ax = sns.lineplot(data = plot2, y = 'time', x = 'map_name', hue = 'Algorithms', linewidth = 4, palette = palette, ax =ax)
ax.set_ylabel('Time [ms]')
ax.set_xlabel(None)
ax.legend(loc='upper left')
ax1 = sns.lineplot(data = plot1, y = 'time', x = 'map_name', hue = 'Algorithms', linewidth = 4, palette = palette, ax = ax1)
ax1.set_ylabel('Time [ms]')
ax1.set_xlabel(None)
ax1.legend(loc='upper left')
leg = ax.legend()
# change the line width for the legend
for line in leg.get_lines():
    line.set_linewidth(4)
leg = ax1.legend()
# change the line width for the legend
for line in leg.get_lines():
    line.set_linewidth(4)
plt.tight_layout()
plt.savefig(f'{system}_{backend}_MapName_Algorithms_LINEAR.png', bbox_inches='tight')
#%% plot 
fig, ((ax, ax1), (ax2, ax3)) = plt.subplots(2,2)
ax = sns.barplot(data = df, x = 'Algorithms', y = 'time', errorbar = 95, ax = ax, palette = palette)
ax.set_ylabel('Time [ms]')
ax.set_xlabel(None)
ax.set(yscale="log")

ax1 = sns.barplot(data = df, x = 'num_of_paths_found', y = 'Algorithms', ax = ax1, errorbar=None, palette = palette)
ax1.set_ylabel(None)
ax1.set_xlabel('Number of path found')

ax2 = sns.swarmplot(data = df, x = 'Algorithms', y = 'percentage_of_paths_found', ax = ax2, palette = palette)
ax2.set_ylabel('Percentage of paths found [%]')
ax2.set_xlabel(None)

ax3 = sns.lineplot(data = df, x = 'Algorithms', y = 'sum_of_paths_length', linewidth = 4, ax = ax3, color = colors[0])
ax3.set_ylabel('Sum of path length')
ax3.set_xlabel(None)

plt.tight_layout()
plt.savefig(f'{system}_{backend}_Algorithms_subplot.png', bbox_inches='tight')