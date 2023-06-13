import json
import os
import csv
import operator
import random
import copy
import pandas as pd

import pycountry_convert as pc
from config import DefaultConfig
sum=0
config = DefaultConfig()

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
  
def find_virtual_points(lst):
    virtual_points = []
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            if isinstance(lst[i], list) and isinstance(lst[j], list):  # 检查子列表是否为列表
                for x in lst[i]:
                    if x in lst[j]:
                        virtual_points.append(x)
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


def find_which_is_landpoint(point):
    with open('./landing-point-coordinates.json', "r", encoding="utf-8") as f1:
        landing_points = json.load(f1)
    if point in landing_points:
        return True
    else:
        return False


def get_l4_node():
    land_set=set()
    land_set2=set()
    cable_num_dict={} #cable_num_dict{land_point_name:num}
    path=config.cable_file_path
    files_name = os.listdir(path)
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


    with open(config.cable_geo_data_path, "r", encoding="utf-8") as f1:
        line_dict=json.load(f1)
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
        # land_set3.update(land_points.values())

        land_points_temp=[]
        for item in land_points.keys():
            item = item.replace("[", "")
            item = item.replace("]", "")
            item = item.replace(" ", "")
            item = item.split(",")
            item = [float(item[0]), float(item[1])]
            land_points_temp.append(item)




        cable_all_points = []
        for list_single_line in list_line:
            cable_all_points.extend(list_single_line)

        list_line_noland = list_line[:]
        for l in list_line_noland:
            for p in land_points_temp:
                if p in l:
                    # print(p)
                    l.remove(p)

        virtual_points = find_virtual_points(list_line_noland)


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
                    csv_writer.writerow([point,land_point_name,cable_number,land_point_country])
                    # del land_points[land_point_coordinates]
            for virtual_point in virtual_points[:]:
                if point== virtual_point:
                    print("yes")

                    csv_writer.writerow([point,"vp"+str(x)+","+cable_id,1,'none'])
                    virtual_points.remove(virtual_point)
                    x=x+1

    #去重
    df_node = pd.read_csv(config.l4_node_data_path) 
    df_node.drop_duplicates(inplace=True)
    df_node.to_csv(config.l4_node_data_path,index=False)

def get_l4_edge():

    land_set=set()
    land_set2=set()
    cable_num_dict={} #cable_num_dict{land_point_name:num}
    path=config.cable_file_path
    files_name = os.listdir(path)
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

    with open(config.cable_geo_data_path, "r", encoding="utf-8") as f1:
        line_dict=json.load(f1)
    f = open(config.l4_edge_data_path, 'w', encoding='utf-8',newline='')
    csv_writer = csv.writer(f)
    csv_writer.writerow(['start_land_name','end_land_name','cable_id','band_width','length','owners','suppliers','rfs','rfs_year','is_planned'])


    for index1,value1 in enumerate(line_dict["features"]):
        # list_cable为一个种类的海缆
        list_line=line_dict["features"][index1]["geometry"]["coordinates"]
        # list_line为一个种类的海缆线
        cable_id=line_dict["features"][index1]["properties"]["id"]
        land_points = {}
        # 构建land_points{coordinates,name}
        land_points=find_land_points_coordinates(find_land_points_name(findfiles(cable_id)))
        # land_set3.update(land_points.values())
        # print(land_points)
    

        #构建land_points_temp float类型一位小数
        land_points_temp=[]
        land_points_copy=land_points.copy()
        for item in land_points_copy.keys():
            item = item.replace("[", "")
            item = item.replace("]", "")
            item = item.replace(" ", "")
            item = item.split(",")
            item = [float(item[0]),float(item[1])]
            # print(item)
            land_points_temp.append(item)




        cable_all_points = []
        for list_single_line in list_line:
            cable_all_points.extend(list_single_line)

        #构建list_line_noland
        list_line_noland=copy.deepcopy(list_line)
        # list_line_noland=list_line[:]
        for l in list_line_noland:
            for p in land_points_temp:
                if p in l:
                    l.remove(p)

        virtual_points = find_virtual_points(list_line_noland)

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

        if cable_id=="cadmos-2":
            print("我是登陆点集合")
            print(land_points)

        #point 一位小数float
        #land_point_coordinates 1位小数str
        # triple.csv正确的and edge.csv正确的
        if cable_id=="cadmos-2":
            print("我是所有点集合")
            print(list_line)
            print(line_dict["features"][index1]["geometry"]["coordinates"])
        for line in list_line:
            line_point_list=[]#存放这条线里所有点
            triple_list=[]#存放land_coo三元组
            triple_list_name=[]#存放land_name三元组
            for point in line:
                line_point_list.append(point)
            for point in line_point_list:
                if cable_id=="cadmos-2":
                    print("我是点"+str(point))
                # print(point)
                for land_point_coordinates,land_point_name in land_points.items():
                    if cable_id=="cadmos-2":
                        
                        print("我是登陆点"+land_point_coordinates+land_point_name)
                    if str(point) == str(land_point_coordinates):

                        # print(point,land_point_coordinates)
                        # print(land_point_coordinates)
                        triple_list.append(point)
                        triple_list_name.append(land_point_name)
                for i in range(len(virtual_points)):
                    if point == virtual_points[i]:
                        triple_list.append(point)
                        triple_list_name.append(virtual_points_dict[str(point)])

            cable_length,cable_owners,cable_suppliers,cable_rfs,cable_rfs_year,cable_is_planned=find_cable_attributes(findfiles(cable_id))


            for i in range(len(triple_list_name)-1):
                csv_writer.writerow([triple_list_name[i],triple_list_name[i+1],cable_id,random_num,cable_length,cable_owners,cable_suppliers,cable_rfs,cable_rfs_year,cable_is_planned])

    df_l4_edge = pd.read_csv(config.l4_edge_data_path)
    df_l4_edge = df_l4_edge.drop_duplicates()
    df_l4_edge = df_l4_edge.loc[~(df_l4_edge['start_land_name'] == df_l4_edge['end_land_name'])]
    df_l4_edge.to_csv(config.l4_edge_data_path, index=False)

if __name__ == '__main__':
    # get_l4_node()
    get_l4_edge()