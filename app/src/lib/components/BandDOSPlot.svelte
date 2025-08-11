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

    const layout_bands = {
        showlegend: false,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        width: 500,
        height: 300,
        margin: {
            // control plot padding inside the container
            l: 40, // left margin, reduce if you want more space
            r: 20, // right margin
            t: 20, // top margin (title area)
            b: 20, // bottom margin (x-axis labels)
        },
        xaxis: {
            linewidth: 0,
            tickmode: "array", // Use an explicit list of ticks
            showticklabels: true, // Show tick labels
            showgrid: false, // Optional: Hide grid lines if needed
            ticks: "", // Optional: Hide tick marks
        },
        yaxis: {
            linewidth: 0,
        },
    };

    const layout_dos = {
        showlegend: false,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        width: 500,
        height: 200,
        margin: {
            l: 40, // left margin, reduce if you want more space
            r: 20, // right margin
            t: 20, // top margin (title area)
            b: 20, // bottom margin (x-axis labels)
        },
        xaxis: {
            linewidth: 0,
        },
        yaxis: {
            linewidth: 0,
        },
    };

    onMount(async () => {
        await loadPlotly();

        const plotDiv_Band = document.getElementById("plotDiv_Band");
        const plotDiv_DOS = document.getElementById("plotDiv_DOS");

        const res = await fetch(
            `/api/get_plotinfo_from_hash?hash=${item.hash}`,
        );

        const data = await res.json();

        console.log(data);

        const bands = data["bands"];
        const distances = data["band distances"];
        const ticks = data["KPoints"];

        const numBands = bands[0].length; // bands[segment][band][point]
        const numSegments = bands.length;
        const allDistances = distances.flat(); // flatten all segments into one array

        const traces_bands = [];
        for (let j = 0; j < numBands; j++) {
            const bandY = [];
            for (let i = 0; i < numSegments; i++) {
                bandY.push(...bands[i][j]);
            }

            traces_bands.push({
                x: allDistances,
                y: bandY,
                type: "scatter",
                mode: "lines",
                name: `Band ${j}`,
            });
        }

        const energy = data["density of states energies"];
        const tdos = data["total density of states"];
        const pdos = data["projected density of states"];

        const traces_tdos = [
            {
                x: tdos,
                y: energy,
                type: "scatter",
                mode: "lines",
            },
        ];

        const traces_pdos = pdos.map((d) => ({
            x: d,
            y: energy,
            type: "scatter",
            mode: "lines",
        }));

        if (plotDiv_Band && (window as any).Plotly) {
            (window as any).Plotly.newPlot(
                plotDiv_Band,
                traces_bands,
                {
                    ...layout_bands,
                    xaxis: {
                        tickmode: "array",
                        tickvals: ticks["distance"],
                        ticktext: ticks["label"],
                    },
                },
                {
                    displaylogo: false,
                },
            );
        }

        const traces_dos = [...traces_tdos, ...traces_pdos];

        if (plotDiv_DOS && (window as any).Plotly) {
            (window as any).Plotly.newPlot(
                plotDiv_DOS,
                traces_dos,
                layout_dos,
                {
                    displaylogo: false,
                },
            );
        }
    });
</script>

<div id="plotly" class="flex flex-col gap-0">
    <div id="plotDiv_DOS" class="m-0 p-0"></div>
    <div id="plotDiv_Band" class="m-0 p-0"></div>
</div>
