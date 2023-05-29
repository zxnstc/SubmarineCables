import os


class DefaultConfig(object):
    # dir path
    current_path = os.path.dirname(os.path.abspath(__file__))

    # l4
    l4_node_data_path = os.path.join(current_path, 'data/near_merge_data/l4_node_one.csv')
    l4_edge_data_path = os.path.join(current_path, 'data/near_merge_data/l4_edge_one.csv')
    l4_result_path = os.path.join(current_path, 'result/result_l4/')

    # l3
    l3_node_data_path = os.path.join(current_path, 'data/near_merge_data/l3_node.csv')
    l3_edge_data_path = os.path.join(current_path, 'data/near_merge_data/l3_edge.csv')
    l3_result_path = os.path.join(current_path, 'result/result_l3/')

    # l2
    l2_node_data_path = os.path.join(current_path, 'data/near_merge_data/l2_node.csv')
    l2_edge_data_path = os.path.join(current_path, 'data/near_merge_data/l2_edge.csv')
    l2_result_path = os.path.join(current_path, 'result/result_l2/')

    # l1
    l1_node_data_path = os.path.join(current_path, 'data/near_merge_data/l1_node.csv')
    l1_edge_data_path = os.path.join(current_path, 'data/near_merge_data/l1_edge.csv')
    l1_result_path = os.path.join(current_path, 'result/result_l1/')

    # 原始数据
    cable_geo_data_path = os.path.join(current_path, 'data/raw_data/cable-geo.json')
    landing_point_data_path = os.path.join(current_path, 'data/raw_data/landing-point-geo.json')
    cable_file_path = os.path.join(current_path, 'data/raw_data/cable/')
