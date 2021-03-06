'use strict';

const DEFAULT_CONFIG = {
    'elementId': 'functree',
    'width': '100%',
    'height': '100%',
    'viewBoxWidth': 800,
    'viewBoxHeight': 800,
    'diameter': 800,
    'duration': 1000,
    'normalize': true,
    'percentage': false,
    'labelMinDepth': 3,
    'maxDepth': 4,
    'colorizeBy': 'layer',
    'colorSet': {
        'default': '#5f5f5f'
    },
    colorPalettes: {
    	// https://public.tableau.com/profile/chris.gerrard#!/vizhome/TableauColors/ColorPaletteswithRGBValues
    	'tableauColorBlind10' : [
        	'rgb(255, 128, 14)', 
        	'rgb(171, 171, 171)', 
        	'rgb(95, 158, 209)',
        	'rgb(89, 89, 89)',
        	'rgb(0, 107, 164)',
        	'rgb(255, 188, 121)',
        	'rgb(207, 207, 207)',
        	'rgb(200, 82, 0)',
        	'rgb(162, 200, 236)',
        	'rgb(137, 137, 137)',
        	], 
        // http://jfly.iam.u-tokyo.ac.jp/color/
        'cud8': [
        	'rgb(0, 0, 0)',
        	'rgb(230, 159, 0)',
        	'rgb(86, 180, 233)',
        	'rgb(0, 158, 115)',
        	'rgb(240, 228, 66)',
        	'rgb(0, 114, 178)',
        	'rgb(213, 94, 0)',
        	'rgb(204, 121, 167)'
        ]
    },
    'external': {
        'entry': 'vmEntryDetail.entry',
        'breadcrumb': 'vmBreadcrumb.items'
    }
}

