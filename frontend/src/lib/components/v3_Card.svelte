<script lang="ts">
    import { spring } from "svelte/motion";
    import { slide, fade, fly } from "svelte/transition";
    import { quintOut } from "svelte/easing";
    import CardTables from "./CardTables.svelte";
    import CrystalPlot from "./CrystalPlot.svelte";

    export let item;

    let height = spring(3); // Row height
    let isExpanded = false;
    let expandableContent: HTMLElement; // Reference to expandable content
    let cardElement: HTMLElement; // Reference to the card element
    let scrollContainer: HTMLElement; // Reference to scroll container

    function expand() {
        isExpanded = true;

        // Lock the body scroll
        document.body.style.overflow = "hidden";

        // Focus the scroll container for keyboard events
        setTimeout(() => {
            if (scrollContainer) {
                scrollContainer.focus();
            }
        }, 300); // Wait for animation to settle
    }

    function unexpand() {
        if (isExpanded) {
            height.set(0);
            // Unlock the body scroll
            document.body.style.overflow = "";
        }
        isExpanded = false;
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === "Escape") {
            unexpand();
        }
    }
</script>

<div
    bind:this={cardElement}
    role="button"
    tabindex="0"
    on:keydown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            expand();
        }
    }}
    on:click={expand}
    class="border border-primary rounded-lg transition-all duration-50 cursor-pointer my-1 overflow-hidden {isExpanded
        ? 'opacity-20'
        : ''}"
    style="height: {$height}em; min-height: 3em; width: 90%"
>
    <!-- Always visible row content -->
    <div
        class="flex items-start justify-between p-3 min-h-12 bg-background hover:bg-primary/5"
    >
        <div class="flex gap-4 flex-1">
            <!-- Column 1: MP-ID -->
            <div class="text-sm text-muted-foreground w-24 break-words">
                {item["MP-ID"] != null ? item["MP-ID"] : "N/A"}
            </div>
            <!-- Column 2: Formula -->
            <div class="font-medium w-32 break-words">
                {item.formula != null ? item.formula : "N/A"}
            </div>
            <!-- Column 3: Spacegroup -->
            <div class="text-sm text-muted-foreground w-28 break-words">
                {item.spacegroup != null ? item.spacegroup : "N/A"}
            </div>
            <!-- Column 4: Bandgap -->
            <div class="text-sm text-muted-foreground w-28 break-words">
                {item["band gap"] != null ? item["band gap"] : "N/A"}
            </div>
        </div>

        <!-- Controls -->
        <div class="flex items-center gap-2 ml-2">
            <!-- Expand/Collapse indicator -->
            <div
                class="transition-transform duration-200 {isExpanded
                    ? 'rotate-180'
                    : ''}"
            >
                <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                >
                    <path d="M6 9l6 6 6-6" />
                </svg>
            </div>
        </div>
    </div>
</div>

