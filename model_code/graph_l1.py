# 图数据挖掘
from config import DefaultConfig
import networkx as nx
from networkx.algorithms import approximation as approx
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
    df_node = pd.read_csv(config.l1_node_data_path)
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
    df_edge = pd.read_csv(config.l1_edge_data_path)
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


def plot_graph_l1(G):

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
        node_shape='o',
        alpha=alpha,
        with_labels=False,
    )
    # plt.show()
    plt.savefig('./result/L1_one_graph.jpg')


class L1Indicator_area:
    @staticmethod
    def l1_pagerank(G):
        # 计算节点重要度  自动转化为双向图
        pagerank = nx.pagerank(G, alpha=0.8)
        # 获取排名前五的节点
        top_nodes = sorted(pagerank, key=pagerank.get, reverse=True)[:5]
        # 打印排名前五的节点
        print("Top 5 nodes:")
        for node in top_nodes:
            print("Node:", node)

    @staticmethod
    # 计算连通性(可达区域数) 连通率（占总的）
    def l2_connectivity(G, country_name):
        num_nodes = G.number_of_nodes()
        print("所有区域数量：", num_nodes)
        # 计算可达国家数
        reachable_nodes = nx.descendants(G, country_name)
        print("可达区域数量：", len(reachable_nodes))
        print("可达区域：", reachable_nodes)
        # 计算连通率
        connectivity = len(reachable_nodes) / num_nodes
        print("连通率：", connectivity)

    @staticmethod
    # 计算区域间连通性
    def l1_connect_uv(G, source, target):
        paths = nx.all_simple_paths(G, source=source, target=target, cutoff=5)
        sum = 0
        for i in paths:
            sum += 1
        print(source, "到", target, "的路径数：", sum)
        return sum

    @staticmethod
    # 计算路径可靠性
    def l1_independent_path(G, source, target):
        independent_paths = approx.local_node_connectivity(G, source, target)
        total_independent_paths = 0
        for path in independent_paths:
            total_independent_paths += path
        print(source, "到", target, "的独立路径数：", total_independent_paths)
        return total_independent_paths


