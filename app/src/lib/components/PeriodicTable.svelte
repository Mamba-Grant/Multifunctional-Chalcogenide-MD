<script lang="ts">
    import ElementButton from "$lib/components/ElementButton.svelte";
    import { elements } from "$lib/elements";
    import { searchQuery } from "$lib/store";

    function handleElementClick(element: JSON) {
        let newQuery = $searchQuery;

        const regex = /elements:([^ ]*)/g;
        const found = $searchQuery.match(regex);

        if (found) {
            newQuery = $searchQuery.replace(
                /elements:([^ ]*)/,
                found[0] + "," + element.symbol,
            );
            console.log(newQuery);
        } else {
            newQuery = $searchQuery + " elements:" + element.symbol;
        }

        searchQuery.update((q) => newQuery);
    }
</script>

<div class="periodic-table max-w-[95vw] mx-auto">
    {#each elements as element}
        <ElementButton {element} onClick={handleElementClick} />
    {/each}
</div>

<style>
    .periodic-table {
        display: grid;
        grid-template-columns: repeat(18, 1fr);
        grid-template-rows: repeat(10, 1fr);
        gap: 0.2em;
        max-width: 80%;
        width: auto;
        margin: 1em;
        flex-shrink: 1;
    }
</style>
