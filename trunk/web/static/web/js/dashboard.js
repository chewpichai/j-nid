$(function() {
	$('#hour-stat-chart').highcharts({
        chart: {
            type: 'line',
            marginBottom: 25
        },
        credits: {
        	enabled: false
        },
        title: {
            text: 'ยอดขายรายชั่วโมง',
            x: 50
        },
        xAxis: {
            categories: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                         13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
        },
        yAxis: {
            title: {
                text: 'ยอดขาย (บาท)'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }],
            min: 0
        },
        tooltip: {
            formatter: function() {
            	var total = "" + this.y;
            	total = total.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
            	return this.x + ":00<br/> <b>" + total + "</b> บาท";
            }
        },
        legend: {
        	enabled: false
        },
        series: [{
            data: eval($('#hour-stat-chart').attr('data'))
        }]
    });

	$('#product-stat-chart').highcharts({
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false
        },
        title: {
            text: 'จำนวนชิ้นที่สินค้า'
        },
        tooltip: {
    	    pointFormat: '{series.name}: <b>{point.y} ชิ้น</b>',
        	percentageDecimals: 1
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    color: '#000000',
                    connectorColor: '#000000',
                    formatter: function() {
                        return '<b>'+ this.point.name +'</b>: '+ this.percentage.toFixed(2) +' %';
                    }
                }
            }
        },
        series: [{
            type: 'pie',
            name: 'จำนวนชิ้น',
            data: eval($('#product-stat-chart').attr('data'))
        }]
    });
});