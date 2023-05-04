import json
import os
import csv
import operator
import random
import networkx
import pycountry_convert as pc

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
    path="cable"
    files_name = os.listdir(path)
    for file_name in files_name:
        if cable_id in file_name:
            return file_name

def find_land_points_name(file_name):
    land_points_name_list=[]
    with open('./cable/'+file_name, "r", encoding="utf-8") as f1:
        line_dict=json.load(f1)
    for land_point in line_dict["landing_points"]:
        land_point_name=land_point["name"]
        land_points_name_list.append(land_point_name)
    return land_points_name_list

def find_land_points_coordinates(land_poins_name_list):
    with open('./landing-point-geo.json', "r", encoding="utf-8") as f1:
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

land_set=set()
land_set2=set()
cable_num_dict={} #cable_num_dict{land_point_name:num}
path="cable"
files_name = os.listdir(path)
for file_name in files_name:
    try:
        with open('./cable/'+file_name, "r", encoding="utf-8") as f2:
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


# print(find_land_points_coordinates(find_land_points_name(findfiles("cadmos-2"))))

with open('./cable_geo.json', "r", encoding="utf-8") as f1:
    line_dict=json.load(f1)
f = open('ContinentEdge.csv', 'w', encoding='utf-8',newline='')
# f = open('LandingPoints.csv', 'w', encoding='utf-8',newline='')
csv_writer = csv.writer(f)
# f1 = open('triples.csv', 'w', encoding='utf-8',newline='')
# csv_writer = csv.writer(f1)
# f2 = open('LandingPointsEdge.csv', 'w', encoding='utf-8',newline='')
# csv_writer1 = csv.writer(f1)
# csv_writer2=csv.writer(f2)
csv_writer.writerow(['start_land_name','end_land_name','cable_id'])
# csv_writer1.writerow(['start_land_coordinates','end_land_coordinates','cable_id','band_width'])
# csv_writer2.writerow(['start_land_name','end_land_name','cable_id','band_width'])
# land_set3=set()




