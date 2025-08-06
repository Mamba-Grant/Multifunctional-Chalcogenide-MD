<script lang="ts">
    import { onMount } from "svelte";

    export let item;

    function loadPlotly(): Promise<void> {
        return new Promise((resolve, reject) => {
            if ((window as any).Plotly) {
                resolve(); // already loaded
                return;
            }
            const script = document.createElement("script");
            script.src = "https://cdn.plot.ly/plotly-3.0.1.min.js";
            script.onload = () => resolve();
            script.onerror = () =>
                reject(new Error("Failed to load Plotly.js"));
            document.body.appendChild(script);
        });
    }

    const layout_bands_dos = {
        showlegend: false,
        paper_bgcolor: "rgba(0,0,0,0)",
        width: 700,
        height: 700,
    };

    onMount(async () => {
        await loadPlotly();

        const plotDiv_BandDOS = document.getElementById("plotDiv_BandDOS");
        if (plotDiv_BandDOS && (window as any).Plotly) {
            (window as any).Plotly.newPlot(
                plotDiv_BandDOS,
                // plot_data_bands_dos,
                layout_bands_dos,
                {
                    displaylogo: false,
                },
            );
        }

        const res = await fetch(
            `http://localhost:8000/v1/material_data/dos_from_hash?hash=${item.hash}`,
        );
        const data = await res.json();
        console.log(data);
    });

    let plot_data;
</script>

<!-- /dos_from_hash -->
<!-- Band structure, DOS, etc. -->