class L1Indicator_between_area:
    @staticmethod
    def country_to_continent(country_name):
        try:
            country_name = str(country_name.strip())
            country_alpha2 = pc.country_name_to_country_alpha2(country_name)
            country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
            country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
            return country_continent_name
        except:
            return 'none'

    @staticmethod
    def df_with_continent(file_name):
        df = pd.read_csv(file_name)
        df['continent'] = df['country'].apply(L1Indicator.country_to_continent)
        return df

    @staticmethod
    # 总登陆点个数
    def landing_point_sum(continent_name):
        df_node = L1Indicator.df_with_continent(config.l3_node_data_path)
        df_node.drop_duplicates(subset=df_node.columns, keep='last', inplace=True)
        df_node_continent = df_node[df_node['continent'] == continent_name]
        print("df_node land point: ", df_node_continent.shape[0])
        print("df_node land point: ", df_node_continent)
        return df_node_continent.shape[0]

    @staticmethod
    # 对内对外登陆点、海缆、带宽
    # 遍历亚洲所有登陆点➡️找到这个登陆点所在海缆（edge.csv)➡️遍历这根海缆上所有登陆点：
    # 1.如果有一个登录点是在其他洲===对外登陆点、对外海缆、带宽
    # 2.所有登陆点都在这个洲内===对内登陆点、对内海缆、带宽
    def inside_out(continent_name):
        inside_landing_set = set()
        outside_landing_set = set()
        inside_cable_set = set()
        outside_cable_set = set()
        inside_bandwidth_list = []
        outside_bandwidth_list = []

        df_node = L1Indicator.df_with_continent(config.l3_node_data_path)
        df_node.drop_duplicates(subset=df_node.columns, keep='last', inplace=True)
        # df_node_country存储这个洲所有登陆点（格式：node.csv行拼接）
        df_node_continent = df_node[df_node['continent'] == continent_name]
        # print(df_node_country)
        df_edge = pd.read_csv(config.l3_edge_data_path)
        df_edge.drop_duplicates(subset=df_edge.columns, keep='last', inplace=True)
        # df_edge_continent存储的是所有涉及到这个洲的海缆（格式：edge.csv行拼接）
        df_edge_continent = pd.concat([df_edge[df_edge['start_land_name'].isin(df_node_continent['land_name'])],
                                      df_edge[df_edge['end_land_name'].isin(df_node_continent['land_name'])]])

        print(df_edge_continent)

        # 遍历这些涉及到亚洲的海缆（海缆id存储在cable_id_set）
        # 如果有一个登录点是在其他洲===对外海缆➡️上面所有亚洲的登陆点都是对外登陆点
        # 如果所有登陆点都在这个洲内===对内海缆➡️上面所有亚洲的登陆点都是对内登陆点
        cable_id_set = set(df_edge_continent['cable_id'])
        print("cable_id_set: ", len(cable_id_set))
        print("cable_id_set: ", cable_id_set)
        for cable_id in cable_id_set:
            # print("cable_id: ", cable_id)
            df_cable = df_edge[df_edge['cable_id'] == cable_id]
            # print("df_cable: ", df_cable)
            # print("df_cable: ", df_cable.shape[0])
            # print("df_cable: ", df_cable['start_land_name'].values[0])
            # print("df_cable: ", df_cable['end_land_name'].values[0])
            # print("df_cable: ", df_cable['start_land_name'].values[0].split(",")[-1])
            # print("df_cable: ", df_cable['end_land_name'].values[0].split(",")[-1])

            for index, row in df_cable.iterrows():
                start_continent = L1Indicator.country_to_continent(row['start_land_name'].split(",")[-1])
                end_continent = L1Indicator.country_to_continent(row['end_land_name'].split(",")[-1])
                if start_continent != continent_name or start_continent != continent_name:
                    outside_cable_set.add(cable_id)
                    # print(df_cable['start_land_name'].values,type(df_cable['start_land_name'].values))
                    # print(set(df_cable['start_land_name'].values.tolist()))
                    outside_landing_set = outside_landing_set.union(set(df_cable['start_land_name'].values.tolist()))
                    # print("outside_landing_set: ", outside_landing_set)
                    outside_landing_set = outside_landing_set.union(df_cable['end_land_name'].values.tolist())
                    # print("outside_landing_set: ", outside_landing_set)
                    outside_bandwidth_list.append(df_cable['band_width'].values[0])
                    # print("outside_bandwidth_list: ", outside_bandwidth_list)
                    break
            # print("==============================================================")
        for landing in outside_landing_set.copy():
            landing_continent = L1Indicator.country_to_continent(landing.split(",")[-1])
            if landing_continent != continent_name:
                outside_landing_set.remove(landing)
        # 输出对外信息
        print("对外海缆集合: ", outside_cable_set)
        print("对外海缆数量: ", len(outside_cable_set))
        print("对外登陆点", outside_landing_set)
        print("对外登陆点数量: ", len(outside_landing_set))
        print("对外带宽", outside_bandwidth_list)
        outside_bandwidth_sum = 0
        for bandwidth in outside_bandwidth_list:
            outside_bandwidth_sum += bandwidth
        print("对外带宽总和", outside_bandwidth_sum)

        # 处理inside
        inside_cable_set = cable_id_set-outside_cable_set
        for inside_cable in inside_cable_set:
            df_cable = df_edge[df_edge['cable_id'] == inside_cable]
            inside_landing_set = inside_landing_set.union(set(df_cable['start_land_name'].values.tolist()))
            inside_landing_set = inside_landing_set.union(set(df_cable['end_land_name'].values.tolist()))
            inside_bandwidth_list.append(df_cable['band_width'].values[0])
        # 输出对内信息
        print("对内海缆集合: ", inside_cable_set)
        print("对内海缆数量: ", len(inside_cable_set))
        print("对内登陆点", inside_landing_set)
        print("对内登陆点数量: ", len(inside_landing_set))
        print("对内海缆带宽列表: ", inside_bandwidth_list)
        inside_bandwidth_sum = 0
        for bandwidth in inside_bandwidth_list:
            inside_bandwidth_sum += bandwidth
        print("对内海缆总带宽: ", inside_bandwidth_sum)


def main_l1():
    G = gen_graph()
    # plot_graph_l1(G)
    L1Indicator_area.landing_point_sum('Asia')
    L1Indicator_area.inside_out('Asia')
    L1Indicator_between_area.l1_pagerank(G)
    L1Indicator_between_area.l2_connectivity(G, 'Asia')


if __name__ == '__main__':
    main_l1()

    # extract_subgraph_l3()
    # extract_subgraph_l2()
    # extract_subgraph_l1()
