var load_chart = function(graph) {
    var myChart = echarts.init(document.getElementById('canvas'));
    categories = [];
    for (var i in graph['categories']) categories.push({name : graph['categories'][i]});
    nodes = [];
    for (var i in graph['nodes']) {
        node = graph['nodes'][i];
        node['label'] = {normal : {show : node['symbolSize'] > 10}};
        nodes.push(node)
    }
    console.log(graph);
    var option = {
        title: {
            text: graph['title'],
            subtext: graph['subtitle'],
            top: 'bottom',
            left: 'right'
        },
        tooltip: {},
        legend: [{
            data: categories.map(function (a) {
                return a.name;
            })
        }],
        animationDuration: 1500,
        animationEasingUpdate: 'quinticInOut',
        series : [
            {
                name: graph['title'],
                type: 'graph',
                layout: 'force',
                // force : {
                //     repulsion : 0,
                //     gravity : 0.1,
                //     edgeLength : [100, 110]
                // },
                data: nodes,
                links: graph['edges'],
                legendHoverLink : true,
                hoverAnimation : true,
                draggable : true,
                categories: categories,
                roam: true,
                edgeSymbol : ['none', 'arrow'],
                focusNodeAdjacency: true,
                itemStyle: {
                    normal: {
                        borderColor: '#fff',
                        borderWidth: 1,
                        shadowBlur: 10,
                        shadowColor: 'rgba(0, 0, 0, 0.3)'
                    }
                },
                label: {
                    position: 'right',
                    formatter: '{b}'
                },
                lineStyle: {
                    color: 'source',
                    curveness: 0.3
                },
                emphasis: {
                    lineStyle: {
                        width: 5
                    }
                }
            }
        ]
    };
    myChart.setOption(option);
}

var load_list = function(l) {
    inner_text = '';
    for (p of l) {
        inner_text += '<li>' + p + '</li>';
    }
    $('#result_list').html(inner_text);
}

var is_number = function(s) {
    for (x of s) {
        if ('0123456789'.indexOf(x) == -1) {
            return false;
        }
    }
    return true;
}

var query = function() {
    if (($('#customer').val() == '') || ($('#prototype').val() == '')){
        $('#msgheader').html('输入错误');
        $('#msgbody').html('输入为空，请输入后再点击查询按钮');
        $('#msg').attr('class', 'ui negative message');
    } else if (!is_number($('#list_len').val())) {
        $('#msgheader').html('类型错误');
        $('#msgbody').html('列表长度应为正整数');
        $('#msg').attr('class', 'ui negative message');
    } else {
        $.ajaxSetup({
            headers : {'X-CSRFToken' : $('#csrf input').val()}
        });
        var list_len = 0;
        if ($('#list_len').val() == '') {
            list_len = 1;
        } else { list_len = parseInt($('#list_len').val()); }
        $.post('http://localhost:8000/q/q1/',
            JSON.stringify({
                'customer' : $('#customer').val(),
                'prototype' : $('#prototype').val(),
                'list_len' : list_len
            }),
            function(resp, status) {
                if (resp.empty) {
                    $('#msgheader').html('抱歉');
                    $('#msgbody').html('您所查找的目标不在数据库中');
                    $('#msg').attr('class', 'ui negative message');
                } else {
                    $('#msg').attr('class', 'ui negative hidden message');
                    // console.log(resp);
                    $('#result_container').attr('class', '');
                    load_chart(resp.graph_cont);
                    load_list(resp.list_cont);
                }
            }
        );
    }
}

$('#submit').click(function() {
    query();
})

$('.message .close').on('click', function() {
    $(this).closest('.message').transition('fade');
})