<!-- Fullscreen overlay -->
{#if isExpanded}
    <!-- Backdrop -->
    <div
        class="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
        in:fade={{ duration: 300 }}
        out:fade={{ duration: 200 }}
        on:click={unexpand}
    ></div>

    <!-- Fullscreen content -->
    <div
        class="fixed inset-0 z-50 flex flex-col"
        in:fly={{
            y: window.innerHeight,
            duration: 400,
            easing: quintOut,
        }}
        out:fly={{
            y: window.innerHeight,
            duration: 300,
            easing: quintOut,
        }}
    >
        <!-- Header -->
        <div
            class="bg-background rounded-xl p-6 border border-primary/20 shadow-sm"
            style="background-color: white; height: 6em; transform: translateY(-2em);"
        >
            <div class="flex items-center justify-between p-4 relative z-10">
                <div class="flex items-center gap-4">
                    <h1 class="text-2xl font-bold text-foreground">
                        {item.formula ?? "Unknown Material"}
                    </h1>
                    <div class="flex gap-4 text-sm text-muted-foreground">
                        <span class="bg-primary/10 px-2 py-1 rounded"
                            >MP-ID: {item["MP-ID"] ?? "N/A"}</span
                        >
                        <span class="bg-primary/10 px-2 py-1 rounded"
                            >Spacegroup: {item.spacegroup ?? "N/A"}</span
                        >
                        <span class="bg-primary/10 px-2 py-1 rounded"
                            >Bandgap: {item["band gap"] ?? "N/A"}</span
                        >
                    </div>
                </div>

                <!-- Close button -->
                <button
                    class="p-2 rounded-lg hover:bg-primary/10 transition-colors focus:outline-none focus:ring-2 focus:ring-primary/50"
                    on:click={unexpand}
                    title="Close (ESC)"
                    aria-label="Close fullscreen view"
                >
                    <svg
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                    >
                        <path d="M18 6L6 18M6 6l12 12" />
                    </svg>
                </button>
            </div>
        </div>

        <!-- Scrollable content -->
        <div
            role="button"
            bind:this={scrollContainer}
            class="flex-1 overflow-auto bg-background focus:outline-none"
            tabindex="0"
            on:keydown={handleKeydown}
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
                    in:fade={{ delay: 200, duration: 300 }}
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
                                <span class="text-muted-foreground"
                                    >Band Gap</span
                                >
                                <span class="font-medium"
                                    >{item["band gap"] ?? "N/A"} eV</span
                                >
                            </div>
                            <div
                                class="flex justify-between py-2 border-b border-primary/10"
                            >
                                <span class="text-muted-foreground"
                                    >Band Gap Type</span
                                >
                                <span class="font-medium">N/A</span>
                            </div>
                            <div
                                class="flex justify-between py-2 border-b border-primary/10"
                            >
                                <span class="text-muted-foreground"
                                    >Conductivity</span
                                >
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
                                <span class="text-muted-foreground"
                                    >Effective Mass</span
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
                                <span class="text-muted-foreground"
                                    >Crystal System</span
                                >
                                <span class="font-medium">N/A</span>
                            </div>
                            <div
                                class="flex justify-between py-2 border-b border-primary/10"
                            >
                                <span class="text-muted-foreground"
                                    >Space Group</span
                                >
                                <span class="font-sm"
                                    >{item.spacegroup ?? "N/A"}</span
                                >
                            </div>
                            <div
                                class="flex justify-between py-2 border-b border-primary/10"
                            >
                                <span class="text-muted-foreground"
                                    >Lattice Parameters (please check validity
                                    of calculation) [Å]</span
                                >
                                <!-- should include some conditionals here to simplify a=b or b=c or a=b=c -->
                                <span class="font-sm text-right break-words">
                                    a={item.cell?.array?.[0]?.[0] != null
                                        ? item.cell.array[0][0].toFixed(3)
                                        : "N/A"}, b={item.cell
                                        ?.array?.[1]?.[1] != null
                                        ? item.cell.array[1][1].toFixed(3)
                                        : "N/A"}, c={item.cell
                                        ?.array?.[2]?.[2] != null
                                        ? item.cell.array[2][2].toFixed(3)
                                        : "N/A"}
                                </span>
                            </div>
                            <div
                                class="flex justify-between py-2 border-b border-primary/10"
                            >
                                <span class="text-muted-foreground">Volume</span
                                >
                                <span class="font-medium">N/A</span>
                            </div>
                            <div
                                class="flex justify-between py-2 border-b border-primary/10"
                            >
                                <span class="text-muted-foreground">MP-ID</span>
                                <span class="font-sm"
                                    >{item["MP-ID"] ?? "N/A"}</span
                                >
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
                                            {value != null
                                                ? value.toFixed(5)
                                                : "N/A"}
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
                            class="bg-gray-100 dark:bg-gray-800 rounded-lg aspect-square flex items-center justify-center text-gray-500 dark:text-gray-400 min-h-[400px]"
                        >
                            <div class="text-center">
                                <!-- <div class="text-4xl mb-2">📊</div> -->
                                <!-- <div>Property Plots & Charts</div> -->
                                <div class="text-sm opacity-75 mt-2">
                                    Band structure, DOS, etc.
                                </div>
                            </div>
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
                                    >{item["band gap soc"].toFixed(5) ??
                                        "N/A"}</span
                                >
                            </div>
                            <div
                                class="flex flex-1 justify-between py-2 border-b border-primary/10"
                            >
                                <span
                                    class="text-muted-foreground text-left text-muted-foreground w-32 break-words"
                                    >VBM wrt. vacuum</span
                                >
                                <!-- <span -->
                                <!--     class="text-muted-foreground text-left text-muted-foreground w-32 break-words" -->
                                <!--     >{item.vbm.toFixed(5) ?? "N/A"}</span -->
                                <!-- > -->
                            </div>
                            <div
                                class="flex flex-1 justify-between py-2 border-b border-primary/10"
                            >
                                <span
                                    class="text-muted-foreground text-left text-muted-foreground w-32 break-words"
                                    >VBM wrt. vacuum (SOC)</span
                                >
                                <!-- <span -->
                                <!--     class="text-muted-foreground text-left text-muted-foreground w-32 break-words" -->
                                <!--     >{item["vbm soc"].toFixed(5) ?? "N/A"}</span -->
                                <!-- > -->
                            </div>
                            <div
                                class="flex flex-1 justify-between py-2 border-b border-primary/10"
                            >
                                <span
                                    class="text-muted-foreground text-left text-muted-foreground w-32 break-words"
                                    >CBM wrt. vacuum</span
                                >
                                <!-- <span -->
                                <!--     class="text-muted-foreground text-left text-muted-foreground w-32 break-words" -->
                                <!--     >{item.cbm.toFixed(5) ?? "N/A"}</span -->
                                <!-- > -->
                            </div>
                            <div
                                class="flex flex-1 justify-between py-2 border-b border-primary/10"
                            >
                                <span
                                    class="text-muted-foreground text-left text-muted-foreground w-32 break-words"
                                    >CBM wrt. vacuum (SOC)</span
                                >
                                <!-- <span -->
                                <!--     class="text-muted-foreground text-left text-muted-foreground w-32 break-words" -->
                                <!--     >{item["cbm soc"].toFixed(5) ?? "N/A"}</span -->
                                <!-- > -->
                            </div>
                        </div>
                    </div>
                </div>

                <!-- <!-- Additional analysis -->
                <!-- <div -->
                <!--     class="bg-card rounded-xl p-6 border border-primary/20 shadow-sm" -->
                <!--     style="background-color: white;" -->
                <!--     in:fade={{ delay: 500, duration: 300 }} -->
                <!-- > -->
                <!--     <h3 class="text-lg font-semibold mb-4 text-foreground"> -->
                <!--         Thermodynamic & Mechanical Properties -->
                <!--     </h3> -->
                <!--     <div -->
                <!--         class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" -->
                <!--     > -->
                <!--         <div class="text-center p-4 bg-primary/5 rounded-lg"> -->
                <!--             <div class="text-2xl font-bold text-primary"> -->
                <!--                 -2.34 -->
                <!--             </div> -->
                <!--             <div class="text-sm text-muted-foreground"> -->
                <!--                 Formation Energy (eV/atom) -->
                <!--             </div> -->
                <!--         </div> -->
                <!--         <div class="text-center p-4 bg-primary/5 rounded-lg"> -->
                <!--             <div class="text-2xl font-bold text-primary"> -->
                <!--                 145 -->
                <!--             </div> -->
                <!--             <div class="text-sm text-muted-foreground"> -->
                <!--                 Bulk Modulus (GPa) -->
                <!--             </div> -->
                <!--         </div> -->
                <!--         <div class="text-center p-4 bg-primary/5 rounded-lg"> -->
                <!--             <div class="text-2xl font-bold text-primary"> -->
                <!--                 89 -->
                <!--             </div> -->
                <!--             <div class="text-sm text-muted-foreground"> -->
                <!--                 Shear Modulus (GPa) -->
                <!--             </div> -->
                <!--         </div> -->
                <!--         <div class="text-center p-4 bg-primary/5 rounded-lg"> -->
                <!--             <div class="text-2xl font-bold text-primary"> -->
                <!--                 0.24 -->
                <!--             </div> -->
                <!--             <div class="text-sm text-muted-foreground"> -->
                <!--                 Poisson's Ratio -->
                <!--             </div> -->
                <!--         </div> -->
                <!--     </div> -->
                <!-- </div> -->

                <!-- Navigation hint -->
                <div class="text-center text-sm text-muted-foreground py-8">
                    <div class="flex items-center justify-center gap-2">
                        <kbd class="px-2 py-1 bg-primary/10 rounded text-xs"
                            >ESC to close</kbd
                        >
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}