for index1,value1 in enumerate(line_dict["features"]):
    # list_cable为一个种类的海缆
    list_line=line_dict["features"][index1]["geometry"]["coordinates"]
    # list_line为一个种类的海缆线
    cable_id=line_dict["features"][index1]["properties"]["id"]
    land_points = {}
    # 构建land_points{coordinates,name}
    land_points=find_land_points_coordinates(find_land_points_name(findfiles(cable_id)))
    # land_set3.update(land_points.values())



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
    # print(virtual_points_dict.keys())
    # print(virtual_points_dict.values())


    # # 把错误的登陆点坐标更新成正确的
    # land_points_=[]
    # land_points_str=list(land_points.keys())
    # for item in land_points_str:
    #     item = item.replace("[","")
    #     item = item.replace("]","")
    #     item = item.replace(" ","")
    #     item = item.split(",")
    #     item = [float(item[0]),float(item[1])]
    #     land_points_.append(item)

    # for i in range(len(land_points_)):
    #     flag=1
    #     for point in cable_all_points:
    #         if land_points_[i] == str(point):
    #             flag=0
    #     if(flag):
    #         diff=[]
    #         for point in cable_all_points:
    #             value=abs(point[0]-land_points_[i][0])+abs(point[1]-land_points_[i][1])
    #             diff.append(value)
    #         min_index, min_number = min(enumerate(diff), key=operator.itemgetter(1))
    #         print(min_index)
    #         old_data=cable_all_points[min_index]
    #         cable_all_points[min_index]=land_points_[i]
    #         for index3,value3 in enumerate(list_line):
    #             for index,value in enumerate(list_line[index3]):
    #                 if(list_line[index3][index]==old_data):
    #                     list_line[index3][index]=land_points_[i]        
   
    # print("land point: ", land_points.keys())
    # # print("land point name",find_land_points_name(findfiles(cable_id)))
    # print("virtual point: ", virtual_points)
    # print("cable_all_points: ",len(cable_all_points), cable_all_points)
    random_num=random.randrange(10,100,1)

    # #edge.csv
    # triple_list=[]#存放land_name三元组
    # for point in cable_all_points:
    #     # for land_point_coordinates,land_point_name in land_points.items():
    #     #     if str(point) == land_point_coordinates:
    #     #         triple_list.append(land_point_name)
    #     for i in range(len(virtual_points)):
    #         if point == virtual_points[i]:
    #             triple_list.append("vp"+str(i+1)+","+cable_id)
    #             virtual_points_dict[point]="vp"+str(i+1)+","+cable_id


    # for i in range(len(triple_list)-1):
    #     csv_writer.writerow([triple_list[i],triple_list[i+1],cable_id,random.randrange(1,100,1)])




    #triple.csv正确的and edge.csv正确的
    # for line in list_line:
    #     line_point_list=[]#存放这条线里所有点
    #     triple_list=[]#存放land_coo三元组
    #     triple_list_name=[]#存放land_name三元组
    #     for point in line:
    #         line_point_list.append(point)
    #     for point in line_point_list:
    #         for land_point_coordinates,land_point_name in land_points.items():
    #             if str(point) == land_point_coordinates:
    #                 triple_list.append(point)
    #                 triple_list_name.append(land_point_name)
    #         for i in range(len(virtual_points)):
    #             if point == virtual_points[i]:
    #                 triple_list.append(point)
    #                 triple_list_name.append(virtual_points_dict[str(point)])

        
    #     for i in range(len(triple_list)-1):
    #         csv_writer1.writerow([triple_list[i],triple_list[i+1],cable_id,random_num])
    #     for i in range(len(triple_list_name)-1):
    #         csv_writer2.writerow([triple_list_name[i],triple_list_name[i+1],cable_id,random_num])

    #     print(triple_list_name)



    # #LandPointsEdge.csv
    # triple_list=set()#存放land_name三元组
    # for point in cable_all_points:
    #     for land_point_coordinates,land_point_name in land_points.items():
    #         if str(point) == land_point_coordinates:
    #             triple_list.add(land_point_name)
    #     # for i in range(len(virtual_points)):
    #     #     if point == virtual_points[i]:
    #     #         triple_list.append("vp"+str(i+1)+","+cable_id)
    #     #         virtual_points_dict[point]="vp"+str(i+1)+","+cable_id

    # triple_list=list(triple_list)

    # for i in range(len(triple_list)-1):
    #     csv_writer2.writerow([triple_list[i],triple_list[i+1],cable_id,random_num])


            

    # #triples.csv
    # triple_list=[]#存放land_name三元组
    # for point in cable_all_points:
    #     for land_point_coordinates,land_point_name in land_points.items():
    #         if str(point) == land_point_coordinates:
    #             triple_list.append(point)
    #     for i in range(len(virtual_points)):
    #         if point == virtual_points[i]:
    #             triple_list.append(point)

    # for i in range(len(triple_list)-1):
    #     csv_writer.writerow([triple_list[i],triple_list[i+1],cable_id,random.randrange(1,100,1)])


    # # node.csv
    # x=1
    # for point in cable_all_points:
    #     for land_point_coordinates,land_point_name in list(land_points.items()):
    #         if str(point) == land_point_coordinates:
    #             land_set2.add(land_point_name)
    #             #取出land_point_country
    #             land_point_name_list=land_point_name.split(",")
    #             if len(land_point_name_list)==2:
    #                 land_point_country=land_point_name_list[1]
    #             else:
    #                 land_point_country=land_point_name_list[2]
    #             #找出cable_number
    #             cable_number=find_cable_num(land_point_name)
    #             csv_writer.writerow([point,land_point_name,cable_number,land_point_country])
    #             # del land_points[land_point_coordinates]
    #     for virtual_point in virtual_points[:]:
    #         if point== virtual_point:
    #             print("yes")

    #             csv_writer.writerow([point,"vp"+str(x)+","+cable_id,1,'none'])
    #             virtual_points.remove(virtual_point)
    #             x=x+1

    
    # LandingPoints.csv 没有虚拟点的子图
    # x=1
    # for point in cable_all_points:
    #     for land_point_coordinates,land_point_name in list(land_points.items()):
    #         if str(point) == land_point_coordinates:
    #             land_set2.add(land_point_name)
    #             #取出land_point_country
    #             land_point_name_list=land_point_name.split(",")
    #             if len(land_point_name_list)==2:
    #                 land_point_country=land_point_name_list[1]
    #             else:
    #                 land_point_country=land_point_name_list[2]
    #             #找出cable_number
    #             cable_number=find_cable_num(land_point_name)
    #             csv_writer.writerow([point,land_point_name,cable_number,land_point_country])
    #             # del land_points[land_point_coordinates]
    #     for virtual_point in virtual_points[:]:
    #         if point== virtual_point:
    #             print("yes")

    #             # csv_writer.writerow([point,"vp"+str(x)+","+cable_id,1,'none'])
    #             virtual_points.remove(virtual_point)
    #             x=x+1


    # CountryNode.csv CountryEdge.csv
    # country_node_set=set()
    # country_node_dict={}
    # for point in cable_all_points:
    #     for land_point_coordinates,land_point_name in list(land_points.items()):
    #         if str(point) == land_point_coordinates:
    #             #取出land_point_country
    #             land_point_name_list=land_point_name.split(",")
    #             if len(land_point_name_list)==2:
    #                 land_point_country=land_point_name_list[1]
    #             else:
    #                 land_point_country=land_point_name_list[2]
    #             #找出cable_number
    #             if land_point_country not in country_node_set:
    #                 country_node_set.add(land_point_country)
    #                 country_node_dict[land_point_country]=land_point_coordinates

    # for i in range(len(country_node_dict.items())-1):
    #     csv_writer.writerow([list(country_node_dict.items())[i][0],list(country_node_dict.items())[i+1][0],cable_id])



    # # ContinentNode.csv ContinentEdge.csv
    country_node_set=set()
    country_node_dict={}

    for point in cable_all_points:
        for land_point_coordinates,land_point_name in list(land_points.items()):
            if str(point) == land_point_coordinates:
                land_point_continent=country_to_continent(land_point_name)
                #
                if (land_point_continent not in country_node_set) and (land_point_continent != 'none'):
                    country_node_set.add(land_point_continent)
                    country_node_dict[land_point_continent]=land_point_coordinates

