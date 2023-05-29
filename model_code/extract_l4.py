import json
import os
import csv
import operator
import random
import pycountry_convert as pc
from config import DefaultConfig
import pandas as pd

config = DefaultConfig()

with open(config.cable_geo_data_path, "r", encoding="utf-8") as f1:
    line_dict=json.load(f1)

class RawDataProcess:
    @staticmethod
    def one_decimal_cable():
        with open(config.cable_geo_data_path, "r", encoding="utf-8") as f1:
            line_dict=json.load(f1)

        for index1,value1 in enumerate(line_dict["features"]):
            # list_cable为一个种类的海缆
            list_line=line_dict["features"][index1]["geometry"]["coordinates"]
            for singleline in list_line:
                for point in singleline:
                    point[0]=round(point[0],1)
                    point[1]=round(point[1],1)
                    if point[0]==-180.0:
                        point[0]=180.0
                    if point[1]==-180.0:
                        point[1]=180.0
                    point[0]=round(point[0],1)
                    point[1]=round(point[1],1)


        with open(config.cable_geo_data_path, 'w') as f:
            json.dump(line_dict, f)

    @staticmethod
    def one_decimal_land():
        with open(config.landing_point_data_path, "r", encoding="utf-8") as f1:
            line_dict=json.load(f1)

        for index1,value1 in enumerate(line_dict["features"]):
            landing_point=line_dict["features"][index1]["geometry"]["coordinates"]
            landing_point[0]=round(landing_point[0],1)
            landing_point[1]=round(landing_point[1],1)
            if landing_point[0]==-180.0:
                landing_point[0]=180.0
            if landing_point[1]==-180.0:
                landing_point[1]=180.0
            landing_point[0]=round(landing_point[0],1)
            landing_point[1]=round(landing_point[1],1)


        with open(config.landing_point_data_path, 'w') as f:
            json.dump(line_dict, f)



def country_to_continent(land_name):
  try:
    land_point_name_list=land_name.split(",")
    if len(land_point_name_list)==2:
      country_name=land_point_name_list[1]
    else:
      country_name=land_point_name_list[2]
    country_name=str(country_name.strip())
    country_alpha2 = pc.country_name_to_country_alpha2(country_name)
    country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
    country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
    return country_continent_name
  except:
    return 'none'
  
def extract_virtual_points(cable_all_points):
    
    virtual_points = []
    list1 = []
    for point in cable_all_points:
        if cable_all_points.count(point) > 1:
            list1.append(point)
    if list1 == []:
        print("no virtual points")
    else:
        for list2 in list1:
            if list2 not in virtual_points:
                virtual_points.append(list2)
    return virtual_points

def findfiles(cable_id):
    path=config.cable_file_path
    files_name = os.listdir(path)
    for file_name in files_name:
        if cable_id in file_name:
            return file_name

def find_land_points_name(file_name):
    land_points_name_list=[]
    with open(config.cable_file_path+file_name, "r", encoding="utf-8") as f1:
        line_dict=json.load(f1)
    for land_point in line_dict["landing_points"]:
        land_point_name=land_point["name"]
        land_points_name_list.append(land_point_name)
    return land_points_name_list

def find_cable_attributes(file_name):
    with open(config.cable_file_path+file_name, "r", encoding="utf-8") as f1:
        line_dict=json.load(f1)
    cable_length=line_dict["length"]
    cable_owners=line_dict["owners"]
    cable_suppliers=line_dict["suppliers"]
    cable_rfs=line_dict["rfs"]
    cable_rfs_year=line_dict["rfs_year"]
    cable_is_planned=line_dict["is_planned"]
    return cable_length,cable_owners,cable_suppliers,cable_rfs,cable_rfs_year,cable_is_planned


def find_land_points_coordinates(land_poins_name_list):
    with open(config.landing_point_data_path, "r", encoding="utf-8") as f1:
        land_points_dict=json.load(f1)
    land_points_coordinates_dict={}
    for land_point in land_points_dict["features"]:
        if land_point["properties"]["name"] in land_poins_name_list:
            land_points_coordinates_dict[str(land_point['geometry']['coordinates'])]=land_point["properties"]["name"]
    return land_points_coordinates_dict


land_set=set()
land_set2=set()
cable_num_dict={} #cable_num_dict{land_point_name:num}
files_name = os.listdir(config.cable_file_path)
for file_name in files_name:
    try:
        with open(config.cable_file_path+file_name, "r", encoding="utf-8") as f2:
            line_dict2=json.load(f2)
        if line_dict2.get("landing_points") == None:
            print(file_name+"no land points")
            continue
        for land_point in line_dict2.get("landing_points"):
        
            land_point_name=land_point["name"]
            land_set.add(land_point_name)
            cable_num_dict[str(land_point_name)]=cable_num_dict.get(str(land_point_name),0)+1
        
    except:
        print(file_name+"error")
    f2.close()

def find_cable_num(land_point_name):
    return cable_num_dict[land_point_name]




