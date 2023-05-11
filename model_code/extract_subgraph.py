from config import DefaultConfig
import networkx as nx
from haversine import haversine
import numpy as np
import pandas as pd
import pycountry_convert as pc

config = DefaultConfig()


def extract_subgraph_l3():
    df_node = pd.read_csv(config.l4_node_data_path)
    df_node.drop_duplicates(subset=df_node.columns, keep='last', inplace=True)
    print("node point number: ", df_node.shape[0])
    dict_node_coor = {}
    for index, row in df_node.iterrows():
        (x, y) = row['coordinates'].split(",")
        dict_node_coor[row['land_name']] = (float(y), float(x))
    # print(dict_node_coor)
    df_edge = pd.read_csv(config.l4_edge_data_path)
    # df_edge.drop_duplicates(subset=df_edge.columns, keep='last', inplace=True)
    # df_edge = df_edge.loc[~(df_edge['start_land_name'] == df_edge['end_land_name'])]
    list_all_point = df_edge['start_land_name'].to_list() + df_edge['end_land_name'].to_list()
    list_all_point = list(set(list_all_point))
    print("edge use point: ", len(list_all_point))

    # find not use point
    df_edge_point = pd.DataFrame(data=list_all_point)
    df_edge_point.columns = ["land_name"]
    df_no_use_node = pd.merge(df_edge_point, df_node, how='left', on=['land_name'])
    df_no_use_node = df_node.append(df_no_use_node).drop_duplicates(keep=False)
    print("df_no_use_node shape", df_no_use_node.shape[0])
    print(df_no_use_node)

    list_cable_id = list(set(df_edge['cable_id'].to_list()))
    print("edge cable number: ", len(list_cable_id))
    # list_cable_id = ['trans-pacific-express-tpe-cable-system']

    df_edge_group = df_edge.groupby('cable_id')
    for cable_id in list_cable_id:
        cable_edge_group = df_edge_group.get_group(cable_id)
        # print(cable_edge_group)
        list_all_point = cable_edge_group['start_land_name'].to_list() + cable_edge_group['end_land_name'].to_list()
        list_all_point = list(set(list_all_point))
        # print(list_all_point)
        list_vp_index = []
        list_land_index = []
        list_coor = []
        for point in list_all_point:
            point_index = list_all_point.index(point)
            list_coor.append(dict_node_coor[point])
            if point[0:2] == "vp":
                list_vp_index.append(point_index)
            else:
                list_land_index.append(point_index)
        # print(list_vp_index)
        # print(list_land_index)
        # print(list_coor)
        if list_vp_index != []:
            for vp_index in list_vp_index:
                temp_dis = 25000
                for land_index in list_land_index:
                    dis = haversine(list_coor[vp_index], list_coor[land_index])
                    # print(dis)
                    if dis < temp_dis:
                        near_land_index = land_index
                        temp_dis = dis
                # print(near_land_index)
                # print(list_all_point[vp_index])
                # print(list_all_point[near_land_index])
                df_edge.loc[df_edge["start_land_name"] == list_all_point[vp_index], "start_land_name"] = list_all_point[near_land_index]
                df_edge.loc[df_edge["end_land_name"] == list_all_point[vp_index], "end_land_name"] = list_all_point[near_land_index]
    print("not delete self to self: ", df_edge.shape[0])
    # df_edge.drop_duplicates(subset=df_edge.columns, keep='last', inplace=True)
    # print(df_edge.shape[0])
    df_edge = df_edge.loc[~(df_edge['start_land_name'] == df_edge['end_land_name'])]
    print("delete self to self: ", df_edge.shape[0])
    df_edge.to_csv(config.l3_edge_data_path, index=False)

    list_all_point = df_edge['start_land_name'].to_list() + df_edge['end_land_name'].to_list()
    list_all_point = list(set(list_all_point))
    # print(len(list_all_point))

    df_use_land = pd.DataFrame(data=list_all_point)

    df_use_land.columns = ["land_name"]
    df_sub_node = pd.merge(df_use_land, df_node, how='left', on=['land_name'])
    print("df_sub_node shape", df_sub_node.shape[0])
    df_sub_node.to_csv(config.l3_node_data_path, index=False)

