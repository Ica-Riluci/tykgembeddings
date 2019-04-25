import json
from py2neo import Graph as ngraph

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from tykgebd import settings
from .models import *

def get_type(s):
    s = s[20:]
    s = s[:-2]
    return s

def get_node(n):
    return '[' + str(n.identity) + ']' + n['value']

def jsonresp(js):
    return HttpResponse(json.dumps(js), content_type='application/json')

# Create your views here.
def prototype_worker(request):
    if request.method == 'GET':
        return HttpResponse(json.dumps({'empty':True, 'content' : None}), content_type='application/json')
    elif request.method == 'POST':
        inp = json.loads(request.body.decode())
        qg = ngraph(settings.NEO_URL, user=settings.NEO_USER, password=settings.NEO_PW)
        qdata = qg.run('MATCH (worker:服务人员)-[]-(:记录编号)-[]-(task:任务号)-[]-(proto:机型) where proto.value="' + inp['prototype']+'" return worker, task').data()
        cnt = [(-1, 0) for i in range(len(qdata))]
        max_app = 0
        for p in qdata:
            worker = p['worker'].identity
            idx = worker % len(cnt)
            while cnt[idx][0] != worker and cnt[idx][0] != -1:
                idx += 1
                if idx >= len(cnt):
                    idx = 0
            if cnt[idx][0] == -1:
                cnt[idx] = (worker, cnt[idx][1])
            cnt[idx] = (cnt[idx][0], cnt[idx][1] + 1)
            if max_app < cnt[idx][1]:
                max_app = cnt[idx][1]
        resp = {
            'categories' : ['服务人员', '记录编号', '任务号', '机型'],
            'nodes' : [{
                'category' : 3,
                'name' : inp['prototype'],
                'symbolSize' : 20,
                'x' : 0,
                'y' : 300
            }],
            'edges' : []
        }
        id_list = []
        for i in cnt:
            if i[1] == max_app:
                id_list.append(i[0])
        for i in id_list:
            tgtnode = qg.run('MATCH (worker:服务人员) WHERE id(worker)=' + str(i) + ' RETURN worker').data()
            node = {
                'category' : 0,
                'name' : '[' + str(tgtnode[0]['worker'].identity) + ']' + dict(tgtnode[0]['worker'])['value'],
                'symbolSize' : 20,
                'x' : 0,
                'y' : -300
            }
            resp['nodes'].append(node)
            for t in qg.run('MATCH (worker:服务人员)-[]-(:记录编号)-[]-(task:任务号)-[]-(proto:机型) WHERE id(worker)=' + str(i) +' and proto.value="' + inp['prototype'] + '" RETURN task').data():
                tnode = {
                    'category' : 2,
                    'name' : dict(t['task'])['value'],
                    'symbolSize' : 20,
                    'x' : 0,
                    'y' : 100
                }
                e = {
                    'source' : tnode['name'],
                    'target' : inp['prototype']
                }
                if not tnode in resp['nodes']:
                    resp['nodes'].append(tnode)
                if not e in resp['edges']:
                    resp['edges'].append(e)
                for s in qg.run('MATCH (service:记录编号)-[]-(task:任务号) where id(task)=' + str(t['task'].identity) + ' RETURN service, task').data():
                    snode = {
                        'category' : 1,
                        'name' : dict(s['service'])['value'],
                        'symbolSize' : 10,
                        'x' : 0,
                        'y' : -100
                    }
                    if snode not in resp['nodes']:
                        resp['nodes'].append(snode)
                    e = {
                        'source' : dict(s['task'])['value'],
                        'target' : dict(s['service'])['value']
                    }
                    if e not in resp['edges']:
                        resp['edges'].append(e)
                    e = {
                        'source' : '[' + str(tgtnode[0]['worker'].identity) + ']' + dict(tgtnode[0]['worker'])['value'],
                        'target' : dict(s['service'])['value']
                    }
                    if e not in resp['edges']:
                        resp['edges'].append(e)
        for i in range(1, 4):
            cnt = 0
            for x in resp['nodes']:
                if x['category'] == i:
                    cnt += 1
            start = 0
            pace = 0
            if cnt > 10:
                start = -500
                pace = 1000.0 / (cnt - 1)
            else:
                pace = 100
                start = -500 + (1000 - pace * (cnt - 1)) / 2.0
            for x in range(0, len(resp['nodes'])):
                if resp['nodes'][x]['category'] == i:
                    resp['nodes'][x]['x'] = start
                    start = start + pace
        return HttpResponse(json.dumps({
            'empty' : False,
            'content' : resp
        }), content_type='application/json')

