# 图数据挖掘
from networkx.algorithms import approximation as approx
import warnings
import re
import gzip
import networkx as nx
import numpy as np
import pandas as pd
# 数据可视化
import matplotlib.pyplot as plt
# plt.rcParams['font.sans-serif']=['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

warnings.simplefilter("ignore")


# ========================================构建图========================================
# fh = gzip.open("knuth_miles.txt.gz", "r")

G = nx.MultiGraph()
G.position = {}
# G.num_cable = {}

# 图节点：包括登陆点和虚拟点
df_node = pd.read_csv('/Data/My Drive/graph_code/data/node.csv')
df_node.drop_duplicates(subset=df_node.columns, keep='last', inplace=True)
df_node.drop_duplicates(subset=['land_name'], keep='last', inplace=True)
df_node

for idx, row in df_node.iterrows():  # 遍历表格的每一行
    G.add_node(row['land_name'])
    (x, y) = row['coordinates'].split(",")
    G.position[row['land_name']] = (float(x), float(y))
print(G.position)

# 边：包括起始位置、海缆名字、带宽
df_edge = pd.read_csv('/Data/My Drive/graph_code/data/edge.csv')
df_edge.drop_duplicates(subset=df_edge.columns, keep='last', inplace=True)
df_edge

for idx, row in df_edge.iterrows():  # 遍历表格的每一行
    G.add_edges_from([(row['start_land_name'], row['end_land_name'])], cable_name=row['cable_id'], band_width=row['band_width'])


# ========================================指标计算========================================
# -------------------------------- 1.可达国家
reachable_land_country = set()
reachable_country = set()
target_nodes = df_node[df_node['country'] == 'China']['land_name']
print(target_nodes)
for target_node in target_nodes:
    reachable_nodes = nx.descendants(G, target_node)
    for name in reachable_nodes:
        reachable_land_country.add(name)
for country in reachable_land_country:
    if country[:2] != 'vp':
        reachable_country.add(country[country.rfind(',') + 2:])

# ----------------------------------2.land_name_set
land_name_set = set()
xx = df_node['land_name']
for x in xx:
    if x[:2] != 'vp':
        land_name_set.add(x)
# print(sorted(land_name_set))
# print(len(land_name_set))

# ----------------------------------3.连通性
# 计算从节点 China 到节点 United States 的独立路径数
sources = set()
targets = set()
for x in land_name_set:
    if 'China' in x:
        sources.add(x)
    if 'States' in x:
        targets.add(x)
print(sources)
print(targets)

source = 'Chung Hom Kok, China'
# target = 'Point Hope, AK, United States'
target = 'Batangas, Philippines'
# for source in sources:
# for target in targets:
independent_paths = set()
paths = nx.all_simple_paths(G, source=source, target=target, cutoff=10)
sum = 0
for i in paths:
    sum += 1
    print(i)
print(sum)


# ----------------------------------4.独立路径


# 计算从节点 China 到节点 United States 的独立路径数
sources = set()
targets = set()
for x in land_name_set:
    if 'States' in x:
        sources.add(x)
    if 'China' in x:
        targets.add(x)
print(sources)
print(targets)

independent_paths = []

for source in sources:
    for target in targets:
        independent_paths.append(approx.local_node_connectivity(G, source, target))

print(independent_paths)

total_independent_paths = 0
for path in independent_paths:
    total_independent_paths += path
print(total_independent_paths)
