<script lang="ts">
    import { onMount } from "svelte";

    export let item;

    let plotCanvas: HTMLElement;
    let containerWidth = 0;
    let containerHeight = 0;

    let plotDiv: HTMLElement;

    $: plotWidth = Math.floor(containerWidth * 0.9);
    $: plotHeight = Math.floor(containerHeight * 0.9);

    let plotsInitialized = false;

    // Reactive layouts updated on size change
    $: if (plotsInitialized) {
        const Plotly = (window as any).Plotly;
        if (Plotly) {
            Plotly.relayout(plotDiv, {
                width: plotWidth,
                height: plotHeight,
            });
        }
    }

    export let supercell = [2, 2, 1];

    const baseSymbols: string[] = item.symbols ?? [];
    const basePositions: number[][] = item.positions ?? [];
    const supercellConnectivity: number[][] = item.connectivity ?? [];

    type Atom = {
        pos: number[];
        symbol: string;
        cellIndex: number;
        imageOffset: [number, number, number];
        globalIndex: number;
    };

    let atoms: Atom[] = [];
    let atomMap = new Map<string, number>(); // "cellIndex_ix_iy_iz" -> globalIndex
    let globalIndex = 0;

    const [nx, ny, nz] = supercell;

    const lattice = item.cell?.array ?? [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ];

    for (let ix = 0; ix < nx; ix++) {
        for (let iy = 0; iy < ny; iy++) {
            for (let iz = 0; iz < nz; iz++) {
                const offset = [
                    ix * lattice[0][0] +
                        iy * lattice[1][0] +
                        iz * lattice[2][0],
                    ix * lattice[0][1] +
                        iy * lattice[1][1] +
                        iz * lattice[2][1],
                    ix * lattice[0][2] +
                        iy * lattice[1][2] +
                        iz * lattice[2][2],
                ];

                for (let a = 0; a < basePositions.length; a++) {
                    const pos = basePositions[a];
                    const newPos = [
                        pos[0] + offset[0],
                        pos[1] + offset[1],
                        pos[2] + offset[2],
                    ];
                    atoms.push({
                        pos: newPos,
                        symbol: baseSymbols[a],
                        cellIndex: a,
                        imageOffset: [ix, iy, iz],
                        globalIndex,
                    });
                    atomMap.set(`${a}_${ix}_${iy}_${iz}`, globalIndex);
                    globalIndex++;
                }
            }
        }
    }

    // let bonds: number[][][] = [];
    // for (let i = 0; i < baseConnectivity.length; i++) {
    //     for (let j = i + 1; j < baseConnectivity[i].length; j++) {
    //         if (baseConnectivity[i][j]) {
    //             const pos1: number[] = atoms[i].pos;
    //             const pos2: number[] = atoms[j].pos;
    //             bonds.push([pos1, pos2]); // Or push this into a bond list
    //         }
    //     }
    // }
    // console.log(bonds);

    export let symbols = atoms.map((a) => a.symbol);
    export let positions = atoms.map((a) => a.pos);

    // Bond data
    let bond_x: number[] = [];
    let bond_y: number[] = [];
    let bond_z: number[] = [];

    for (let i = 0; i < supercellConnectivity.length; i++) {
        for (let j = 1; j < supercellConnectivity[i].length; j++) {
            if (supercellConnectivity[i]?.[j] === 1) {
                const [x1, y1, z1] = atoms[i].pos;
                const [x2, y2, z2] = atoms[j].pos;

                bond_x.push(x1, x2, null);
                bond_y.push(y1, y2, null);
                bond_z.push(z1, z2, null);
            }
        }
    }

    // jmol palette: https://jmol.sourceforge.net/jscolors/
    const colors = {
        H: "#FFFFFF",
        He: "#D9FFFF",
        Li: "#CC80FF",
        Be: "#C2FF00",
        B: "#FFB5B5",
        C: "#909090",
        N: "#3050F8",
        O: "#FF0D0D",
        F: "#90E050",
        Ne: "#B3E3F5",
        Na: "#AB5CF2",
        Mg: "#8AFF00",
        Al: "#BFA6A6",
        Si: "#F0C8A0",
        P: "#FF8000",
        S: "#FFFF30",
        Cl: "#1FF01F",
        Ar: "#80D1E3",
        K: "#8F40D4",
        Ca: "#3DFF00",
        Sc: "#E6E6E6",
        Ti: "#BFC2C7",
        V: "#A6A6AB",
        Cr: "#8A99C7",
        Mn: "#9C7AC7",
        Fe: "#E06633",
        Co: "#F090A0",
        Ni: "#50D050",
        Cu: "#C88033",
        Zn: "#7D80B0",
        Ga: "#C28F8F",
        Ge: "#668F8F",
        As: "#BD80E3",
        Se: "#FFA100",
        Br: "#A62929",
        Kr: "#5CB8D1",
        Rb: "#702EB0",
        Sr: "#00FF00",
        Y: "#94FFFF",
        Zr: "#94E0E0",
        Nb: "#73C2C9",
        Mo: "#54B5B5",
        Tc: "#3B9E9E",
        Ru: "#248F8F",
        Rh: "#0A7D8C",
        Pd: "#006985",
        Ag: "#C0C0C0",
        Cd: "#FFD98F",
        In: "#A67573",
        Sn: "#668080",
        Sb: "#9E63B5",
        Te: "#D47A00",
        I: "#940094",
        Xe: "#429EB0",
        Cs: "#57178F",
        Ba: "#00C900",
        La: "#70D4FF",
        Ce: "#FFFFC7",
        Pr: "#D9FFC7",
        Nd: "#C7FFC7",
        Pm: "#A3FFC7",
        Sm: "#8FFFC7",
        Eu: "#61FFC7",
        Gd: "#45FFC7",
        Tb: "#30FFC7",
        Dy: "#1FFFC7",
        Ho: "#00FF9C",
        Er: "#00E675",
        Tm: "#00D452",
        Yb: "#00BF38",
        Lu: "#00AB24",
        Hf: "#4DC2FF",
        Ta: "#4DA6FF",
        W: "#2194D6",
        Re: "#267DAB",
        Os: "#266696",
        Ir: "#175487",
        Pt: "#D0D0E0",
        Au: "#FFD123",
        Hg: "#B8B8D0",
        Tl: "#A6544D",
        Pb: "#575961",
        Bi: "#9E4FB5",
        Po: "#AB5C00",
        At: "#754F45",
        Rn: "#428296",
        Fr: "#420066",
        Ra: "#007D00",
        Ac: "#70ABFA",
        Th: "#00BAFF",
        Pa: "#00A1FF",
        U: "#008FFF",
        Np: "#0080FF",
        Pu: "#006BFF",
        Am: "#545CF2",
        Cm: "#785CE3",
        Bk: "#8A4FE3",
        Cf: "#A136D4",
        Es: "#B31FD4",
        Fm: "#B31FBA",
        Md: "#B30DA6",
        No: "#BD0D87",
        Lr: "#C70066",
        Rf: "#CC0059",
        Db: "#D1004F",
        Sg: "#D90045",
        Bh: "#E00038",
        Hs: "#E6002E",
        Mt: "#EB0026",
        Ds: "#FF1493",
        Rg: "#FF1493",
        Cn: "#FF1493",
        Nh: "#FF1493",
        Fl: "#FF1493",
        Mc: "#FF1493",
        Lv: "#FF1493",
        Ts: "#FF1493",
        Og: "#FF1493",
    };

    export let data = [
        {
            x: positions.map((p) => p[0]),
            y: positions.map((p) => p[1]),
            z: positions.map((p) => p[2]),
            mode: "markers",
            type: "scatter3d",
            text: symbols,
            marker: {
                size: 5,
                color: symbols.map((el) => colors[el] ?? "#808080"),
            },
            hoverinfo: "text",
        },
    ];

    export let bond_data = [
        {
            x: bond_x,
            y: bond_y,
            z: bond_z,
            mode: "lines",
            type: "scatter3d",
            line: {
                color: "#666666",
                width: 4,
            },
            hoverinfo: "none",
        },
    ];

    let [a, b, c] = item.cell.array;

    const origin = [0, 0, 0];

    // The 8 corners of the unit cell
    const corners = [
        origin,
        a,
        b,
        c,
        [a[0] + b[0], a[1] + b[1], a[2] + b[2]],
        [a[0] + c[0], a[1] + c[1], a[2] + c[2]],
        [b[0] + c[0], b[1] + c[1], b[2] + c[2]],
        [a[0] + b[0] + c[0], a[1] + b[1] + c[1], a[2] + b[2] + c[2]],
    ];

    // Edges are pairs of indices of corners connected by an edge
    const edges = [
        [0, 1],
        [0, 2],
        [0, 3],
        [1, 4],
        [1, 5],
        [2, 4],
        [2, 6],
        [3, 5],
        [3, 6],
        [4, 7],
        [5, 7],
        [6, 7],
    ];

    let xs = [],
        ys = [],
        zs = [];

    edges.forEach(([i, j]) => {
        xs.push(corners[i][0], corners[j][0], null);
        ys.push(corners[i][1], corners[j][1], null);
        zs.push(corners[i][2], corners[j][2], null);
    });

    export let cell_data = [
        {
            x: xs,
            y: ys,
            z: zs,
            mode: "lines",
            type: "scatter3d",
            line: {
                color: "#666666",
                width: 4,
                dash: "dash",
            },
            hoverinfo: "none",
        },
    ];

    // Combined data
    export let plot_data = [...data, ...bond_data, ...cell_data];

    // Breaks if we don't wait for plotly
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

    const layout = {
        showlegend: false,
        paper_bgcolor: "rgba(0,0,0,0)",
        dragmode: "turntable",
        aspectratio: { x: 1, y: 1, z: 1 },
        margin: { l: 10, r: 10, t: 10, b: 10 },
        scene: {
            xaxis: {
                autorange: true,
                showgrid: false,
                zeroline: true,
                showline: false,
                autotick: true,
                ticks: "",
                showticklabels: false,
            },
            yaxis: {
                autorange: true,
                showgrid: false,
                zeroline: true,
                showline: false,
                autotick: true,
                ticks: "",
                showticklabels: false,
            },
            zaxis: {
                autorange: true,
                showgrid: false,
                zeroline: true,
                showline: false,
                autotick: true,
                ticks: "",
                showticklabels: false,
            },
            camera: {
                projection: { type: "orthographic" }, // perspective | orthographic
                eye: { x: 0, y: 0, z: 1 },
                up: { x: 0, y: 1, z: 0 },
                center: { x: 0, y: 0, z: 0 },
            },
        },
    };

    // onMount(async () => {
    async function initializePlots() {
        await loadPlotly();

        if (plotDiv && (window as any).Plotly) {
            (window as any).Plotly.newPlot(
                plotDiv,
                plot_data,
                {
                    ...layout,
                    height: plotHeight || 700,
                    width: plotWidth || 700,
                },
                {
                    displaylogo: false,
                    responsive: false,
                },
            );
        }

        plotsInitialized = true;
    }

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

<div id="plotly" bind:this={plotCanvas}>
    <div id="plotDiv" bind:this={plotDiv}></div>
</div>