def simpleQ(request):
    if request.method == 'POST':
        input = json.loads(request.body.decode())
        db = ngraph(settings.NEO_URL, user=settings.NEO_USER, password=settings.NEO_PW)
        if str(input['type']) == '1':
            cypher_q = 'MATCH (n)-[e]-(x) WHERE n.value="' + input['target'] + '" RETURN n, e, x'
            qresp = db.run(cypher_q).data()
            if len(qresp) == 0:
                cypher_q = 'MATCH (n) WHERE n.value="' + input['target'] + '" RETURN n'
                qresp = db.run(cypher_q).data()
                if len(qresp) == 0:
                    resp = {
                        'empty' : True,
                        'content' : {}
                    }
                else:
                    graph = {
                        'title' : input['target'] + '',
                        'subtitle' : '',
                        'categories' : [qresp[0]['n']['type']],
                        'nodes' : [{
                            'category' : 0,
                            'name' : '*' + input['target'],
                            'symbolSize' : 20
                        }],
                        'edges' : []
                    }
                    resp = {
                        'empty' : False,
                        'content' : graph
                    }
                q = SimpleQuery(q_type=SimpleQuery.QTYPE, type=1, target=input['target'], q_result=json.dumps(resp['content']))
                q.save()
                return HttpResponse(json.dumps(resp), content_type='application/json')
            else:
                graph = {
                    'title' : input['target'] + '有关三元组',
                    'subtitle' : '',
                    'categories' : [qresp[0]['n']['type']],
                    'nodes' : [{'category' : 0, 'name' : get_node(qresp[0]['n']), 'symbolSize' : 20}],
                    'edges' : []
                }
                node_set = set([qresp[0]['n'].identity])
                category_set = set([qresp[0]['n']['type']])
                for triple in qresp:
                    if (triple['x'].identity not in node_set):
                        node_set.add(triple['x'].identity)
                        if triple['x']['type'] == None:
                            if triple['x']['label'] not in category_set:
                                category_set.add(triple['x']['label'])
                                graph['categories'].append(triple['x']['label'])
                        elif triple['x']['type'] not in category_set:
                            category_set.add(triple['x']['type'])
                            graph['categories'].append(triple['x']['type'])
                        if triple['x']['type'] == None:
                            graph['nodes'].append({
                                'category' : graph['categories'].index(triple['x']['label']),
                                'name' : get_node(triple['x']),
                                'symbolSize' : 20
                            })
                        else:
                            graph['nodes'].append({
                                'category' : graph['categories'].index(triple['x']['type']),
                                'name' : get_node(triple['x']),
                                'symbolSize' : 10
                            })
                    graph['edges'].append({
                        'source' : get_node(triple['e']._Walkable__sequence[0]),
                        'target' : get_node(triple['e']._Walkable__sequence[2]),
                        'value' : get_type(str(type(triple['e'])))
                    })
                graph['subtitle'] = '共计' + str(len(node_set)) + '个点,' + str(len(graph['edges'])) + '条边'
                resp = {
                    'empty' : False,
                    'content' : graph
                }
                q = SimpleQuery(q_type=SimpleQuery.QTYPE, type=1, target=input['target'], q_result=json.dumps(graph))
                q.save()
                return jsonresp(resp)
        elif str(input['type']) == '2':
            return jsonresp({})
        else:
            return jsonresp({})
    else:
        return jsonresp({})

