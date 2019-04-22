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
    console.log(nodes);
    var option = {
        title: {
            text: $('#prototype').val(),
            subtext: '',
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
                name: $('#prototype').val(),
                type: 'graph',
                layout: 'none',
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
                        width: 10
                    }
                }
            }
        ]
    };
    myChart.setOption(option);
}

var query = function() {
    if ($('#prototype').val() != '') {
        $.ajaxSetup({
            headers : {'X-CSRFToken' : $('#csrf_token input').val()}
        });
        $.post('http://localhost:8000/q/prototype_worker/',
            JSON.stringify({
                'prototype' : $('#prototype').val()
            }),
            function(data, status) {
                console.log(data);
                if (!data.empty) {
                    load_chart(data.content);
                } else {
                    $('#msg').attr('class', 'ui warning messsage');
                }
            });
    }
}

$('#submit').click(function() {
    query();
})
