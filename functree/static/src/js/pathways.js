'use strict';

const visualize = (profile, columns, column, cutoff, color, opacity, width, map) => {

    /** iPath */
    {
    	// select the 
        var seriesData = profile.filter((x) => {
            // let layers = ['pathway', 'module', 'ko'];
            let layers = ['ko'];
            // Match KO layer and ensure that the value is above > cutoff
            return ~layers.indexOf(x.layer) && x.values[column] > cutoff;
        })
        
        // a function that always return the same color
        var colorGradient = (x) => {return color}
        // if color is null then define a colorGradient
        if(color == null){
        	var seriesValues = seriesData.map((x) => {return x.values[column]})
            colorGradient = d3.scale.linear()
            	.domain(d3.extent(seriesValues))
        		.range([d3.rgb(255, 128, 14), d3.rgb(171, 171, 171)])
        		.interpolate(d3.interpolateHcl);
        }
        // generate the selection for iPath 
        var selection = seriesData.map((x) => {
        	return x.entry + ' ' + colorGradient(x.values[column]) + ' W' + (width) + ' ' + opacity
        }).join('\n');
        // add default parameters
        var params = {
            'selection': selection,
            'default_opacity': 1,
            'default_width': 3,
            'default_radius': 7,
            'default_color': '#aaaaaa',
            'background_color':'#ffffff',
            'tax_filter': '',
            'map': map
        };
        // attach a form
        var form = $('<form/>', {'action': 'https://pathways.embl.de/ipath3.cgi', 'method': 'POST', 'target': 'ipath'}).hide();
        // append form parameters
        for (var name in params) {
            form.append($('<input/>', {'type': 'hidden', 'name': name, 'value': params[name]}));
        }
        // submit the form
        form.appendTo(document.body).submit().remove();
    }
};

// color picker for ipath submission
Vue.component('colorpicker', {
	components: {
		'chrome-picker': VueColor.Chrome,
	},
	template: `
<div class="input-group color-picker" ref="colorpicker">
	<input type="text" class="form-control" v-model="colorValue.hex" @focus="showPicker()" @input="updateFromInput" />
	<span class="input-group-addon color-picker-container">
		<span class="current-color" :style="'background-color: ' + colorValue.hex + '; opacity:' + colorValue.a + ';'" @click="togglePicker()"></span>
		<chrome-picker :value="colors" @input="updateFromPicker" v-if="displayPicker" />
	</span>
</div>`,
	props: ['color'],
	data() {
		return {
			colors: {
				hex: '#FF800E',
				a: 1
			},
			colorValue: '',
			displayPicker: false,
		}
	},
	mounted() {
		this.setColor(this.color || {hex: '#FF800E', a: 1});
	},
	methods: {
		setColor(color) {				
			this.updateColors(color);
			this.colorValue = color;
		},
		updateColors(color) {
			this.colors = color
		},
		showPicker() {
			document.addEventListener('click', this.documentClick);
			this.displayPicker = true;
		},
		hidePicker() {
			document.removeEventListener('click', this.documentClick);
			this.displayPicker = false;
		},
		togglePicker() {
			this.displayPicker ? this.hidePicker() : this.showPicker();
		},
		updateFromInput() {
			this.updateColors(this.colorValue.hex);
		},
		updateFromPicker(color) {
			this.colors = color;
			this.colorValue = color;
		},
		documentClick(e) {
			var el = this.$refs.colorpicker,
				target = e.target;
			if(el !== target && !el.contains(target)) {
				this.hidePicker()
			}
		}
	},
	watch: {
		colorValue(val) {
			if(val) {
				this.updateColors(val);
				this.$emit('input', val);
			}
		}
	},
});