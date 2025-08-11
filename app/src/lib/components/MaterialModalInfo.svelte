<script lang="ts">
    import { fade } from "svelte/transition";
    import CardTables from "./CardTables.svelte";
    import CrystalPlot from "./CrystalPlot.svelte";
    import BandDOSPlot from "./BandDOSPlot.svelte";

    export let item;

    let scrollContainer: HTMLElement;
</script>

<div
    role="button"
    bind:this={scrollContainer}
    class="flex-1 overflow-auto bg-background focus:outline-none"
    tabindex="0"
    on:keydown|capture={(e) => {
        // Only stop propagation for navigation keys, not ESC
        const navigationKeys = [
            "PageUp",
            "PageDown",
            "Home",
            "End",
            "ArrowUp",
            "ArrowDown",
            "ArrowLeft",
            "ArrowRight",
        ];
        if (navigationKeys.includes(e.key)) {
            e.stopPropagation();
            e.preventDefault();
        }
        // Let ESC and other keys bubble through to handleKeydown
    }}
>
    <div class="max-w-7xl mx-auto p-6 space-y-8">
        <!-- Detailed information sections -->
        <div
            class="grid grid-cols-1 md:grid-cols-2 gap-6"
            in:fade={{ delay: 200, duration: 500 }}
        >
            <div
                class="bg-card rounded-xl p-6 border border-primary/20 shadow-sm"
                style="background-color: white;"
            >
                <h3 class="text-lg font-semibold mb-4 text-foreground">
                    At a Glance...
                </h3>
                <div class="space-y-3">
                    <div
                        class="flex justify-between py-2 border-b border-primary/10"
                    >
                        <span class="text-muted-foreground">Band Gap</span>
                        <span class="font-medium"
                            >{item["band gap"] ?? "N/A"} eV</span
                        >
                    </div>
                    <div
                        class="flex justify-between py-2 border-b border-primary/10"
                    >
                        <span class="text-muted-foreground">Band Gap Type</span>
                        <span class="font-medium">N/A</span>
                    </div>
                    <div
                        class="flex justify-between py-2 border-b border-primary/10"
                    >
                        <span class="text-muted-foreground">Conductivity</span>
                        <span class="font-medium">N/A</span>
                    </div>
                    <div
                        class="flex justify-between py-2 border-b border-primary/10"
                    >
                        <span class="text-muted-foreground"
                            >Magnetic Ordering</span
                        >
                        <span class="font-medium">N/A</span>
                    </div>
                    <div
                        class="flex justify-between py-2 border-b border-primary/10"
                    >
                        <span class="text-muted-foreground">Effective Mass</span
                        >
                        <span class="font-medium">
                            {typeof item["effective mass"] === "number"
                                ? item["effective mass"].toFixed(7)
                                : "N/A"} [m₀]
                        </span>
                    </div>
                </div>
            </div>

            <div
                class="bg-card rounded-xl p-6 border border-primary/20 shadow-sm"
                style="background-color: white;"
            >
                <h3 class="text-lg font-semibold mb-4 text-foreground">
                    Crystallographic Data
                </h3>
                <div class="space-y-3">
                    <div
                        class="flex justify-between py-2 border-b border-primary/10"
                    >
                        <span class="text-muted-foreground">Crystal System</span
                        >
                        <span class="font-medium">N/A</span>
                    </div>
                    <div
                        class="flex justify-between py-2 border-b border-primary/10"
                    >
                        <span class="text-muted-foreground">Space Group</span>
                        <span class="font-sm">{item.spacegroup ?? "N/A"}</span>
                    </div>
                    <div
                        class="flex justify-between py-2 border-b border-primary/10"
                    >
                        <span class="text-muted-foreground"
                            >Lattice Parameters (please check validity of
                            calculation) [Å]</span
                        >
                        <!-- should include some conditionals here to simplify a=b or b=c or a=b=c -->
                        <span class="font-sm text-right break-words">
                            a={item.cell?.array?.[0]?.[0] != null
                                ? item.cell?.array[0][0].toFixed(3)
                                : "N/A"}, b={item.cell?.array?.[1]?.[1] != null
                                ? item.cell?.array[1][1].toFixed(3)
                                : "N/A"}, c={item.cell?.array?.[2]?.[2] != null
                                ? item.cell?.array[2][2].toFixed(3)
                                : "N/A"}
                        </span>
                    </div>
                    <div
                        class="flex justify-between py-2 border-b border-primary/10"
                    >
                        <span class="text-muted-foreground">Volume</span>
                        <span class="font-medium">N/A</span>
                    </div>
                    <div
                        class="flex justify-between py-2 border-b border-primary/10"
                    >
                        <span class="text-muted-foreground">MP-ID</span>
                        <span class="font-sm">{item["MP-ID"] ?? "N/A"}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Material details -->
        <div
            class="bg-card rounded-xl p-6 border border-primary/20 shadow-sm"
            style="background-color: white;"
            in:fade={{ delay: 300, duration: 300 }}
        >
            <h2 class="text-xl font-semibold mb-6 text-foreground">
                Material Properties
            </h2>
            <CardTables {item} />
        </div>

        <!-- Visualizations -->
        <div
            class="grid grid-cols-1 xl:grid-cols-2 gap-8"
            in:fade={{ delay: 400, duration: 300 }}
        >
            <div
                class="bg-card rounded-xl p-6 border border-primary/20 shadow-sm"
                style="background-color: white;"
            >
                <h3 class="text-lg font-semibold mb-4 text-foreground">
                    3D Crystal Structure
                </h3>
                <div
                    class="bg-gray-100 dark:bg-gray-800 rounded-lg aspect-square flex items-center justify-center text-gray-500 dark:text-gray-400 min-h-[400px]"
                >
                    <CrystalPlot {item} />
                </div>
                <div class="space-y-3">
                    <div
                        class="flex flex-1 justify-between py-2 border-b border-primary/10"
                    >
                        <span
                            class="text-muted-foreground text-left font-bold text-muted-foreground w-32 break-words"
                            >Axis</span
                        >
                        <span
                            class="text-muted-foreground text-left font-bold text-muted-foreground w-32 break-words"
                            >x [Å]</span
                        >
                        <span
                            class="text-muted-foreground text-left font-bold text-muted-foreground w-32 break-words"
                            >y [Å]</span
                        >
                        <span
                            class="text-muted-foreground text-left font-bold text-muted-foreground w-32 break-words"
                            >z [Å]</span
                        >
                        <span
                            class="text-muted-foreground text-left font-bold text-muted-foreground w-32 break-words"
                            >Periodic</span
                        >
                    </div>
                    {#each item.cell.array as row, index}
                        <div
                            class="flex flex-1 justify-between py-2 border-b border-primary/10"
                        >
                            <span
                                class="text-muted-foreground text-left w-32 break-words"
                            >
                                {index + 1}
                            </span>
                            {#each row as value}
                                <span
                                    class="text-muted-foreground text-left w-32 break-words"
                                >
                                    {value != null ? value.toFixed(5) : "N/A"}
                                </span>
                            {/each}
                            <span
                                class="text-muted-foreground text-left w-32 break-words"
                            >
                                N/A
                            </span>
                        </div>
                    {/each}
                </div>
            </div>

            <div
                class="bg-card rounded-xl p-6 border border-primary/20 shadow-sm"
                style="background-color: white;"
            >
                <h3 class="text-lg font-semibold mb-4 text-foreground">
                    Band Structure and Density of States
                </h3>
                <div
                    class="bg-gray-100 dark:bg-gray-800 rounded-lg aspect-square flex items-center justify-center text-gray-500 dark:text-gray-400 w-[98%]"
                >
                    <BandDOSPlot {item} />
                </div>
                <div class="space-y-3">
                    <div
                        class="flex flex-1 justify-between py-2 border-b border-primary/10"
                    >
                        <span
                            class="text-muted-foreground text-left font-bold text-muted-foreground w-32 break-words"
                            >Properties [eV]</span
                        >
                    </div>
                    <div
                        class="flex flex-1 justify-between py-2 border-b border-primary/10"
                    >
                        <span
                            class="text-muted-foreground text-left text-muted-foreground w-32 break-words"
                            >Band Gap</span
                        >
                        <span
                            class="text-muted-foreground text-left text-muted-foreground w-32 break-words"
                            >{item["band gap"] ?? "N/A"}</span
                        >
                    </div>
                    <div
                        class="flex flex-1 justify-between py-2 border-b border-primary/10"
                    >
                        <span
                            class="text-muted-foreground text-left text-muted-foreground w-32 break-words"
                            >Band Gap (SOC)</span
                        >
                        <span
                            class="text-muted-foreground text-left text-muted-foreground w-32 break-words"
                            >{item["band gap soc"].toFixed(5) ?? "N/A"}</span
                        >
                    </div>
                    <div
                        class="flex flex-1 justify-between py-2 border-b border-primary/10"
                    >
                        <span
                            class="text-muted-foreground text-left text-muted-foreground w-32 break-words"
                            >VBM wrt. vacuum</span
                        >
                    </div>
                    <div
                        class="flex flex-1 justify-between py-2 border-b border-primary/10"
                    >
                        <span
                            class="text-muted-foreground text-left text-muted-foreground w-32 break-words"
                            >VBM wrt. vacuum (SOC)</span
                        >
                    </div>
                    <div
                        class="flex flex-1 justify-between py-2 border-b border-primary/10"
                    >
                        <span
                            class="text-muted-foreground text-left text-muted-foreground w-32 break-words"
                            >CBM wrt. vacuum</span
                        >
                    </div>
                    <div
                        class="flex flex-1 justify-between py-2 border-b border-primary/10"
                    >
                        <span
                            class="text-muted-foreground text-left text-muted-foreground w-32 break-words"
                            >CBM wrt. vacuum (SOC)</span
                        >
                    </div>
                </div>
            </div>
        </div>

        <div class="text-center text-sm text-muted-foreground py-8">
            <div class="flex items-center justify-center gap-2">
                <kbd class="px-2 py-1 bg-primary/10 rounded text-xs"
                    >ESC to close</kbd
                >
            </div>
        </div>
    </div>
</div>
