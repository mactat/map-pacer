#%% import libraries
import pandas as pd 
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import cmasher as cmr
import sys,json
import glob
import argparse
#%% plot setup
sns.set(rc={'figure.figsize':(11.7,6.27)})
sns.set(font_scale=2)
sns.set_style("whitegrid")

#%% set colors
colors = ['#7ea6e0','#f19c99','#9c99f1','#99f19c']
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", colors)
#%% load data 
files = []

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, default='./perf/cpu*', help='path to the folder with results')
args = parser.parse_args()
print(f"Path: {args.path}")

folders = glob.glob(args.path)
print(f"Found {len(folders)} folders")
for folder in folders:
    with open(f'{folder}/res.json') as f:
        files.append(json.load(f))

#%%
system = [data['metadata']['system'] for data in files]
backend = [data['metadata']['backend'] for data in files]
#%% read DataFrame 
names = [file.split('\\')[-1] for file in folders]
df = [pd.DataFrame(data['results']) for data in files]
for i,d in enumerate(df):
    d['profile'] = str(names[i])
df = pd.concat(df, axis = 0)
df.reset_index(drop = True, inplace = True)
algorithm_names = {'a_star':  'A*', 'a_star_cloud' : 'Cloud A*', 'ca_star':'CA*', 'ca_star_cloud': 'Cloud CA*'}
df['Algorithms'] = df['algo_name'].map(algorithm_names)
df.drop('algo_name', axis = 1, inplace = True)
profile_names = list(df['profile'].unique())
rename_profile = ['Very low profile', 'Low profile', 'Medium profile', 'High profile']
profile_names = dict(zip(profile_names, rename_profile ))
df['profile'] = df['profile'].map(profile_names)

#%%
color_ = cmr.take_cmap_colors(cmap, len(df['Algorithms'].unique()), return_fmt='hex')
palette = dict(zip(list(df['Algorithms'].unique()), color_ ))

fig, (ax) = plt.subplots(1,1)
ax = sns.barplot(data = df, y = 'percentage_of_paths_found', x = 'profile', hue = 'Algorithms', palette = palette, ax =ax)
ax.set_ylabel('Percent of found paths [%]')
ax.set_xlabel(None)
plt.setp(ax.get_xticklabels(), rotation = 25)
sns.move_legend(ax, "upper center", bbox_to_anchor=(0.5, 1.3), ncol = 4)
# save figure
fig.savefig('compare_profiles.png', dpi = 300, bbox_inches = 'tight')

#%%
fig, (ax) = plt.subplots(1,1)
ax= sns.pointplot(data = df, y = 'num_of_paths_found', x = 'profile', hue = 'Algorithms', errorbar=None, ax = ax, palette = palette)
ax.set_ylabel('Number of found paths ')
ax.set_xlabel(None)
plt.setp(ax.get_xticklabels(), rotation = 25)
sns.move_legend(ax, "upper center", bbox_to_anchor=(0.5, 1.2), ncol = 4)
# save figure
fig.savefig('compare_profiles_num_of_paths.png', dpi = 300, bbox_inches = 'tight')


#%% Log plot
fig, (ax) = plt.subplots(1,1)
ax = sns.barplot(data = df, y = 'time', x = 'profile', hue = 'Algorithms', errorbar=None, ax = ax, palette = palette, linewidth = 4)
ax.set_ylabel('Time [ms] ')
ax.set_xlabel(None)
plt.setp(ax.get_xticklabels(), rotation = 25)
ax.set(yscale="log")
sns.move_legend(ax, "upper center", bbox_to_anchor=(0.5, 1.2), ncol = 4)
# save figure
fig.savefig('compare_profiles_log.png', dpi = 300, bbox_inches = 'tight')
