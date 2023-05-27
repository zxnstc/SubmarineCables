import csv
import os
import pandas as pd
from config import DefaultConfig

config=DefaultConfig()

df_node = pd.read_csv(config.l4_node_data_path)
df_node.drop_duplicates(subset=df_node.columns, keep='last', inplace=True)
df_node_virtual = df_node[df_node['land_name'].str.startswith('vp') == True]
df_node_180=df_node_virtual[df_node_virtual['coordinates'].str.contains("180")]

df_edge=pd.read_csv(config.l4_edge_data_path)
df_edge.drop_duplicates(subset=df_edge.columns, keep='last', inplace=True)


for index,node in df_node_180.iterrows():
    node_name=node[1]
    print(node_name)
    df_edge_180=df_edge.loc[df_edge["start_land_name"] == node_name]
    df_edge_180=df_edge_180.append(df_edge.loc[df_edge["end_land_name"] == node_name])
    df_edge_copy=df_edge_180.copy()
    print(df_edge_180)   
    landset=set(df_edge_180['start_land_name'].to_list()+df_edge_180['end_land_name'].to_list())
    print(landset)
    landset.remove(node_name)
    landlist=list(landset)
    print(landlist)
    edge_new=df_edge_180.iloc[0].copy()
    print(edge_new)
    edge_new['start_land_name']=landlist[0]
    edge_new['end_land_name']=landlist[1]
    edge_new['cable_id']=df_edge_copy['cable_id'].to_list()[0]
    edge_new['band_width']=df_edge_copy['band_width'].to_list()[0]

    print(edge_new)


    #在df_edge中删除df_edge_180
    df_edge=df_edge.append(df_edge_180).drop_duplicates(keep=False)
    #在df_edge中添加合并后的边
    df_edge=df_edge.append(edge_new,ignore_index=True)

    #在df_node中删除df_node_180
    df_node=df_node.append(df_node_180).drop_duplicates(keep=False)

df_node.to_csv('./l4_node_without180.csv', index=False)
df_edge.to_csv('./l4_edge_without180.csv', index=False)


