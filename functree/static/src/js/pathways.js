'use strict';

const visualize = (profile, columns, column) => {

    /** iPath */
    {
        const data = profile;
        const seriesData = data.map((x) => {
            x.name = x.entry;
            x.y = x.values[column];
            return x;
        });
        const selection = seriesData.filter((x) => {
            // let layers = ['pathway', 'module', 'ko'];
            let layers = ['ko'];
            return ~layers.indexOf(x.layer);
        }).map((x) => {
            x = x.name;
            return x;
        }).join('\n');

        const params = {
            'selection': selection,
            'default_opacity': 1,
            'default_width': 3,
            'default_radius': 7,
            'default_color': '#aaaaaa',
            'tax_filter': '',
            'map': 'metabolic',
            'export_type': 'svg',
            'export_dpi': 10
        };

        const form = $('<form/>', {'action': 'https://pathways.embl.de/ipath3.cgi', 'method': 'POST', 'target': 'ipath'}).hide();
        for (name in params) {
            form.append($('<input/>', {'type': 'hidden', 'name': name, 'value': params[name]}));
        }
        form.appendTo(document.body).submit().remove();
    }

};
