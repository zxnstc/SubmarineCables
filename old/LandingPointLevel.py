# 图数据挖掘
import networkx as nx

import numpy as np
import pandas as pd

# 数据可视化
import matplotlib.pyplot as plt

# plt.rcParams['font.sans-serif']=['SimHei']  # 用来正常显示中文标签  
plt.rcParams['axes.unicode_minus']=False  # 用来正常显示负号
import gzip
import re

import warnings
warnings.simplefilter("ignore")


G = nx.MultiGraph()
G.position = {}

# 图节点：包括登陆点和虚拟点
df_node = pd.read_csv('/Data/My Drive/graph_code/data/LandingPoints.csv')
df_node.drop_duplicates(subset = df_node.columns,keep='last',inplace=True)
df_node.drop_duplicates(subset = ['continent'],keep='last',inplace=True)
df_node

for idx, row in df_node.iterrows(): # 遍历表格的每一行
    G.add_node(row['continent'])
    (x, y) = row['coordinates'].split(",")
    G.position[row['continent']] = (float(x), float(y))

# 边：包括起始位置、海缆名字、带宽
df_edge = pd.read_csv('/Data/My Drive/graph_code/data/LandingPointsEdge.csv')
df_edge.drop_duplicates(subset = df_edge.columns,keep='last',inplace=True)
df_edge

for idx, row in df_edge.iterrows(): # 遍历表格的每一行
    G.add_edges_from([(row['start_land_name'], row['end_land_name'])], cable_name=row['cable_id'])

# 节点颜色-节点度
# node_color = [float(G.degree(v)) for v in G]
node_color = []
node_size = []
alpha = []
for v in G:
    node_size.append(50*G.degree(v))
    if v == 'Asia':
        node_color.append('r')
        alpha.append(1)
    else:
        node_color.append('purple')
        alpha.append(1)


fig = plt.figure(figsize=(32, 16))
nx.draw(
    G,
    G.position,
    node_size=node_size,
    node_color=node_color,
    edgecolors='purple',
    node_shape = 'o',
    alpha = alpha,
    with_labels=False,
)
plt.show()