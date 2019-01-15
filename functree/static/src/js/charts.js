'use strict';

const visualize = (profile, columns, layer, column) => {

    /** Percent stacked column chart */
    {
        const data = profile.filter((x) => {
            return x.layer === layer;
        });
        let series = [];
        for (var i = 0; i < columns.length; i++) {
            let s = {'name': columns[i], 'data': []}
            for (const d of data) {
                s.data.push(d.values[i]);
            }
            series.push(s);
        }
        let options = {
            'chart': {
                'type': 'column',
                'zoomType': 'x'
            },
            'title': {
                'text': 'Layer: "' + layer + '"'
            },
            'xAxis': {
                'categories': data.map((x) => { return x.entry; })
            },
            'yAxis': {
                'min': 0,
                'max': 100,
                'title': {
                    'text': 'Percentage'
                },
                'reversedStacks': false
            },
            'tooltip': {
                'pointFormat': '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.percentage:.0f}%)<br/>',
                'shared': true
            },
            'plotOptions': {
                'column': {
                    'stacking': 'percent'
                }
            },
            'colors': ['rgb(255, 128, 14)', 
            	'rgb(171, 171, 171)', 
            	'rgb(95, 158, 209)',
            	'rgb(89, 89, 89)',
            	'rgb(0, 107, 164)',
            	'rgb(255, 188, 121)',
            	'rgb(207, 207, 207)',
            	'rgb(200, 82, 0)',
            	'rgb(162, 200, 236)',
            	'rgb(137, 137, 137)'],
            'series': series,
            'credits': {
                'enabled': false
            }
        };
        Highcharts.chart('chart-0', options);
    }


    /** Normal stacked column chart */
    {
        const data = profile.filter((x) => {
            return x.layer === layer;
        });
        let series = [];
        for (var i = 0; i < columns.length; i++) {
            let s = {'name': columns[i], 'data': []}
            for (const d of data) {
                s.data.push(d.values[i]);
            }
            series.push(s);
        }
        let options = {
            'chart': {
                'type': 'column',
                'zoomType': 'x'
            },
            'title': {
                'text': 'Layer: "' + layer + '"'
            },
            'xAxis': {
                'categories': data.map((x) => { return x.entry; })
            },
            'yAxis': {
                'min': 0,
                'title': {
                    'text': 'Value'
                },
                'reversedStacks': false
            },
            'tooltip': {
                'pointFormat': '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.percentage:.0f}%)<br/>',
                'shared': true
            },
            'plotOptions': {
                'column': {
                    'stacking': 'normal'
                }
            },
            'colors': ['rgb(255, 128, 14)', 
            	'rgb(171, 171, 171)', 
            	'rgb(95, 158, 209)',
            	'rgb(89, 89, 89)',
            	'rgb(0, 107, 164)',
            	'rgb(255, 188, 121)',
            	'rgb(207, 207, 207)',
            	'rgb(200, 82, 0)',
            	'rgb(162, 200, 236)',
            	'rgb(137, 137, 137)'],
            'series': series,
            'credits': {
                'enabled': false
            }
        };
        Highcharts.chart('chart-1', options);
    }


    /** Heat map */
    {
        const data = profile.filter((x) => {
            return x.layer === layer;
        });
        let seriesData = [];
        for (var i = 0; i < data.length; i++) {
            for (var j = 0; j < columns.length; j++) {
                seriesData.push([i, j , data[i].values[j]]);
            }
        }
        let options = {
            'chart': {
                'type': 'heatmap',
                'marginTop': 40,
                'marginBottom': 80,
                'plotBorderWidth': 1,
                'zoomType': 'x'
            },
            'title': {
                'text': 'Layer: "' + layer + '"'
            },
            'xAxis': {
                'categories': data.map((x) => { return x.entry; })
            },
            'yAxis': {
                'categories': columns,
                'title': null
            },
            'colorAxis': {
                'min': 0,
                'minColor': '#FFFFFF',
                'maxColor': Highcharts.getOptions().colors[0]
            },
            'legend': {
                'align': 'right',
                'layout': 'vertical',
                'margin': 0,
                'verticalAlign': 'top',
                'y': 25,
                'symbolHeight': 280
            },
            'tooltip': {
                'formatter': function() {
                    return this.series.xAxis.categories[this.point.x] + '<br>' + this.series.yAxis.categories[this.point.y] + ': <b>' + this.point.value + '</b>';
                }
            },
            'series': [{
                'borderWidth': 1,
                'data': seriesData
            }],
            'credits': {
                'enabled': false
            }
        };
        Highcharts.chart('chart-2', options);
    }

    /** Pie chart */
    {
        const data = profile.filter((x) => {
            return x.layer === layer;
        });
        const seriesData = data.map((x) => {
            x.name = x.entry;
            x.y = x.values[column];
            return x;
        });
        let options = {
            'chart': {
                'plotBackgroundColor': null,
                'plotBorderWidth': null,
                'plotShadow': false,
                'type': 'pie'
            },
            'title': {
                'text': 'Layer: "' + layer + '" Column: "' + columns[column] + '"'
            },
            'tooltip': {
                'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            'plotOptions': {
                'pie': {
                    'allowPointSelect': true,
                    'cursor': 'pointer',
                    'dataLabels': {
                        'enabled': true,
                        'format': '<b>{point.name}</b>: {point.percentage:.1f} %',
                        'style': {
                            'color': (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                        }
                    }
                }
            },
            'colors': ['rgb(255, 128, 14)', 
            	'rgb(171, 171, 171)', 
            	'rgb(95, 158, 209)',
            	'rgb(89, 89, 89)',
            	'rgb(0, 107, 164)',
            	'rgb(255, 188, 121)',
            	'rgb(207, 207, 207)',
            	'rgb(200, 82, 0)',
            	'rgb(162, 200, 236)',
            	'rgb(137, 137, 137)'],
            'series': [{
                'name': columns[column],
                'colorByPoint': true,
                'data': seriesData
            }],
            'credits': {
                'enabled': false
            }
        };
        Highcharts.chart('chart-3', options);
    }
};