# for continent,continent_coordinates in country_node_dict.items():
#     csv_writer.writerow([continent,continent_coordinates])

    for i in range(len(country_node_dict.items())-1):
        csv_writer.writerow([list(country_node_dict.items())[i][0],list(country_node_dict.items())[i+1][0],cable_id])



    # triple_list_old=[]#存放三元组
    # for point in cable_all_points:
    #     flag=0
    #     for land_point in land_points:
    #         if point == land_point:
    #             triple_list_old.append(point)
    #     for virtual_point in virtual_points:
    #         if point == virtual_point:
    #             triple_list_old.append(point)
    #     # if flag==1:
    #     #     triple_list_old.append(point)
    # print("triple_list_old: ", len(triple_list_old),triple_list_old)
    # print("triple_list: ", len(triple_list),triple_list)



    # print("triple_list: ", triple_list)

    # for i in range(len(triple_list)-1):
    #     csv_writer.writerow([triple_list[i],triple_list[i+1],cable_id,random.randrange(1,100,1)])



# csv_writer.writerow([point,land_point_country])

# with open('./cable_geo.json', 'w') as f:
#     json.dump(line_dict, f)






# with open('./cable_test.json', "r", encoding="utf-8") as f1:
#     line_dict = json.load(f1)
#     for list_cable in line_dict["features"]:
#         list_line = list_cable["geometry"][0]["coordinates"]
#         land_points = []
#         virtual_points = []
#         cable_all_points = []
#         for list_single_line in list_line:
#             cable_all_points.extend(list_single_line)
#             for list_coordinate in list_single_line:
#                 #print(list_coordinate)
#                 # Check if a point is on land:
#                 res = is_landing_point(list_coordinate)
#                 # print(res)
#                 if res == True:
#                     land_points.append(list_coordinate)
#         virtual_points = extract_virtual_points(cable_all_points)
#         print("land point: ", land_points)
#         print("virtual point: ", virtual_points)    
#         land_points.extend(virtual_points)
#         list_cable["geometry"][1]["coordinates"] = land_points

# with open('./test2.json', 'w') as f:
#     json.dump(line_dict, f)