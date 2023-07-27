import os

from graphviz import Digraph
import networkx as nx
import datetime
import community.community_louvain as community_louvain
from tqdm import tqdm

from config import *
from kairos_utils import *


# Some common path abstraction for visualization
replace_dic = {
        '/run/shm/':'/run/shm/*',
        #     '/home/admin/.cache/mozilla/firefox/pe11scpa.default/cache2/entries/':'/home/admin/.cache/mozilla/firefox/pe11scpa.default/cache2/entries/*',
        '/home/admin/.cache/mozilla/firefox/':'/home/admin/.cache/mozilla/firefox/*',
        '/home/admin/.mozilla/firefox':'/home/admin/.mozilla/firefox*',
        '/data/replay_logdb/':'/data/replay_logdb/*',
        '/home/admin/.local/share/applications/':'/home/admin/.local/share/applications/*',
        '/usr/share/applications/':'/usr/share/applications/*',
        '/lib/x86_64-linux-gnu/':'/lib/x86_64-linux-gnu/*',
        '/proc/':'/proc/*',
        '/stat':'*/stat',
        '/etc/bash_completion.d/':'/etc/bash_completion.d/*',
        '/usr/bin/python2.7':'/usr/bin/python2.7/*',
        '/usr/lib/python2.7':'/usr/lib/python2.7/*',
}


def replace_path_name(path_name):
    for i in replace_dic:
        if i in path_name:
            return replace_dic[i]
    return path_name


# Users should manually put the detected anomalous time windows here
attack_list = [
        artifact_dir+'graph_4_10/2018-04-10 13:31:14.548738409~2018-04-10 13:46:36.161065223.txt',
        artifact_dir+'graph_4_10/2018-04-10 14:02:17.001271389~2018-04-10 14:17:34.001373488.txt',
        artifact_dir+'graph_4_10/2018-04-10 14:17:34.001373488~2018-04-10 14:33:18.350772859.txt',
        artifact_dir+'graph_4_10/2018-04-10 14:33:18.350772859~2018-04-10 14:48:47.320442910.txt',
        artifact_dir+'graph_4_10/2018-04-10 14:48:47.320442910~2018-04-10 15:03:54.307022037.txt',
        artifact_dir+'graph_4_12/2018-04-12 12:39:06.592684498~2018-04-12 12:54:44.001888457.txt',
        artifact_dir+'graph_4_12/2018-04-12 12:54:44.001888457~2018-04-12 13:09:55.026832462.txt',
        artifact_dir+'graph_4_12/2018-04-12 13:09:55.026832462~2018-04-12 13:25:06.588370709.txt',
        artifact_dir+'graph_4_12/2018-04-12 13:25:06.588370709~2018-04-12 13:40:07.178206094.txt',
]

original_edges_count = 0
graphs = []
gg = nx.DiGraph()
count = 0
for path in tqdm(attack_list):
    if ".txt" in path:
        line_count = 0
        node_set = set()
        tempg = nx.DiGraph()
        f = open(path, "r")
        edge_list = []
        for line in f:
            count += 1
            l = line.strip()
            jdata = eval(l)
            edge_list.append(jdata)

        edge_list = sorted(edge_list, key=lambda x: x['loss'], reverse=True)
        original_edges_count += len(edge_list)

        loss_list = []
        for i in edge_list:
            loss_list.append(i['loss'])
        loss_mean = mean(loss_list)
        loss_std = std(loss_list)
        print(loss_mean)
        print(loss_std)
        thr = loss_mean + 1.5 * loss_std
        print("thr:", thr)
        for e in edge_list:
            if e['loss'] > thr:
                tempg.add_edge(str(hashgen(replace_path_name(e['srcmsg']))),
                               str(hashgen(replace_path_name(e['dstmsg']))))
                gg.add_edge(str(hashgen(replace_path_name(e['srcmsg']))), str(hashgen(replace_path_name(e['dstmsg']))),
                            loss=e['loss'], srcmsg=e['srcmsg'], dstmsg=e['dstmsg'], edge_type=e['edge_type'],
                            time=e['time'])


