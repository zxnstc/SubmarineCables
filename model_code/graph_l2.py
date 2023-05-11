# 图数据挖掘
from config import DefaultConfig
import networkx as nx

import numpy as np
import pandas as pd

# 数据可视化
import matplotlib.pyplot as plt
# %matplotlib inline

# plt.rcParams['font.sans-serif']=['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

config = DefaultConfig()


def gen_graph():
    G = nx.MultiGraph()
    G.position = {}
    df_node = pd.read_csv(config.l2_node_data_path)
    print("df_node old: ", df_node.shape[0])
    df_node.drop_duplicates(subset=df_node.columns, keep='last', inplace=True)
    print("df_node dup: ", df_node.shape[0])
    # df_node.drop_duplicates(subset=['land_name'], keep='last', inplace=True)
    # print(df_node.shape[0])
    df_node_land = df_node[df_node['land_name'].str.startswith('vp') != True]
    print("df_node land point: ", df_node_land.shape[0])

    for idx, row in df_node.iterrows():  # 遍历表格的每一行
        # G.add_node(row['land_name'],
        #            cable_number=row["cable_number"], country=row['country'])
        G.add_node(row['land_name'])
        (x, y) = row['coordinates'].split(",")
        G.position[row['land_name']] = (float(x), float(y))

    # 边：包括起始位置、海缆名字、带宽
    df_edge = pd.read_csv(config.l2_edge_data_path)
    print("df_edge old: ", df_edge.shape[0])
    list_edge_point = df_edge['start_land_name'].to_list() + df_edge['end_land_name'].to_list()
    list_edge_point = list(set(list_edge_point))
    print("edge point: ", len(list_edge_point))
    # df_edge.drop_duplicates(subset=df_edge.columns, keep='last', inplace=True)
    # print("df_edge dup column: ", df_edge.shape[0])
    df_edge = df_edge.loc[~(df_edge['start_land_name'] == df_edge['end_land_name'])]
    print("df_edge delete self to self: ", df_edge.shape[0])
    list_edge_point = df_edge['start_land_name'].to_list() + df_edge['end_land_name'].to_list()
    list_edge_point = list(set(list_edge_point))
    print("edge point delete self to self: ", len(list_edge_point))
    num_point = 0
    use_land_point = []
    for point in list_edge_point:
        if point[0:2] == "vp":
            num_point = num_point + 1
        else:
            use_land_point.append(point)
    print("edge vp point delete self to self:", num_point)
    print("edge land point delete self to self:", len(use_land_point))

    df_use_land = pd.DataFrame(data=use_land_point)
    df_use_land.columns = ["land_name"]
    df_use_land_point = pd.merge(df_use_land, df_node_land, how='left', on=['land_name'])
    df_miss_land = df_node_land.append(df_use_land_point).drop_duplicates(keep=False)
    print(df_miss_land)

    for idx, row in df_edge.iterrows():  # 遍历表格的每一行
        G.add_edges_from([(row['start_land_name'], row['end_land_name'])],
                         cable_name=row['cable_id'], band_width=row['band_width'])
    print(G)
    return G


def plot_graph_l2(G):

    # 节点颜色-节点度
    # node_color = [float(G.degree(v)) for v in G]
    node_color = []
    node_size = []
    alpha = []
    for v in G:
        node_size.append(50*G.degree(v))
        if v == ' China':
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
        node_shape='o',
        alpha=alpha,
        with_labels=False,
    )
    # plt.show()
    plt.savefig('./result/L2_one_graph.jpg')

class L2Indicator:
    @staticmethod
    def l2_pagerank(G):
        #计算节点重要度  自动转化为双向图
        pagerank = nx.pagerank(G,alpha=0.8)
        # 获取排名前五的节点
        top_nodes = sorted(pagerank, key=pagerank.get, reverse=True)[:5]
        # 打印排名前五的节点
        print("Top 5 nodes:")
        for node in top_nodes:
            print("Node:", node, "PageRank Score:", pagerank[node])

    @staticmethod
    #计算连通性(可达国家数) 连通率（占总的）
    def l2_connectivity(G,country_name):
        num_nodes = G.number_of_nodes()
        print("所有国家数量：", num_nodes)
        # 计算可达国家数
        reachable_nodes = nx.descendants(G, country_name)
        print("可达国家数量：", len(reachable_nodes))
        print("可达国家：", reachable_nodes)
        # 计算连通率
        connectivity = (len(reachable_nodes)+1) / num_nodes
        print("连通率：", connectivity)


def calculate_l2_indicator(G):
    # L2Indicator.l2_pagerank(G)
    L2Indicator.l2_connectivity(G,' China')

def main_l2():
    G = gen_graph()
    # plot_graph_l2(G)
    calculate_l2_indicator(G)


if __name__ == '__main__':
    main_l2()

    # extract_subgraph_l3()
    # extract_subgraph_l2()
    # extract_subgraph_l1()