const FuncTree = class {
	constructor(root, infoServiceURL, config={}) {
        this.root = root;
        this.infoServiceURL = infoServiceURL;
        this.root.x0 = 0;
        this.root.y0 = 0;
        this.nodes = this.getNodes();
        this.config = mergeRecursive(JSON.parse(JSON.stringify(DEFAULT_CONFIG)), config);
        this.tree = d3.layout.tree()
            .size([360, this.config.diameter / 2]);
        
        this.colorScale = d3.scale.ordinal().range( this.config.colorPalettes.tableauColorBlind10 );

        let id = 0;
        for (const node of this.nodes) {
            node.id = id++;
        }
        this.initTree();
    }

    configure(config={}) {
        this.config = mergeRecursive(this.config, config);
        return this;
    }

    initTree(zeroize=true) {
        for (const node of this.nodes) {
            if (zeroize) {
                node.values = [];
                node.value = 0;
                node.cols = [];
            }
            if (node.children && node.depth >= this.config.maxDepth) {
                node._children = node.children;
                node.children = null;
            }
            if (node._children && node.depth < this.config.maxDepth) {
                node.children = node._children;
                node._children = null;
            }
        }
        return this;
    }

    create(elementId=this.config.elementId, width=this.config.width, height=this.config.height) {
        const svg = d3.select('#' + elementId)
            .insert('svg', ':first-child')
            .attr('xmlns', 'http://www.w3.org/2000/svg')
            .attr('version', '1.1')
            .attr('width', width)
            .attr('height', height)
            .attr('viewBox', '0 0 ' + this.config.viewBoxWidth + ' ' + this.config.viewBoxHeight)
            .attr('preserveAspectRatio', 'xMidYMid meet');
        const buffer = svg.append('g')
            .attr('id', 'buffer')
            .attr('transform', 'translate(' + this.config.viewBoxWidth / 2 + ',' + this.config.viewBoxHeight / 2 + '),scale(1)');
        const groupIds = [
            'rings',
            'links',
            'charts',
            'rounds',
            'labels',
            'nodes'
        ];
        for (const i of groupIds) {
            buffer.append('g').attr('id', i);
        }
        const zoomListener = d3.behavior.zoom()
        svg.call(zoomListener
            .translate([this.config.viewBoxWidth / 2, this.config.viewBoxHeight / 2])
            .scaleExtent([0.5, 10])
            .on('zoom', () => {
                buffer.attr({
                    'transform': 'translate(' + d3.event.translate + '),scale(' + d3.event.scale + ')'
                });
            })
        );
        
        d3.selectAll(".zoomcontrol").on('click', () => {
        	zoomClick(zoomListener, this.config)
        });
        
        return this;
    }

    update(source=this.root) {

        const nodes = this.tree.nodes(this.root);
        const links = this.tree.links(nodes);
        const depth = d3.max(
            nodes.map((x) => {
                return x.depth;
            })
        );


        const getLayerMax = (nodes, maxFunc) => {
            return Array.from(new Array(depth + 1))
                .map((v, i) => {
                    const candidates = nodes
                        .filter((x) => {
                            return x.depth === i;
                        })
                        .map(maxFunc);
                    return d3.max(candidates);
                });
        };
        const maxValue = getLayerMax(nodes, (x) => {
            return x.value;
        });

        const maxSumOfValues = getLayerMax(nodes, (x) => {
            return d3.sum(x.values);
        });
        const maxMaxOfValues = getLayerMax(nodes, (x) => {
            return d3.max(x.values);
        });

        this._updateRings(depth);
        this._updateLinks(links, source);
        this._updateNodes(nodes, source);
        this._updateBars(nodes, source, depth, maxSumOfValues, maxMaxOfValues);
        this._updateRounds(nodes, source, depth, maxValue);
        this._updateLabels(nodes, source, maxValue, maxSumOfValues);

        for (var node of nodes) {
            node.x0 = node.x;
            node.y0 = node.y;
        }
        // Lazy initialize Bootstrap tooltip 
        // FIXME for <g> elements this does not work as children trigger the event but they lack the data-original-title attribute
        $('[data-toggle="tooltip"]').on({
        	'mouseenter': (x) => {
        		$(x.target).tooltip({
        			container: 'body',
        			placement: 'top',
        			trigger: 'manual'
        		}).tooltip('show');
        	},
        	'mouseleave': (x) => {
        		$(x.target).tooltip('hide');
        	}
        });
    }

    _updateRings(depth) {
        const ring = d3.select('#rings')
            .selectAll('circle')
            .data(d3.range(1, depth, 2));
        ring.enter()
            .append('circle')
            .attr('fill', 'none')
            .attr('r', (d) => {
                return (this.config.diameter / 2) / depth * (d + 0.5) || 0;
            })
            .attr('stroke', '#f8f8f8')
            .attr('stroke-width', 0);
        ring
            .transition()
            .duration(this.config.duration)
            .attr('r', (d) => {
                return (this.config.diameter / 2) / depth * (d + 0.5) || 0;
            })
            .attr('stroke-width', (this.config.diameter / 2) / depth || 0);
        ring.exit()
            .transition()
            .duration(this.config.duration)
            .attr('stroke-width', 0)
            .remove();
    }

    _updateLinks(links, source) {
        const diagonal = d3.svg.diagonal.radial()
            .projection((d) => {
                return [d.y, d.x / 180 * Math.PI];
            });
        const straight = (d) => {
            const x = (d) => {
                return d.y * Math.cos((d.x - 90) / 180 * Math.PI);
            };
            const y = (d) => {
                return d.y * Math.sin((d.x - 90) / 180 * Math.PI);
            };
            return 'M' + x(d.source) + ',' + y(d.source) + 'L' + x(d.target) + ',' + y(d.target);
        };
        const link = d3.select('#links')
            .selectAll('path')
            .data(links, (d) => {
                return d.target.id;
            });
        link.enter()
            .append('path')
            .attr('fill', 'none')
            .attr('stroke', '#999')
            .attr('stroke-width', 0.25)
            .attr('stroke-dasharray', (d) => {
                if (d.source.depth === 0) {
                    return '1,1';
                }
            })
            .attr('d', (d) => {
                const o = {
                    'x': source.x0,
                    'y': source.y0
                };
                const vector = {
                    'source': o,
                    'target': o
                };
                if (d.source.depth === 0) {
                    return straight(vector);
                } else {
                    return diagonal(vector);
                }
            })
            .on('mouseover', (d) => {
                this._highlightLinks(d.target);
            })
            .on('mouseout', () => {
                if (this.config.external.breadcrumb) {
                    eval(this.config.external.breadcrumb + ' = []');
                }
                d3.select('#links')
                    .selectAll('path')
                    .attr('style', null);
            });
        link
            .transition()
            .duration(this.config.duration)
            .attr('d', (d) => {
                if (d.source.depth === 0) {
                    return straight(d);
                } else {
                    return diagonal(d);
                }
            });
        link.exit()
            .transition()
            .duration(this.config.duration)
            .attr('d', (d) => {
                const o = {
                    'x': source.x,
                    'y': source.y
                };
                const vector = {
                    'source': o,
                    'target': o
                };
                if (d.source.depth === 0) {
                    return straight(vector);
                } else {
                    return diagonal(vector);
                }
            })
            .remove();
    }

    _updateNodes(nodes, source) {
        const node = d3.select('#nodes')
            .selectAll('circle')
            .data(nodes, (d) => {
                return d.id;
            });
        node.enter()
            .append('circle')
            .attr('id', (d) => {return d.entry})
            .attr('transform', () => {
                return 'rotate(' + (source.x0 - 90) + '),translate(' + source.y0 + ')';
            })
            .attr('r', 0.5)
            .attr('fill', (d) => {
                return d._children ? '#ddd' : '#fff';
            })
            .attr('stroke', '#999')
            .attr('stroke-width', 0.25)
            .attr('cursor', 'pointer')
            .attr('data-toggle', 'tooltip')
            .attr('data-original-title', this._makeNodeTitle)
            .on('click', (d) => {
                this._collapseChildren(d);
                this.update(d);
            })
            .on('mouseover', (d) => {
                d3.select(d3.event.target)
                    .style('r', 1)
                    .style('fill', '#000')
                    .style('opacity', 0.5);
                this._highlightLinks(d);
            })
            .on('mouseout', () => {
                if (this.config.external.breadcrumb) {
                    eval(this.config.external.breadcrumb + ' = []');
                }
                d3.select(d3.event.target)
                    .attr('style', null);
                d3.select('#links')
                    .selectAll('path')
                    .attr('style', null);
            }).on('contextmenu', (d) => {
            	if (this.config.external.entry) {
            		eval(this.config.external.entry + ' = d.entry');
            	}
            	// get a pointer to the FuncTree instance
            	const self = this
            	// get the id of the triggering node
            	const nodeId = d3.event.target.id
            	
            	// create an array of actions for the context menu
            	const actions = [{
        			name: 'Copy',
        			iconClass: 'fa-clipboard',
        			onClick: function(){
        				setClipboard(d.entry);
        			}
        		}, {
        			name: 'Set as root',
        			iconClass: 'fa-undo',
        			onClick: function() {
                        $("#form-entry-detail input[name=root]").val(d.entry);
        				$("#form-entry-detail").submit();
        			}
        		}]
            	
            	if(!isModuleUndefinedNode(nodeId, "KEGG")){
            		// Toggle/Untoggle labels for unlabeled nodes
                	if (d.depth >= this.config.labelMinDepth) {
                		actions.push({
                    		name: 'Toggle label',
                    		iconClass: 'fa-toggle-off',
                    		onClick: function() {
                    			const selectedLabel = d3.select('#label-' + nodeId)
                    			if (selectedLabel.empty()) {
                    				const selectedNode = d3.select('#' + nodeId)
                    				const text = d3.select("#labels")
                    				.append('g')
                    				.attr('id', 'label-' + nodeId)
                    				.attr('transform', selectedNode .attr("transform"))
                    				.append('text')
                    				.attr('text-anchor', 'middle')
                    				.attr('font-family', 'arial, sans-serif')
                    				.attr('font-size', 4)
                    				.attr('fill', '#555')
                    				.text(selectedNode.attr("data-original-title").replace(/\[.*\] /, ''))
                    				// add drag behavior
                    				text.call(d3.behavior.drag()
                    						.on('dragstart', () => {
                    							d3.event.sourceEvent.stopPropagation();
                    						})
                    						.on('drag', function(d) {
                    							d3.select(this)
                    							.attr('y', 0)
                    							.attr('transform', 'translate(' + d3.event.x + ',' + d3.event.y + ')');
                    						})
                    				);

                    			} else {
                    				selectedLabel.remove()
                    			}
                    		}
                		})
                	}	
            	}
            	
            	// check node id eligible for View Details actions
            	if (hasMoreDetails(nodeId, "KEGG")) {
            		actions.push({
            			name: 'View details',
            			iconClass: 'fa-info',
            			onClick: function() {
            				axios.get(self.infoServiceURL + d.entry)
                                .then(function(res) {
                                    vmEntryDetail.detail = res.data;
                                })
                                .catch(function(error) {
                                    if (error.response.status === 404) {
                                        vmEntryDetail.detail = 'No information available';
                                    } else {
                                        vmEntryDetail.detail = 'Ajax error';
                                    }
                                });
                                $('#modal-entry-detail').modal('show');
            			    }
            		})
            		
            		actions.push({
            			name: 'View in KEGG',
            			iconClass: 'fa-eye',
            			onClick: function() {
            				var url = resolveExternalURL(nodeId, "KEGG")
            				window.open(url, '_blank');
            			}
            		})            		
            	}
            	//escape space in the selector
            	const menu = new BootstrapMenu("#"+nodeId.replace(/([ &,;:\+\*\(\)\[\]])/g, '\\$1'), {
            		actions: actions
            	}); 
            	return false;
            });
        node
            .transition()
            .duration(this.config.duration)
            .attr('fill', (d) => {
                return d._children ? '#ddd' : '#fff';
            })
            .attr('transform', (d) => {
                return 'rotate(' + (d.x - 90) + '),translate(' + d.y + ')';
            });
        node.exit()
            .transition()
            .duration(this.config.duration)
            .attr('r', 0)
            .attr('transform', () => {
                return 'rotate(' + (source.x - 90) + '),translate(' + source.y + ')';
            })
            .remove();
    }

    _updateBars(nodes, source, depth, maxSumOfValues, maxMaxOfValues) {
        const self = this;
        const data = nodes
            .filter((d) => {
                return d.depth > 0;
            });
        const barWidth = d3.scale.linear()
            .domain([4, 0])
            .range([1.5, 5]);
        const chart = d3.select('#charts')
            .selectAll('g')
            .data(data, (d) => {
                return d.id;
            });
        chart.enter()
            .append('g')
            .attr('transform', 'rotate(' + (source.x0 - 90) + '),translate(' + source.y0 + '),rotate(-90)')
            .attr('data-toggle', 'tooltip')
            .attr('data-original-title', this._makeNodeTitle)
            .on('click', (d) => {
                this._collapseChildren(d);
                this.update(d);
            })
            .on('mouseover', (d) => {
                if (this.config.external.entry) {
                    eval(this.config.external.entry + ' = d.entry');
                }
                this._highlightLinks(d);
            })
            .on('mouseout', () => {
                if (this.config.external.breadcrumb) {
                    eval(this.config.external.breadcrumb + ' = []');
                }
                d3.select('#links')
                    .selectAll('path')
                    .attr('style', null);
            });
        chart
            .transition()
            .duration(this.config.duration)
            .attr('transform', (d) => {
                return 'rotate(' + (d.x - 90) + '),translate(' + d.y + '),rotate(-90)';
            });
        chart.exit()
            .transition()
            .duration(this.config.duration)
            .attr('transform', 'rotate(' + (source.x - 90) + '),translate(' + source.y + '),rotate(-90)')
            .remove();
        
        const bar = chart
            .selectAll('rect')
            .data((d) => {
                return d.values;
            });
        bar.enter()
            .append('rect')
            .attr('x', function(d) {
                const p = this.parentNode.__data__;
                return - barWidth(p.depth) / 2;
            })
            .attr('y', 0)
            .attr('rx', function(d) {
                const p = this.parentNode.__data__;
                return barWidth(p.depth) / 4;
            })
            .attr('ry', function(d) {
                const p = this.parentNode.__data__;
                return barWidth(p.depth) / 4;
            })
            .attr('width', function(d) {
                const p = this.parentNode.__data__;
                return barWidth(p.depth);
            })
            .attr('height', 0)
            .attr('fill', function(d, i) {
                const n = self.config._selectedColumns.multiple[i];
                return self.config.colorSet[n] || self.colorScale('column-' + n);
            })
            .on('mouseover', () => {
                d3.select(d3.event.target)
                    .style('fill', '#000')
                    .style('opacity', 0.5);
            })
            .on('mouseout', () => {
                d3.select(d3.event.target)
                    .attr('style', null);
            });
        bar
            .transition()
            .duration(this.config.duration)
            .attr('y', function(d, i) {
                const p = this.parentNode.__data__;
                const maxHight = self.config.diameter / 2 / depth * 0.8;
                const sum = d3.sum(p.values);
                const subSum = d3.sum(p.values.slice(0, i));
                if (self.config.percentage) {
                    return subSum / sum * maxHight || 0;
                } else if (self.config.normalize) {
                    return subSum / maxSumOfValues[p.depth] * maxHight || 0;
                } else {
                    return subSum;
                }
            })
            .attr('height', function(d) {
                const p = this.parentNode.__data__;
                const sum = d3.sum(p.values);
                const maxHight = self.config.diameter / 2 / depth * 0.8;
                if (self.config.percentage) {
                    return d / sum * maxHight || 0;
                } else if (self.config.normalize) {
                    return d / maxSumOfValues[p.depth] * maxHight || 0;
                } else {
                    return d;
                }
            })
            .attr('fill', function(d, i) {
                const n = self.config._selectedColumns.multiple[i];
                return self.config.colorSet[n] || self.colorScale('column-' + n);
            });
        bar.exit()
            .transition()
            .duration(this.config.duration)
            .attr('y', 0)
            .attr('height', 0)
            .remove();
    }

    _updateRounds(nodes, source, depth, max) {
        const data = nodes
            .filter((d) => {
                return d.depth > 0;
            });
        const circle = d3.select('#rounds')
            .selectAll('circle')
            .data(data, (d) => {
                return d.id;
            });
        circle.enter()
            .append('circle')
            .attr('transform', () => {
                return 'rotate(' + (source.x0 - 90) + '),translate(' + source.y0 + ')';
            })
            .attr('r', 0)
            .attr('fill', (d) => {
                let color;
                switch (this.config.colorizeBy) {
                    case 'layer':
                        color = this.config.colorSet[d.layer] || this.colorScale(d.layer);
                        break;
                    case 'entry':
                        color = this.config.colorSet[d.entry] || this.config.colorSet.default;
                        break;
                    case 'column':
                        const n = this.config._selectedColumns.single;
                        color = this.config.colorSet[n] || this.colorScale('column-' + n);
                        break;
                    default:
                        color = this.config.colorSet.default;
                }
                return color;
            })
            .attr('stroke', '#fff')
            .attr('stroke-width', 0.5)
            .attr('opacity', 0.75)
            .attr('data-toggle', 'tooltip')
            .attr('data-original-title', this._makeNodeTitle)
            .on('click', (d) => {
                this._collapseChildren(d);
                this.update(d);
            })
            .on('mouseover', (d) => {
                if (this.config.external.entry) {
                    eval(this.config.external.entry + ' = d.entry');
                }
                d3.select(d3.event.target)
                    .style('fill', '#000')
                    .style('opacity', 0.5);
                this._highlightLinks(d);
            })
            .on('mouseout', () => {
                if (this.config.external.breadcrumb) {
                    eval(this.config.external.breadcrumb + ' = []');
                }
                d3.select(d3.event.target)
                    .attr('style', null);
                d3.select('#links')
                    .selectAll('path')
                    .attr('style', null);
            });
        circle
            .transition()
            .duration(this.config.duration)
            .attr('r', (d) => {
                const r_ = 25;
                if (this.config.normalize) {
                	var radius = null;
                	// map to Area
                	if(this.config.circleMapToArea){
                		var scaledArea = d.value / max[d.depth]
                		radius = Math.sqrt(scaledArea/Math.PI)
                	// map to radius
                	} else {
                		radius = d.value / max[d.depth];
                	}
                	return radius * r_ || 0;
                } else {
                    return this.config.circleMapToArea? Math.sqrt(d.value/Math.PI) : d.value;
                }
            })
            .attr('transform', (d) => {
                return 'rotate(' + (d.x - 90) + '),translate(' + d.y + ')';
            })
            .attr('fill', (d) => {
                let color;
                switch (this.config.colorizeBy) {
                    case 'layer':
                        color = this.config.colorSet[d.layer] || this.colorScale(d.layer);
                        break;
                    case 'entry':
                        color = this.config.colorSet[d.entry] || this.config.colorSet.default;
                        break;
                    case 'column':
                        const n = this.config._selectedColumns.single;
                        color = this.config.colorSet[n] || this.colorScale('column-' + n);
                        break;
                    default:
                        color = this.config.colorSet.default;
                }
                return color;
            });
        circle.exit()
            .transition()
            .duration(this.config.duration)
            .attr('r', 0)
            .attr('transform', () => {
                return 'rotate(' + (source.x - 90) + '),translate(' + source.y + ')';
            })
            .remove();
    }

    _updateLabels(nodes, source, maxValue, maxSumOfValues) {
        const data = nodes
            .filter((d) => {
                return 0 < d.depth && d.depth < this.config.labelMinDepth;
            })
            .filter((d) => {
                return !d.name.startsWith('*');
            });
        const label = d3.select('#labels')
            .selectAll('g')
            .data(data, (d) => {
                return d.id;
            });
        const fontSize = d3.scale.linear()
            .domain([3, 0])
            .range([4, 8]);
        label.enter()
            .append('g')
            .attr('transform', (d) => {
                return 'rotate(' + (source.x0 - 90) + '),translate(' + source.y0 + '),rotate(' + (90 - source.x0) + ')';
            })
            .append('text')
            .attr('text-anchor', 'middle')
            .attr('font-family', 'arial, sans-serif')
            .attr('font-size', (d) => {
                return fontSize(d.depth);
            })
            .attr('y', (d) => {
                return - fontSize(d.depth) / 2;
            })
            .attr('fill', '#555')
            .text((d) => {
                return d.name.replace(/ \[.*\]/, '');
            });
        /*
        node.append("text")
        .attr("dy", "0.31em")
        .attr("x", function(d) { return d.x < Math.PI === !d.children ? 6 : -6; })
        .attr("text-anchor", function(d) { return d.x < Math.PI === !d.children ? "start" : "end"; })
        .attr("transform", function(d) { return "rotate(" + (d.x < Math.PI ? d.x - Math.PI / 2 : d.x + Math.PI / 2) * 180 / Math.PI + ")"; })
        .text(function(d) { return d.id.substring(d.id.lastIndexOf(".") + 1); });*/
        
        label
            .transition()
            .duration(this.config.duration)
            .attr('transform', (d) => {
                return 'rotate(' + (d.x - 90) + '),translate(' + d.y + '),rotate(' + (90 - d.x) + ')';
            });
        label.exit()
            .transition()
            .duration(this.config.duration)
            .attr('transform', (d) => {
                return 'rotate(' + (source.x - 90) + '),translate(' + source.y + '),rotate(' + (90 - source.x) + ')';
            })
            .remove();
        label.selectAll('text')
            .call(d3.behavior.drag()
                .on('dragstart', () => {
        	    	d3.event.sourceEvent.stopPropagation();
        	    })
                .on('drag', function(d) {
                    d3.select(this)
                        .attr('y', 0)
                        .attr('transform', 'translate(' + d3.event.x + ',' + d3.event.y + ')');
                })
            );
    }

    /**
     * Returns a clean title for the tooltip with PATH, BR information stripped from modules names
     */
    _makeNodeTitle(d){
    	var title = d.name.replace(/ \[PATH:.*\]$/, '');
    	if(d.entry != d.name) {
    		title = '[' + d.entry + '] ' + title
    	}
        return title;
    }
    
    search(word) {
        const node = d3.select('#nodes')
            .selectAll('circle');
        const hits = node
            .filter((d) => {
                return d.entry === word;
            });
        hits.style('fill', '#f00')
        	.style('stroke', '#f00')
            .style('opacity', 0.5)
            .transition()
            .duration(1000)
            .style('r', 50)
            .style('stroke-width', 50)
            .style('opacity', 0)
            .each('end', function() {
                d3.select(this)
                    .attr('style', null);
            });
        if (!hits[0].length) {
            alert('No results found from displayed entries: ' + word);
        }
    }


    getNodes(node=this.root, nodes=[], depth=0) {
        node.depth = depth;
        nodes.push(node);
        for (const node of (node.children || node._children || [])) {
            this.getNodes(node, nodes, depth + 1);
        }
        return nodes;
    }

    _collapseChildren(node) {
        if (node.children) {
            node._children = node.children;
            node.children = null;
        } else if (node._children) {
            node.children = node._children;
            node._children = null;
        }
    }

    _highlightLinks(node) {
        d3.selectAll('path')
            .filter((d) => {
                if (d.target.id === node.id) {
                    return true;
                }
            })
            .style('stroke', (d) => {
                return this.config.colorSet[d.target.layer] || this.colorScale(d.target.layer);
            })
            .style('stroke-width', 1.5);
        if (this.config.external.breadcrumb) {
            eval(this.config.external.breadcrumb + '.unshift(node.entry)');
        }
        if (node.parent) {
            this._highlightLinks(node.parent);
        }
    }
}

