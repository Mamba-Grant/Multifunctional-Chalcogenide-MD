<script lang="ts">
    import { spring } from "svelte/motion";
    import { fade, slide } from "svelte/transition";
    export let item;

    let height = spring(50); // Row height
    let isExpanded = false;
    let expandableContent: HTMLElement; // Reference to expandable content

    function toggleExpanded() {
        if (isExpanded) {
            height.set(50); // Collapsed height
        } else {
            // Wait for DOM to update, then measure content height
            setTimeout(() => {
                if (expandableContent) {
                    const contentHeight = expandableContent.scrollHeight;
                    height.set(50 + contentHeight); // Base height + content height
                }
            }, 0);
        }
        isExpanded = !isExpanded;
    }
</script>

<div
    role="button"
    tabindex="0"
    on:keydown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            toggleExpanded();
        }
    }}
    on:click={toggleExpanded}
    class="border border-primary rounded-lg transition-all duration-50 cursor-pointer my-1 overflow-hidden"
    style="height: {$height}px; min-height: 50px; width: 90%"
>
    <!-- Always visible row content -->
    <div
        class="flex items-start justify-between p-3 min-h-12 bg-background hover:bg-primary/5"
    >
        <div class="flex gap-4 flex-1">
            <!-- Column 1: MP-ID -->
            <div class="text-sm text-muted-foreground w-24 break-words">
                {item["MP-ID"] ?? "N/A"}
            </div>
            <!-- Column 2: Formula -->
            <div class="font-medium w-32 break-words">
                {item.formula ?? "N/A"}
            </div>
            <!-- Column 3: Spacegroup -->
            <div class="text-sm text-muted-foreground w-28 break-words">
                {item.spacegroup ?? "N/A"}
            </div>
            <!-- Column 4: Bandgap -->
            <div class="text-sm text-muted-foreground w-28 break-words">
                {item["band gap"] ?? "N/A"}
            </div>
        </div>
        <!-- Expand/Collapse indicator -->
        <div
            class="ml-2 transition-transform duration-200 {isExpanded
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

    <!-- Expandable content -->
    {#if isExpanded}
        <div
            bind:this={expandableContent}
            class="px-3 pb-3"
            in:slide={{ duration: 300 }}
        >
            <div class="border-t border-primary/20 pt-3">
                <div in:fade={{ duration: 400, delay: 100 }}>
                    <pre>{JSON.stringify(item, null, 2)}</pre>
                </div>
            </div>
        </div>
    {/if}
</div>
