
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
    var test = []
    for (var i = 0; i < data.length; i++) {
        labels.push(data[i]['benchmark_execution_hash'].toString());
        test.push(labels[i] + "--test");
    }

    var values = [];
    var accum_average = 0.0;
    for (var i = 0; i < data.length; i++) {
        var float_value = parseFloat(data[i]['average']);
        accum_average = accum_average + float_value;
        values.push(float_value);
    }

    accum_average = accum_average / Math.max(data.length, 1.0);


    var chartData = {}
    chartData['labels'] = labels
    chartData['test'] = test
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
        barValueSpacing : 1,

        //Number - Spacing between data sets within X values
        barDatasetSpacing : 0,

        //String - A legend template
        legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<datasets.length; i++){%><li><span style=\"background-color:<%=datasets[i].fillColor%>\"></span><%if(datasets[i].label){%><%=datasets[i].label%><%}%></li><%}%></ul>"

    }

    var ctx = document.getElementById(objId).getContext('2d');
    var myBarChart = new Chart(ctx).Bar(chartData, options);


    for (var i = 0; i < data.length; i++) {
        labels.push(data[i]['benchmark_execution_hash'].toString());

        var color = "#000000";
        var color_hi = "#FF0000";
        var ele = data[i];

        if (ele['invalidated']) {
            if (ele['bar_type'] === 'current_branch') {
                color = "#ff6666";
            } else if (ele['bar_type'] === 'other_branch') {
                color = "#ffcccc";
            }

            color_hi = "darkred"
        } else {
            if (ele['status'] === 'Ready') {
                if (ele['bar_type'] === 'current_branch') {
                    color = "#E0E0E0";
                    color_hi = "#D0D0D0";
                } else if (ele['bar_type'] === 'other_branch') {
                    color = "#F0F0F0";
                    color_hi = "#E0E0E0";
                }

                if (myBarChart.datasets[0].bars[i].value === 0) {
                    myBarChart.datasets[0].bars[i].value = Math.max(1, Math.trunc(accum_average * 0.2));
                    myBarChart.datasets[0].bars[i].label = "No result yet";
                    color = "#F0F0F0";
                    color_hi = "#E0E0E0";
                }

            } else if (ele['status'] === 'In_Progress') {

                if (ele['bar_type'] === 'current_branch') {
                    color = "#FFD770";
                    color_hi = "#F8D060";
                } else if (ele['bar_type'] === 'other_branch') {
                    color = "#FFE7F0";
                    color_hi = "#F8E0E0";
                }

            } else if (ele['status'] === 'Finished') {

                if (ele['bar_type'] === 'current_branch') {
                    color = "#B0C4DE";
                    color_hi = "steelblue";
                } else if (ele['bar_type'] === 'other_branch') {
                    color = "#dbe4f0";
                    color_hi = "steelblue";
                }

            } else if (ele['status'] === 'Finished_With_Errors') {

                if (ele['bar_type'] === 'current_branch') {
                    color = "#FF77FF";
                    color_hi = "#EE66EE";
                } else if (ele['bar_type'] === 'other_branch') {
                    color = "#FFDDFF";
                    color_hi = "#EECCEE";
                }

            }
            else {
            }
        }

        myBarChart.datasets[0].bars[i].fillColor = color;
        myBarChart.datasets[0].bars[i].highlightFill = color_hi;
        myBarChart.datasets[0].bars[i].benchmarkExecutionUrl = data[i]['benchmark_execution_url'];
    }

    myBarChart.update();

    document.getElementById(objId).onclick = function(evt){
        var activeBars = myBarChart.getBarsAtEvent(evt);
        console.log("activeBars", activeBars);
        window.location = activeBars[0].benchmarkExecutionUrl
    }.bind(myBarChart);
}