/**
 * A function to check if a node has more details.
 * For KEGG only K, Module, and map elements have more details
 * @param nodeId
 * @param referenceDatabase
 * @returns
 */
function hasMoreDetails(nodeId, referenceDatabase){
	let hasMoreDetails = false;
	if (referenceDatabase == "KEGG") {
		if (nodeId.match(/^(K|M|map)[0-9]{5}/)) {
			hasMoreDetails = true
		}
	}
	return hasMoreDetails
}

function isModuleUndefinedNode(nodeId, referenceDatabase){
	let truth = false;
	if (referenceDatabase == "KEGG") {
		if (nodeId.match(/^\*map[0-9]{5}/)) {
			truth = true
		}
	}
	return truth
}

function resolveExternalURL(nodeId, referenceDatabase){
	let url = null;
	if (referenceDatabase == "KEGG") {
		if (nodeId.match(/K[0-9]{5}/)) {
			url = "https://www.genome.jp/dbget-bin/www_bget?ko+" + nodeId
		} else if (nodeId.match(/M[0-9]{5}/)){
			url = "https://www.genome.jp/kegg-bin/show_module?" + nodeId
		} else if (nodeId.match(/map[0-9]{5}/)) {
			url = "https://www.genome.jp/kegg-bin/show_pathway?" + nodeId
		}
	}
	return url
}

