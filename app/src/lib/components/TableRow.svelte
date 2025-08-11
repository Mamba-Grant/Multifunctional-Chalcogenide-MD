<script lang="ts">
    import { onMount, tick } from "svelte";
    import { fade } from "svelte/transition";
    import MaterialModalInfo from "$lib/components/MaterialModalInfo.svelte";

    export let item = {};
    let expanded = false;
    let row: HTMLElement;

    let topX = 0,
        topY = 10;

    function updatePositions() {
        if (!row) return;

        // Use the expanded width for centering calculation
        const expandedWidth = window.innerWidth - 20; // calc(100vw - 20px)
        topX = window.innerWidth / 2 - expandedWidth / 2;
        topY = 10;
    }

    onMount(() => {
        window.addEventListener("resize", updatePositions);
    });

    async function expand() {
        if (!row) return;

        // Measure before expanding
        const first = row.getBoundingClientRect();
        const centerX = first.left + first.width / 2;
        const centerY = first.top + first.height / 2;

        // Calculate target position
        updatePositions();
        const targetX = topX;
        const targetY = topY;
        const expandedWidth = window.innerWidth - 20;
        const targetCenterX = targetX + expandedWidth / 2;
        const targetCenterY = targetY + first.height / 2; // Assuming height doesn't change much

        // Calculate scale factor (how much smaller the original was)
        const scaleX = first.width / expandedWidth;
        const scaleY = 1; // Keep height scale at 1 if height doesn't change much

        // Calculate translation needed to keep center aligned
        const translateX = centerX - targetCenterX;
        const translateY = centerY - targetCenterY;

        // Expand & wait for DOM update
        expanded = true;
        await tick();

        // Immediately set the element to the starting position and scale
        row.style.transition = "none";
        row.style.transformOrigin = "center center";
        row.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scaleX}, ${scaleY})`;

        // Force reflow
        row.offsetHeight;

        // Animate to final position and scale
        row.style.transition = "transform 400ms ease";
        row.style.transform = "translate(0, 0) scale(1, 1)";

        row.addEventListener(
            "transitionend",
            () => {
                row.style.transition = "";
                row.style.transform = "";
                row.style.transformOrigin = "";
            },
            { once: true },
        );

        document.body.style.overflow = "hidden";
    }

    async function unexpand() {
        if (!row) return;

        // Get current position (expanded)
        const expandedRect = row.getBoundingClientRect();
        const expandedCenterX = expandedRect.left + expandedRect.width / 2;
        const expandedCenterY = expandedRect.top + expandedRect.height / 2;

        // Set state to collapsed
        expanded = false;
        await tick();

        // Get target position (collapsed)
        const collapsedRect = row.getBoundingClientRect();
        const collapsedCenterX = collapsedRect.left + collapsedRect.width / 2;
        const collapsedCenterY = collapsedRect.top + collapsedRect.height / 2;

        // Calculate scale factor (how much smaller the target is)
        const scaleX = collapsedRect.width / expandedRect.width;
        const scaleY = 1;

        // Calculate translation to keep centers aligned during animation
        const translateX = expandedCenterX - collapsedCenterX;
        const translateY = expandedCenterY - collapsedCenterY;

        // Start from expanded state
        row.style.transition = "none";
        row.style.transformOrigin = "center center";
        row.style.transform = `translate(${translateX}px, ${translateY}px) scale(${1 / scaleX}, ${1 / scaleY})`;

        // Force reflow
        row.offsetHeight;

        // Animate to collapsed state
        row.style.transition = "transform 400ms ease";
        row.style.transform = "translate(0, 0) scale(1, 1)";

        row.addEventListener(
            "transitionend",
            () => {
                row.style.transition = "";
                row.style.transform = "";
                row.style.transformOrigin = "";
            },
            { once: true },
        );

        document.body.style.overflow = "";
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === "Escape" && expanded) {
            unexpand();
        }
    }

    // Style reactive statement: only fixed position when expanded, otherwise no positioning styles
    $: style = expanded
        ? `position: fixed; top: ${topY}px; left: ${topX}px; z-index: 1000; width: calc(100vw - 20px);`
        : `z-index: 1; width: auto;`;
</script>

<div
    bind:this={row}
    role="button"
    tabindex="0"
    class="border border-primary rounded-lg bg-white"
    {style}
    on:click={expand}
    on:keydown={handleKeydown}
    aria-expanded={expanded}
>
    <div
        class="normal-content row grid grid-cols-[15vw_15vw_15vw_15vw] gap-4 cursor-pointer my-1 w-full"
        aria-hidden={expanded}
    >
        <div class="text-center text-[clamp(0.75rem,1.5vw,1rem)]">
            {item["MP-ID"] ?? "N/A"}
        </div>
        <div class="text-center text-[clamp(0.75rem,1.5vw,1rem)]">
            {item.formula ?? "N/A"}
        </div>
        <div class="text-center text-[clamp(0.75rem,1.5vw,1rem)]">
            {item.spacegroup ?? "N/A"}
        </div>
        <div class="text-center text-[clamp(0.75rem,1.5vw,1rem)]">
            {item["band gap"] ?? "N/A"}
        </div>
    </div>
    <div
        class="expanded-content w-full flex items-center justify-between"
        aria-hidden={!expanded}
    >
        <!-- Topbar -->
        <div class="flex items-center gap-4">
            <h1 class="text-2xl font-bold text-foreground">
                {item.formula ?? "Unknown Material"}
            </h1>
            <div class="flex gap-4 text-sm text-muted-foreground">
                <span class="bg-primary/10 px-2 py-1 rounded">
                    MP-ID: {item["MP-ID"] ?? "N/A"}
                </span>
                <span class="bg-primary/10 px-2 py-1 rounded">
                    Spacegroup: {item.spacegroup ?? "N/A"}
                </span>
                <span class="bg-primary/10 px-2 py-1 rounded">
                    Bandgap: {item["band gap"] ?? "N/A"}
                </span>
            </div>
        </div>

        <!-- Close button -->
        <button
            class="p-2 rounded-lg hover:bg-primary/10 transition-colors focus:outline-none focus:ring-2 focus:ring-primary/50"
            on:click|stopPropagation={unexpand}
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

{#if expanded}
    <div
        class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto pointer-events-none"
    >
        <!-- Scrollable modal content -->
        <div
            class="relative max-h-[90vh] rounded-lg w-fill pointer-events-auto"
            on:click|stopPropagation
        >
            <MaterialModalInfo {item} />
        </div>
    </div>
{/if}

{#if expanded}
    <div
        class="fixed inset-0 bg-black/20 backdrop-blur-sm z-10"
        in:fade={{ duration: 500 }}
        out:fade={{ duration: 500 }}
        on:click|stopPropagation={unexpand}
        on:keydown|stopPropagation={handleKeydown}
    ></div>
{/if}

<style>
    .normal-content[aria-hidden="true"],
    .expanded-content[aria-hidden="true"] {
        opacity: 0;
        pointer-events: none;
        height: 0;
        overflow: hidden;
        transition: opacity 0.5s ease;
    }

    .normal-content[aria-hidden="false"],
    .expanded-content[aria-hidden="false"] {
        opacity: 1;
        pointer-events: auto;
        height: auto;
        transition: opacity 0.5s ease;
    }
</style>