def get_l4_node():
    f = open(config.l4_node_data_path, 'w', encoding='utf-8',newline='')
    csv_writer = csv.writer(f)
    csv_writer.writerow(['coordinates','land_name','cable_number','country'])

    for index1,value1 in enumerate(line_dict["features"]):
        # list_cable为一个种类的海缆
        list_line=line_dict["features"][index1]["geometry"]["coordinates"]
        # list_line为一个种类的海缆线
        cable_id=line_dict["features"][index1]["properties"]["id"]
        land_points = {}
        # 构建land_points{coordinates,name}
        land_points=find_land_points_coordinates(find_land_points_name(findfiles(cable_id)))

        #找虚拟点的过程
        s2=list()
        for item in land_points.keys():
            s2.append(str(item))

        virtual_points = []
        cable_all_points = []
        for list_single_line in list_line:
            cable_all_points.extend(list_single_line)

        s1=list()
        for item in cable_all_points:
            s1.append(str(item))
        
        cable_all_points_noland = []
        cable_all_points_noland_str = [i for i in s1 if i not in s2]
        for item in cable_all_points_noland_str:
            item = item.replace("[","")
            item = item.replace("]","")
            item = item.replace(" ","")
            item = item.split(",")
            item = [float(item[0]),float(item[1])]
            cable_all_points_noland.append(item)
        virtual_points = extract_virtual_points(cable_all_points_noland)

        #构建虚拟点字典{str(point),vpx+id}
        virtual_points_temp=virtual_points[:]
        virtual_points_dict={}
        x=1
        for point in cable_all_points:
            for virtual_point in virtual_points_temp[:]:
                if point== virtual_point:
                    virtual_points_dict[str(point)]="vp"+str(x)+","+cable_id
                    virtual_points_temp.remove(virtual_point)
                    x=x+1


        random_num=random.randrange(10,100,1)

    # node.csv
    x=1
    for point in cable_all_points:
        for land_point_coordinates,land_point_name in list(land_points.items()):
            if str(point) == land_point_coordinates:
                land_set2.add(land_point_name)
                #取出land_point_country
                land_point_name_list=land_point_name.split(",")
                if len(land_point_name_list)==2:
                    land_point_country=land_point_name_list[1]
                else:
                    land_point_country=land_point_name_list[2]
                #找出cable_number
                cable_number=find_cable_num(land_point_name)
                point=str(point)
                point=point.replace("[","")
                point=point.replace("]","")
                csv_writer.writerow([point,land_point_name,cable_number,land_point_country])
                # del land_points[land_point_coordinates]
        for virtual_point in virtual_points[:]:
            if point== virtual_point:
                print("yes")
                # print(type(point))
                point=str(point)
                point=point.replace("[","")
                point=point.replace("]","")
                csv_writer.writerow([point,"vp"+str(x)+","+cable_id,1,'none'])
                virtual_points.remove(virtual_point)
                x=x+1

    # f.close()


def get_l4_edge():
    f2 = open(config.l4_edge_data_path, 'w', encoding='utf-8',newline='')
    csv_writer2 = csv.writer(f2)
    csv_writer2.writerow(['start_land_name','end_land_name','cable_id','band_width','length','owners','suppliers','rfs','rfs_year','is_planned'])
    for index1,value1 in enumerate(line_dict["features"]):
        # list_cable为一个种类的海缆
        list_line=line_dict["features"][index1]["geometry"]["coordinates"]
        # list_line为一个种类的海缆线
        cable_id=line_dict["features"][index1]["properties"]["id"]
        land_points = {}
        # 构建land_points{coordinates,name}
        land_points=find_land_points_coordinates(find_land_points_name(findfiles(cable_id)))

        cable_length,cable_owners,cable_suppliers,cable_rfs,cable_rfs_year,cable_is_planned=find_cable_attributes(findfiles(cable_id))

        #找虚拟点的过程
        s2=list()
        for item in land_points.keys():
            s2.append(str(item))

        virtual_points = []
        cable_all_points = []
        for list_single_line in list_line:
            cable_all_points.extend(list_single_line)

        s1=list()
        for item in cable_all_points:
            s1.append(str(item))
        
        cable_all_points_noland = []
        cable_all_points_noland_str = [i for i in s1 if i not in s2]
        for item in cable_all_points_noland_str:
            item = item.replace("[","")
            item = item.replace("]","")
            item = item.replace(" ","")
            item = item.split(",")
            item = [float(item[0]),float(item[1])]
            cable_all_points_noland.append(item)
        virtual_points = extract_virtual_points(cable_all_points_noland)

        #构建虚拟点字典{str(point),vpx+id}
        virtual_points_temp=virtual_points[:]
        virtual_points_dict={}
        x=1
        for point in cable_all_points:
            for virtual_point in virtual_points_temp[:]:
                if point== virtual_point:
                    virtual_points_dict[str(point)]="vp"+str(x)+","+cable_id
                    virtual_points_temp.remove(virtual_point)
                    x=x+1


        random_num=random.randrange(10,100,1)

        # triple.csv正确的and edge.csv正确的
        for line in list_line:
            line_point_list=[]#存放这条线里所有点
            triple_list=[]#存放land_coo三元组
            triple_list_name=[]#存放land_name三元组
            for point in line:
                line_point_list.append(point)
            for point in line_point_list:
                for land_point_coordinates,land_point_name in land_points.items():
                    if str(point) == land_point_coordinates:
                        triple_list.append(point)
                        triple_list_name.append(land_point_name)
                for i in range(len(virtual_points)):
                    if point == virtual_points[i]:
                        triple_list.append(point)
                        triple_list_name.append(virtual_points_dict[str(point)])

            for i in range(len(triple_list_name)-1):
                csv_writer2.writerow([triple_list_name[i],triple_list_name[i+1],cable_id,random_num,cable_length,cable_owners,cable_suppliers,cable_rfs,cable_rfs_year,cable_is_planned])


def clean_180():
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

    df_node.to_csv(config.l4_node_data_path, index=False)
    df_edge.to_csv(config.l4_edge_data_path, index=False)

def delete_blank():
    df_node = pd.read_csv(config.l4_node_data_path)
    df_node.drop_duplicates(subset=df_node.columns, keep='last', inplace=True)
    

def l4_csv_data():
    get_l4_edge()
    clean_180()



if __name__ == '__main__':
    l4_csv_data()




