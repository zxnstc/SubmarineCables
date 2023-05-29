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


class L2Indicator_country:
    @staticmethod
    # 总登陆点个数
    def landing_point_sum(country_name):
        df_node = pd.read_csv(config.l3_node_data_path)
        df_node.drop_duplicates(subset=df_node.columns, keep='last', inplace=True)
        df_node_country = df_node[df_node['country'] == country_name]
        print("df_node land point: ", df_node_country.shape[0])
        return df_node_country.shape[0]

    @staticmethod
    # 对内对外登陆点、海缆、带宽
    # 遍历中国所有登陆点➡️找到这个登陆点所在海缆（edge.csv)➡️遍历这根海缆上所有登陆点：
    # 1.如果有一个登录点是在其他国家===对外登陆点、对外海缆、带宽
    # 2.所有登陆点都在这个国家内===对内登陆点、对内海缆、带宽
    def inside_out(country_name):
        inside_landing_set = set()
        outside_landing_set = set()
        inside_cable_set = set()
        outside_cable_set = set()
        inside_bandwidth_list = []
        outside_bandwidth_list = []

        df_node = pd.read_csv(config.l3_node_data_path)
        df_node.drop_duplicates(subset=df_node.columns, keep='last', inplace=True)
        # df_node_country存储这个国家所有登陆点（格式：node.csv行拼接）
        df_node_country = df_node[df_node['country'] == country_name]
        # print(df_node_country)
        df_edge = pd.read_csv(config.l3_edge_data_path)
        df_edge.drop_duplicates(subset=df_edge.columns, keep='last', inplace=True)
        # df_edge_country存储的是所有涉及到这个国家的海缆（格式：edge.csv行拼接）
        df_edge_country = pd.concat([df_edge[df_edge['start_land_name'].isin(df_node_country['land_name'])],
                                    df_edge[df_edge['end_land_name'].isin(df_node_country['land_name'])]])

        # print(df_edge_country)

        # 遍历这些涉及到中国的海缆（海缆id存储在cable_id_set）
        # 如果有一个登录点是在其他国家===对外海缆➡️上面所有中国的登陆点都是对外登陆点
        # 如果所有登陆点都在这个国家内===对内海缆➡️上面所有中国的登陆点都是对内登陆点
        cable_id_set = set(df_edge_country['cable_id'])
        # print("cable_id_set: ", len(cable_id_set))
        # print("cable_id_set: ", cable_id_set)
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
                if row['start_land_name'].split(",")[-1] != country_name or row['end_land_name'].split(",")[-1] != country_name:
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
            if landing.split(",")[-1] != country_name:
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

        return len(outside_landing_set), len(outside_cable_set), outside_bandwidth_sum, len(inside_landing_set), len(inside_cable_set), \
            inside_bandwidth_sum


class L2Indicator_between_country:
    @staticmethod
    def l2_pagerank(G):
        # 计算节点重要度  自动转化为双向图
        pagerank = nx.pagerank(G, alpha=0.8)
        # 获取排名前五的节点
        top_nodes = sorted(pagerank, key=pagerank.get, reverse=True)[:5]
        # all_nodes = sorted(pagerank, key=pagerank.get, reverse=True)
        # 打印排名前五的节点
        print("Top 5 nodes:")
        for node in top_nodes:
            print("Node:", node, "PageRank Score:", pagerank[node])
        return pagerank

    @staticmethod
    # 计算连通性(可达国家数) 连通率（占总的）
    def l2_connectivity(G, country_name):
        num_nodes = G.number_of_nodes()
        print("所有国家数量：", num_nodes)
        # 计算可达国家数
        reachable_nodes = nx.descendants(G, country_name)
        print("可达国家数量：", len(reachable_nodes))
        print("可达国家：", reachable_nodes)
        # 计算连通率
        connectivity = (len(reachable_nodes)+1) / num_nodes
        print("连通率：", connectivity)
        return len(reachable_nodes), connectivity

    @staticmethod
    # 计算区域间连通性
    def l2_connect_uv(G, source, target):
        paths = nx.all_simple_paths(G, source=source, target=target, cutoff=10)
        sum = 0
        for i in paths:
            sum += 1
        print(source, "到", target, "的路径数：", sum)
        return sum

    @staticmethod
    # 计算路径可靠性
    def l2_independent_path(G, source, target):
        independent_paths = approx.local_node_connectivity(G, source, target)
        total_independent_paths = 0
        for path in independent_paths:
            total_independent_paths += path
        print(source, "到", target, "的独立路径数：", total_independent_paths)
        return total_independent_paths


def sat_country_indicator(G):
    df_node = pd.read_csv(config.l2_node_data_path)
    all_country = df_node['land_name'].to_list()
    pagerank = L2Indicator_between_country.l2_pagerank(G)
    record_list = []
    for country in all_country:

        # 资源占有类
        landing_point_sum = L2Indicator_country.landing_point_sum(country)
        outside_land, outside_cable, outside_bw, inside_land, inside_cable, inside_bw = L2Indicator_country.inside_out(country)

        # 连通性类
        connected_country, connectivity = L2Indicator_between_country.l2_connectivity(G, country)
        pagerank_score = pagerank[country]

        record_list.append([country, landing_point_sum, outside_land, outside_cable, outside_bw, inside_land,
                            inside_cable, inside_bw, connected_country, connectivity, pagerank_score])
    df_record = pd.DataFrame(data=record_list)
    df_record.columns = ['country', 'landing_point_sum', 'outside_land', 'outside_cable', 'outside_bw', 'inside_land',
                         'inside_cable', 'inside_bw', 'connected_country', 'connectivity', 'pagerank_score']
    df_record.to_csv(config.l2_result_path + 'sat_country_indicator.csvclear', index=False)


def main_l2():

    # 基于L3数据统计
    # L2Indicator_country.landing_point_sum(' China')
    # L2Indicator_country.inside_out(' China')

    G = gen_graph()
    sat_country_indicator(G)
    # plot_graph_l2(G)
    # 总登陆点个数
    # L2Indicator_between_country.l2_pagerank(G)
    # L2Indicator_between_country.l2_connectivity(G, ' China')


if __name__ == '__main__':
    main_l2()
