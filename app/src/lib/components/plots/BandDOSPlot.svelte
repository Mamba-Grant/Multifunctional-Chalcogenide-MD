<script lang="ts">
    import { onMount } from "svelte";
    import { loadPlotly } from "$lib/plotlyLoader";
    import {
        fetchBandData,
        getBandsLayout,
        getDosLayout,
    } from "$lib/components/plots/plotUtils";

    export let item; // inherit the data table entry we're looking at -- grab the hash and query the database for the actual data later

    let plotCanvas: HTMLElement;
    let plotDiv_Band: HTMLElement;
    let plotDiv_DOS: HTMLElement;

    let containerWidth = 0;
    let containerHeight = 0;
    let bandsTraces = [];
    let dosTraces = [];
    let plotsInitialized = false;

    $: bandWidth = Math.floor(containerWidth * 0.7);
    $: dosWidth = containerWidth - bandWidth;

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
        const data = await fetchBandData(item);
        const distances = data["band distances"].flat();
        const numBands = data.bands[0].length;

        bandsTraces = Array.from({ length: numBands }, (_, j) => ({
            x: distances,
            y: [].concat(...data.bands.map((segment: number[]) => segment[j])),
            type: "scatter",
            mode: "lines",
            name: `Band ${j}`,
        }));

        dosTraces = [
            {
                x: data["total density of states"],
                y: data["density of states energies"],
                type: "scatter",
                mode: "lines",
            },
        ];

        let dosLayout = getDosLayout(containerHeight, dosWidth);
        let bandsLayout = getBandsLayout(containerHeight, bandWidth);

        await Plotly.newPlot(
            plotDiv_Band,
            bandsTraces,
            {
                ...bandsLayout,
                axis: {
                    tickvals: data.KPoints.distance,
                    ticktext: data.KPoints.label,
                },
            },
            {
                displaylogo: false,
                responsive: false,
            },
        );

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
