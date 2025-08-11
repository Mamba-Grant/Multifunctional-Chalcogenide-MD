<script lang="ts">
    import { tweened } from "svelte/motion";
    import { cubicOut } from "svelte/easing";
    import { searchQuery } from "$lib/store";

    // Create a tweened store for smooth width animation
    const width = tweened(40, {
        duration: 300,
        easing: cubicOut,
    });

    function expand() {
        width.set(50);
    }

    function contract() {
        width.set(40);
    }
</script>

<input
    type="text"
    placeholder="Search materials... (e.g., 'elements:Fe,Ge bandgap:<0.1' or 'spacegroup:Fm-3m')"
    bind:value={$searchQuery}
    class="px-4 py-2 border border-gray-300 rounded shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-500 min-w-[30em]"
    style="margin: 1em; width: {$width}%; transition: box-shadow 0.3s ease;"
    on:focusin={expand}
    on:focusout={contract}
/>
