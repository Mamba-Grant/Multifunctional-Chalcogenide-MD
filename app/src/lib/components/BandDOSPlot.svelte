<script lang="ts">
    import { onMount } from "svelte";
    import { dev } from "$app/environment";
    import Page from "../../routes/+page.svelte";

    export let item; // inherit the data table entry we're looking at -- grab the hash and query the database for the actual data later

    let plotCanvas: HTMLElement;
    let plotDiv_Band: HTMLElement;
    let plotDiv_DOS: HTMLElement;

    // Bind width and height reactively from parent container
    let containerWidth = 0;
    let containerHeight = 0;

    // Plotly data and layout stores
    let bandsTraces = [];
    let dosTraces = [];
    let bandsLayout = {};
    let dosLayout = {};

    // Track if plots are initialized
    let plotsInitialized = false;

    // Load Plotly once
    function loadPlotly() {
        if ((window as any).Plotly) return Promise.resolve();
        return new Promise((resolve, reject) => {
            const script = document.createElement("script");
            script.src = "https://cdn.plot.ly/plotly-3.0.1.min.js";
            script.onload = () => resolve();
            script.onerror = () =>
                reject(new Error("Failed to load Plotly.js"));
            document.body.appendChild(script);
        });
    }

    // Reactive sizing: Calculate plot widths based on container width
    $: bandWidth = Math.floor(containerWidth * 0.7);
    $: dosWidth = containerWidth - bandWidth;

    // Reactive layouts updated on size change
    $: if (plotsInitialized) {
        const Plotly = (window as any).Plotly;
        if (Plotly) {
            Plotly.relayout(plotDiv_Band, {
                width: bandWidth,
                height: containerHeight,
            });
            Plotly.relayout(plotDiv_DOS, {
                width: dosWidth,
                height: containerHeight,
            });
        }
    }

    async function initializePlots() {
        await loadPlotly();

        const Plotly = (window as any).Plotly;
        const baseApi = dev ? "http://127.0.0.1:8000/api" : "/api";

        const res = await fetch(
            `${baseApi}/get_plotinfo_from_hash?hash=${item.hash}`,
        );
        const data = await res.json();

        const bands = data.bands;
        const distances = data["band distances"].flat();
        const ticks = data.KPoints;

        // Construct band traces
        const numBands = bands[0].length;
        bandsTraces = Array.from({ length: numBands }, (_, j) => ({
            x: distances,
            y: [].concat(...bands.map((segment: number[]) => segment[j])),
            type: "scatter",
            mode: "lines",
            name: `Band ${j}`,
        }));

        // DOS traces
        dosTraces = [
            {
                x: data["total density of states"],
                y: data["density of states energies"],
                type: "scatter",
                mode: "lines",
            },
        ];

        // Layout shared config
        const baseBandsLayout = {
            showlegend: false,
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)",
            margin: { l: 40, r: 5, t: 20, b: 40 },
            xaxis: {
                linewidth: 0,
                tickmode: "array",
                tickvals: ticks.distance,
                ticktext: ticks.label,
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

        bandsLayout = {
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

        dosLayout = {
            ...baseDosLayout,
            height: containerHeight || 500,
            width: dosWidth || 200,
        };

        // Initialize plots
        await Plotly.newPlot(plotDiv_Band, bandsTraces, bandsLayout, {
            displaylogo: false,
            responsive: false,
        });
        await Plotly.newPlot(plotDiv_DOS, dosTraces, dosLayout, {
            displaylogo: false,
            responsive: false,
        });

        plotsInitialized = true;
    }

    // Create an observer to get the area to plot in -- reactive variables don't work here...
    onMount(() => {
        if (!plotCanvas?.parentElement) return;

        const ro = new ResizeObserver((entries) => {
            for (const entry of entries) {
                containerWidth = entry.contentRect.width;
                containerHeight = entry.contentRect.height;
            }
        });

        ro.observe(plotCanvas.parentElement);
        initializePlots();
        return () => ro.disconnect();
    });
</script>

<div
    bind:this={plotCanvas}
    id="plotly"
    class="flex flex-row gap-0 w-full h-full"
>
    <div bind:this={plotDiv_Band} id="plotDiv_Band" class="m-0 p-0"></div>
    <div bind:this={plotDiv_DOS} id="plotDiv_DOS" class="m-0 p-0"></div>
</div>
