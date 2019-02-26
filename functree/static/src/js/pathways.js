'use strict';

const visualize = (profile, columns, column, color, width, map) => {

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
        	return x.name + ' ' + color + ' W' + width
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
