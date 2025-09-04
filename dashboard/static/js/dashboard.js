function getCssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function parseRgb(rgbStr) {
    const [r,g,b] = rgbStr.match(/\d+/g).map(Number);
    return { r, g, b };
}

function rgbToString({r,g,b}) {
    return `rgb(${r},${g},${b})`;
}

/**
 * Generade a shade from a base color. Factor > 1 → lighter, Factor < 1 → darker
 * @param { string } rgbStr base color as "rgb()" string
 * @param { number} factor between 0 and 2 e.g. 1.5 or 0.5
 * @returns { string } New shade as "rgb()" string
 */
function shadeColor(rgbStr, factor) {
    let {r,g,b} = parseRgb(rgbStr);
    r = Math.min(255, Math.max(0, r * factor));
    g = Math.min(255, Math.max(0, g * factor));
    b = Math.min(255, Math.max(0, b * factor));
    return rgbToString({r, g, b});
}

function getColor(colorString) {
    if (Object.keys(colors).includes(colorString)) return colors[colorString];
    return colorString;
}

// E-ink optimised
const colors = {
    red: getCssVar('--red'),
    green: getCssVar('--green'),
    blue: getCssVar('--blue'),
    yellow: getCssVar('--yellow'),
    orange: getCssVar('--orange'),
    black: getCssVar('--black'),
    white: getCssVar('--white'),
    darkGrey: getCssVar('--dark-grey'),
    grey: getCssVar('--grey'),
    lightGrey: getCssVar('--light-grey'),
    lightBlue: getCssVar('--light-blue'),
    purple: getCssVar('--purple'),
    bg: getCssVar('--bg'),
    bgCard: getCssVar('--bg-card'),
    border: getCssVar('--border'),
    borderMedium: getCssVar('--border-medium'),
    borderLight: getCssVar('--border-light'),
};

Chart.defaults.backgroundColor = colors.white;
Chart.defaults.scale.grid.color = colors.borderLight;
Chart.defaults.plugins.legend.display = false;

const mapIdToYOptions = {
    "memory": {
        ticks: {
            callback: function (value,index, ticks) {
                return ((value ?? 0) / 1000000000).toFixed(1)
            }
        }
    },
    "cpu": {
        ticks: {
            callback: function (value,index, ticks) {
                return (value).toFixed() + "%"
            }
        }
    },
    "network": undefined,
}

const defaultOptions = { 
    animation: false,
    devicePixelRatio: 1,
    responsive: true,
};

// Disk graphs, json injectec by django
const disks = JSON.parse(document.getElementById("disks-graph-data").textContent);
const diskBackgroundColor = [colors.green, shadeColor(colors.green,1.5)];
for (const d of disks.disks) {
    const data = {
        datasets: [
            {
                data: [d.disk_used_percent, d.disk_unused_percent],
                backgroundColor: diskBackgroundColor,
            },
        ],
    };
    new Chart(
        document.getElementById(`disk-canvas-${d.id}`),
        {
            type: 'doughnut',
            data,
            options: defaultOptions,
        },
    );
}
// Usage graphs
const systemStats = {
    mem: JSON.parse(document.getElementById("memory-graph-data").textContent),
    cpu: JSON.parse(document.getElementById("cpu-graph-data").textContent),
    network: JSON.parse(document.getElementById("network-graph-data").textContent),
}

for (const stats of Object.values(systemStats)) {
    for (const graphData of stats.graph_data) {
        const graphId = `stat-graph-canvas-${ stats.stat_id_and_grid }-${graphData.id}`
        const data = {
            labels: graphData.labels,
            datasets: [{
                data: graphData.values,
                borderColor: getColor(graphData.color),
            }]
        };
        const specificOptions = {
            ...defaultOptions, 
            pointStyle: false,
            scales: {
                y: mapIdToYOptions[stats.stat_id_and_grid],
            },
        };

        new Chart(
            document.getElementById(graphId),
            {
                type: 'line',
                data,
                options: specificOptions,
            },
        );
    }

}