partition = community_louvain.best_partition(gg.to_undirected())

# Generate the candidate subgraphs based on community discovery results
communities = {}
max_partition = 0
for i in partition:
    if partition[i] > max_partition:
        max_partition = partition[i]
for i in range(max_partition + 1):
    communities[i] = nx.DiGraph()
for e in gg.edges:
    communities[partition[e[0]]].add_edge(e[0], e[1])
    communities[partition[e[1]]].add_edge(e[0], e[1])


# Define the attack nodes. They are **only be used to plot the colors of attack nodes and edges**.
# They won't change the detection results.
def attack_edge_flag(msg):
    attack_nodes = [
        '/home/admin/clean',
        '/dev/glx_alsa_675',
        '/home/admin/profile',
        '/var/log/xdev',
        '/etc/passwd',
        '161.116.88.72',
        '146.153.68.151',
        '/var/log/mail',
        '/tmp/memtrace.so',
        #         '/tmp',
        '/var/log/xdev',
        '/var/log/wdev',
        'gtcache',
        'firefox',
        #         '/var/log',
    ]
    flag = False
    for i in attack_nodes:
        if i in str(msg):
            flag = True
    return flag


# Plot and render candidate subgraph
os.system(f"mkdir -p {artifact_dir}/graph_visual/")
graph_index = 0
for c in communities:
    dot = Digraph(name="MyPicture", comment="the test", format="pdf")
    dot.graph_attr['rankdir'] = 'LR'

    for e in communities[c].edges:
        try:
            temp_edge = gg.edges[e]
            srcnode = e['srcnode']
            dstnode = e['dstnode']
        except:
            pass

        if True:
            # source node
            if "'subject': '" in temp_edge['srcmsg']:
                src_shape = 'box'
            elif "'file': '" in temp_edge['srcmsg']:
                src_shape = 'oval'
            elif "'netflow': '" in temp_edge['srcmsg']:
                src_shape = 'diamond'
            if attack_edge_flag(temp_edge['srcmsg']):
                src_node_color = 'red'
            else:
                src_node_color = 'blue'
            dot.node(name=str(hashgen(replace_path_name(temp_edge['srcmsg']))), label=str(
                replace_path_name(temp_edge['srcmsg']) + str(
                    partition[str(hashgen(replace_path_name(temp_edge['srcmsg'])))])), color=src_node_color,
                     shape=src_shape)

            # destination node
            if "'subject': '" in temp_edge['dstmsg']:
                dst_shape = 'box'
            elif "'file': '" in temp_edge['dstmsg']:
                dst_shape = 'oval'
            elif "'netflow': '" in temp_edge['dstmsg']:
                dst_shape = 'diamond'
            if attack_edge_flag(temp_edge['dstmsg']):
                dst_node_color = 'red'
            else:
                dst_node_color = 'blue'
            dot.node(name=str(hashgen(replace_path_name(temp_edge['dstmsg']))), label=str(
                replace_path_name(temp_edge['dstmsg']) + str(
                    partition[str(hashgen(replace_path_name(temp_edge['dstmsg'])))])), color=dst_node_color,
                     shape=dst_shape)

            if attack_edge_flag(temp_edge['srcmsg']) and attack_edge_flag(temp_edge['dstmsg']):
                edge_color = 'red'
            else:
                edge_color = 'blue'
            dot.edge(str(hashgen(replace_path_name(temp_edge['srcmsg']))),
                     str(hashgen(replace_path_name(temp_edge['dstmsg']))), label=temp_edge['edge_type'],
                     color=edge_color)

    dot.render(f'{artifact_dir}/graph_visual/subgraph_' + str(graph_index), view=False)
    graph_index += 1