def specQ1(request):
    if request.method == 'POST':
        input = json.loads(request.body.decode())
        cypher_q = 'MATCH (n1:服务人员)-[e1]-(n2:记录编号)-[e2]-(n3:任务号)-[e3]-(n4:联系人)-[e4]-(n5:机号)-[e5]-(n6:机型), (n3)-[e6]-(n6) WHERE n4.value="' + input['customer'] +'" and n6.value="' + input['prototype'] +'" RETURN n1, n2, n3, n4, n5, n6, e1, e2, e3, e4, e5, e6'
        db = ngraph(settings.NEO_URL, user=settings.NEO_USER, password=settings.NEO_PW)
        qresp = db.run(cypher_q).data()
        # for p in qresp:
        #     print(p)
        if len(qresp) == 0:
            resp = {
                'empty' : True,
                'content' : {}
            }
            q = SpecQuery1(q_type=SpecQuery1.QTYPE, proto=input['prototype'], customer_id=input['customer'], q_result=json.dumps(resp['content']))
            q.save()
            return jsonresp(resp)
        else:
            graph = {
                'title' : '服务人员推荐',
                'subtitle' : '（熟悉度）',
                'categories' : ['服务人员', '记录编号', '任务号', '联系人', '机号', '机型'],
                'nodes' : [],
                'edges' : []
            }
            node_count = {}
            task_count = set([])
            for p in qresp:
                if (p['n1'].identity, p['n3'].identity) in task_count:
                    pass
                else:
                    if str(p['n1'].identity) in node_count.keys():
                        node_count[str(p['n1'].identity)] += 1
                    else:
                        node_count[str(p['n1'].identity)] = 1
                    task_count.add((p['n1'].identity, p['n3'].identity))
            commend_list = []
            # print(node_count)
            for key in node_count.keys():
                # print('list:', end='')
                # print(commend_list)
                if len(commend_list) == 0:
                    commend_list = [(key, node_count[key])]
                else:
                    prev_l = commend_list
                    post_l = []
                    for i in range(len(commend_list)):
                        idx = len(commend_list) - i - 1
                        if commend_list[idx][1] >= node_count[key]:
                            prev_l = commend_list[:idx + 1]
                            post_l = commend_list[idx + 1:]
                            prev_l.append((key, node_count[key]))
                            prev_l.extend(post_l)
                            commend_list = prev_l
                            break
                        elif idx == 0:
                            prev_l = [(key, node_count[key])]
                            prev_l.extend(commend_list)
                            commend_list = prev_l
                # if len(commend_list) == 0:
                #     commend_list.append((key, node_count[key]))
                # else:
                #     # if node_count[key] > commend_list[-1][1]:
                #     #     commend_list = [(key, node_count[key])]
                #     # elif node_count[key] == commend_list[-1][1]:
                #     #     commend_list.append((key, node_count[key]))
            node_set = set([])
            tmp = commend_list[:input['list_len']]
            commend_list = []
            for i in tmp:
                commend_list.append(int(i[0]))
            # print(commend_list)
            name_list = []
            for i in commend_list:
                cypher_q = 'MATCH (n) WHERE id(n)=' + str(i) + ' RETURN n'
                name_list.append(db.run(cypher_q).data()[0]['n']['value'])
            symbol_size = [20, 5, 10, 20, 5, 20]
            for p in qresp:
                # print(p)
                if p['n1'].identity in commend_list:
                    for i in range(6):
                        if p['n' + str(i + 1)].identity not in node_set:
                            node_set.add(p['n' + str(i + 1)].identity)
                            graph['nodes'].append({
                                'category' : graph['categories'].index(p['n' + str(i + 1)]['type']),
                                'name' : get_node(p['n' + str(i + 1)]),
                                'symbolSize' : symbol_size[i]
                            })
                    for i in range(6):
                        graph['edges'].append({
                            'source' : get_node(p['e' + str(i + 1)]._Walkable__sequence[0]),
                            'target' : get_node(p['e' + str(i + 1)]._Walkable__sequence[2]),
                            'value' : get_type(str(type(p['e' + str(i + 1)])))
                        })
            resp = {
                'empty' : False,
                'graph_cont' : graph,
                'list_cont' : name_list
            }
            # print(resp['graph_cont'])
            q = SpecQuery1(q_type=SpecQuery1.QTYPE, proto=input['prototype'], customer_id=input['customer'], q_result=json.dumps(resp['graph_cont']))
            q.save()
            return jsonresp(resp)
    else:
        return jsonresp({})
