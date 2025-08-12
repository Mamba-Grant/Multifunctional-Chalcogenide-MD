import { baseApi } from "$lib/api";

export async function fetchBandData(item) {
    const res = await fetch(
        `${baseApi}/get_plotinfo_from_hash?hash=${item.hash}`,
    );
    let data = await res.json()

    return data
}

const baseBandsLayout = {
    showlegend: false,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 40, r: 5, t: 20, b: 40 },
    xaxis: {
        linewidth: 0,
        tickmode: "array",
        showticklabels: true,
        showgrid: false,
        ticks: "",
        title: {
            text: "k-points",
            font: {
                size: 18,
            },
        },
    },
    yaxis: { linewidth: 0 },
};

const baseDosLayout = {
    showlegend: false,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 5, r: 20, t: 20, b: 40 },
    xaxis: { linewidth: 0 },
    yaxis: {
        linewidth: 0,
        ticks: "",
        nticks: 0,
        showticklabels: false,
    },
};

export function getBandsLayout(containerHeight, bandWidth) {
    let layout = {
        ...baseBandsLayout,
        height: containerHeight || 500,
        width: bandWidth || 350,
        yaxis: {
            title: {
                text: "E - E<sub>F</sub> [eV]",
                font: {
                    size: 18,
                },
            },
        },
    };
    return layout
}

export function getDosLayout(containerHeight, dosWidth) {
    let dosLayout = {
        ...baseDosLayout,
        height: containerHeight || 500,
        width: dosWidth || 200,
    };

    return dosLayout

}
