
chartVerticalBars = function(objId, data) {
    var labels = []
    for (var i = 0; i < data['data'].length; i++) {
        labels.push(i.toString());
    }

    var chartData = {}
    chartData['labels'] = labels
    chartData['datasets'] = [
        {
            'label' : 'chartDataSet',
            'fillColor': "#B0C4DE",
            'strokeColor': "rgba(220,220,220,0.8)",
            'highlightFill': "steelblue",
            'highlightStroke': "rgba(220,220,220,1)",
            'data' : data['data']
        },
    ]

    var options = {
        //Boolean - Whether the scale should start at zero, or an order of magnitude down from the lowest value
        scaleBeginAtZero : true,

        //Boolean - Whether grid lines are shown across the chart
        scaleShowGridLines : false,

        //String - Colour of the grid lines
        scaleGridLineColor : "rgba(0,0,0,.05)",

        //Number - Width of the grid lines
        scaleGridLineWidth : 1,

        //Boolean - Whether to show horizontal lines (except X axis)
        scaleShowHorizontalLines: true,

        //Boolean - Whether to show vertical lines (except Y axis)
        scaleShowVerticalLines: true,

        //Boolean - If there is a stroke on each bar
        barShowStroke : false,

        //Number - Pixel width of the bar stroke
        barStrokeWidth : 2,

        //Number - Spacing between each of the X value sets
        barValueSpacing : 5,

        //Number - Spacing between data sets within X values
        barDatasetSpacing : 0,

        //String - A legend template
        legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].fillColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"

    }

    var ctx = document.getElementById(objId).getContext('2d');
    var myBarChart = new Chart(ctx).Bar(chartData, options);
}



stackedchartVerticalBars = function(objId, data) {
    var labels = []
    for (var i = 0; i < data.length; i++) {
        labels.push(data[i]['benchmark_execution_id'].toString());
    }

    var values = [];
    for (var i = 0; i < data.length; i++) {
        values.push(parseFloat(data[i]['average']));
    }

    var chartData = {}
    chartData['labels'] = labels
    chartData['datasets'] = [
        {
            'label' : 'chartDataSet',
            'fillColor': "#B0C4DE",
            'strokeColor': "rgba(220,220,220,0.8)",
            'highlightFill': "steelblue",
            'highlightStroke': "rgba(220,220,220,1)",
            'data' : values
        },
    ]

    var options = {
        //Boolean - Whether the scale should start at zero, or an order of magnitude down from the lowest value
        scaleBeginAtZero : true,

        //Boolean - Whether grid lines are shown across the chart
        scaleShowGridLines : false,

        //String - Colour of the grid lines
        scaleGridLineColor : "rgba(0,0,0,.05)",

        //Number - Width of the grid lines
        scaleGridLineWidth : 1,

        //Boolean - Whether to show horizontal lines (except X axis)
        scaleShowHorizontalLines: true,

        //Boolean - Whether to show vertical lines (except Y axis)
        scaleShowVerticalLines: true,

        //Boolean - If there is a stroke on each bar
        barShowStroke : false,

        //Number - Pixel width of the bar stroke
        barStrokeWidth : 2,

        //Number - Spacing between each of the X value sets
        barValueSpacing : 5,

        //Number - Spacing between data sets within X values
        barDatasetSpacing : 0,

        //String - A legend template
        legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].fillColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"

    }

    var ctx = document.getElementById(objId).getContext('2d');
    var myBarChart = new Chart(ctx).Bar(chartData, options);
}
