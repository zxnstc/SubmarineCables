import json
import os
import csv
import operator
import random
import networkx
import pycountry_convert as pc
from config import DefaultConfig

config = DefaultConfig()

with open(config.cable_geo_data_path, "r", encoding="utf-8") as f1:
    line_dict=json.load(f1)

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
path="cable"
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


def get_l4_node():
    f = open(config.l4_node_data_path, 'w', encoding='utf-8',newline='')
    csv_writer = csv.writer(f)
    csv_writer.writerow(['start_land_name','end_land_name','cable_id'])

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
                csv_writer.writerow([point,land_point_name,cable_number,land_point_country])
                # del land_points[land_point_coordinates]
        for virtual_point in virtual_points[:]:
            if point== virtual_point:
                print("yes")

                csv_writer.writerow([point,"vp"+str(x)+","+cable_id,1,'none'])
                virtual_points.remove(virtual_point)
                x=x+1




def get_l4_edge():
    f2 = open(config.l4_edge_data_path, 'w', encoding='utf-8',newline='')
    csv_writer2 = csv.writer(f2)
    csv_writer2.writerow(['start_land_name','end_land_name','cable_id','band_width'])
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
                csv_writer2.writerow([triple_list_name[i],triple_list_name[i+1],cable_id,random_num])


if __name__ == '__main__':
    get_l4_edge()
    get_l4_node()


