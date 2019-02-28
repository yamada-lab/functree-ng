'use strict';

const visualize = (profile, columns, column, color, opacity, width, map) => {

    /** iPath */
    {
        const seriesData = profile.map((x) => {
            x.name = x.entry;
            x.y = x.values[column];
            return x;
        });
        
        const selection = seriesData.filter((x) => {
            // let layers = ['pathway', 'module', 'ko'];
            let layers = ['ko'];
            // Match KO layer and ensure that the value is above > 0 
            return ~layers.indexOf(x.layer) && x.y > 0;
        }).map((x) => {
        	return x.name + ' ' + color + ' W' + (width) + ' ' + opacity
        }).join('\n');

        const params = {
            'selection': selection,
            'default_opacity': 1,
            'default_width': 3,
            'default_radius': 7,
            'default_color': '#aaaaaa',
            'background_color':'#ffffff',
            'tax_filter': '',
            'map': map
        };

        const form = $('<form/>', {'action': 'https://pathways.embl.de/ipath3.cgi', 'method': 'POST', 'target': 'ipath'}).hide();
        for (name in params) {
            form.append($('<input/>', {'type': 'hidden', 'name': name, 'value': params[name]}));
        }
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