function mergeRecursive(obj1, obj2) {
    for (var p in obj2) {
        try {
            if (obj2[p].constructor == Object) {
                obj1[p] = mergeRecursive(obj1[p], obj2[p]);
            } else {
                obj1[p] = obj2[p];
            }
        } catch (e) {
            obj1[p] = obj2[p];
        }
    }
    return obj1;
}


function zoomed(zoom) {
	var svg = d3.select("#buffer").attr({
		'transform': "translate(" + zoom.translate() + ")," + "scale(" + zoom.scale() + ")"
	});
}

function interpolateZoom (translate, scale, zoom) {
    var self = this;
    return d3.transition().duration(350).tween("zoom", function () {
        var iTranslate = d3.interpolate(zoom.translate(), translate),
            iScale = d3.interpolate(zoom.scale(), scale);
        return function (t) {
            zoom
                .scale(iScale(t))
                .translate(iTranslate(t));
            zoomed(zoom);
        };
    });
}

function zoomClick(zoom, config) {

	const clicked = d3.event.target
	const width = config.viewBoxWidth
	const height = config.viewBoxHeight
	if(clicked.id === 'zoom_reset') {
		return interpolateZoom([width / 2, height / 2], 1, zoom)
	}
	
    var direction = 1,
        factor = 0.2,
        target_zoom = 1,
        center = [width / 2, height / 2],
        extent = zoom.scaleExtent(),
        translate = zoom.translate(),
        translate0 = [],
        l = [],
        view = {x: translate[0], y: translate[1], k: zoom.scale()};
	
    d3.event.preventDefault();
    direction = (clicked.id === 'zoom_in') ? 1 : -1;
    target_zoom = zoom.scale() * (1 + factor * direction);

    if (target_zoom < extent[0] || target_zoom > extent[1]) { return false; }

    translate0 = [(center[0] - view.x) / view.k, (center[1] - view.y) / view.k];
    view.k = target_zoom;
    l = [translate0[0] * view.k + view.x, translate0[1] * view.k + view.y];

    view.x += center[0] - l[0];
    view.y += center[1] - l[1];
    
    interpolateZoom([view.x, view.y], view.k, zoom);
}

/**
 * Matcher for the typeahead plugin
 * @param strs
 * @returns
 */
var substringMatcher = function (strs) {
	return function findMatches(q, cb) {
		// an array that will be populated with substring matches
		var matches = [];
		// regex used to determine if a string contains the substring `q`
		var substrRegex = new RegExp(q, 'i');

		// iterate through the pool of strings and for any string that
		// contains the substring `q`, add it to the `matches` array
		$.each(strs, function(i, str) {
			if (substrRegex.test(str)) {
				matches.push(str);
			}
		});
		cb(matches);
	};
};