# 从l3数据聚合


def extract_subgraph_l2():
    # 边：包括起始位置、海缆名字、带宽
    df_edge = pd.read_csv(config.l3_edge_data_path)

    df_node = pd.read_csv(config.l3_node_data_path)
    df_node.drop_duplicates(subset=df_node.columns, keep='last', inplace=True)
    print("node point number: ", df_node.shape[0])
    df_group_country = df_node.groupby(["country"])
    l2_node = []
    for df in df_group_country:
        # print(df[0])
        # cable最多的登陆点代表这个国家
        max_cable_number = df[1].loc[df[1]["cable_number"].idxmax()].to_list()
        # cable_number = df[1]["cable_number"].sum()
        l2_node.append(max_cable_number)
        # print(max_cable_number)
        list_all_country_land = df[1]['land_name'].to_list()
        # print(list_all_country_land)
        df_edge.loc[df_edge["start_land_name"].isin(list_all_country_land), "start_land_name"] = df[0]
        df_edge.loc[df_edge["end_land_name"].isin(list_all_country_land), "end_land_name"] = df[0]

    print("not delete self to self: ", df_edge.shape[0])
    df_edge = df_edge.loc[~(df_edge['start_land_name'] == df_edge['end_land_name'])]
    print("delete self to self: ", df_edge.shape[0])
    df_edge.to_csv(config.l2_edge_data_path, index=False)
    list_all_point = df_edge['start_land_name'].to_list() + df_edge['end_land_name'].to_list()
    list_all_point = list(set(list_all_point))
    print("edge use node: ", len(list_all_point))

    df_node = pd.DataFrame(data=l2_node)
    df_node.columns = ["old_land_name", 'coordinates', 'cable_number', 'land_name']
    print("node: ", df_node.shape[0])
    df_node.drop_duplicates(subset=df_node.columns, keep='last', inplace=True)
    print("node dup: ", df_node.shape[0])
    df_node[['coordinates', 'land_name']].to_csv(config.l2_node_data_path, index=False)


def country_to_continent(country_name):
    try:
        country_name = str(country_name.strip())
        country_alpha2 = pc.country_name_to_country_alpha2(country_name)
        country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
        return country_continent_name
    except:
        return 'none'

# 从l2数据聚合

def extract_subgraph_l1():
    # 边：包括起始位置、海缆名字、带宽
    df_edge = pd.read_csv(config.l2_edge_data_path)

    df_node = pd.read_csv(config.l2_node_data_path)
    df_node.drop_duplicates(subset=df_node.columns, keep='last', inplace=True)
    print("node point number: ", df_node.shape[0])
    for country_point in df_node['land_name'].to_list():
        continent = country_to_continent(country_point)
        if continent == 'none':
            if country_point.strip() in ['Ascension and Tristan da Cunha', 'Dem. Rep.', 'HI']:
                continent = "Africa"
            if country_point.strip() in ['Rep.', 'Virgin Islands (U.K.)', 'Virgin Islands (U.S.)']:
                continent = "North America"
            if country_point.strip() in ['Sint Eustatius and Saba', 'Sint Maarten']:
                continent = "Europe"
            if country_point.strip() in ['Timor-Leste', 'Sint Maarten']:
                continent = "Asia"
        df_edge.loc[df_edge["start_land_name"] == country_point, "start_land_name"] = continent
        df_edge.loc[df_edge["end_land_name"] == country_point, "end_land_name"] = continent
    print("not delete self to self: ", df_edge.shape[0])
    df_edge = df_edge.loc[~(df_edge['start_land_name'] == df_edge['end_land_name'])]
    print("delete self to self: ", df_edge.shape[0])
    df_edge.to_csv(config.l1_edge_data_path, index=False)


if __name__ == '__main__':
    extract_subgraph_l3()
    extract_subgraph_l2()
    extract_subgraph_l1()
