<script lang="ts">
    export let element;
    export let onClick = (element: JSON) => {};

    type elementGroups =
        | "alkali-metal"
        | "nonmetal"
        | "noble-gas"
        | "metalloid"
        | "alkaline-earth-metal"
        | "transition-metal"
        | "post-transition-metal"
        | "actinide"
        | "lanthanide"
        | "halogen";

    const colors: { [key in elementGroups]: string } = {
        // lightness variation to improve color accessibility
        "alkali-metal": "hsl(10, 65%, 65%)",
        "alkaline-earth-metal": "hsl(25, 60%, 70%)",
        "transition-metal": "hsl(40, 55%, 75%)",
        "post-transition-metal": "hsl(55, 60%, 80%)",
        metalloid: "hsl(80, 45%, 72%)",
        nonmetal: "hsl(160, 55%, 68%)",
        halogen: "hsl(200, 60%, 72%)",
        "noble-gas": "hsl(220, 55%, 76%)",
        lanthanide: "hsl(280, 50%, 75%)",
        actinide: "hsl(300, 55%, 70%)",
    };
</script>

<button
    class="element-btn aspect-square w-[2.5vw] rounded-lg min-w-[1.5em] min-h-[1.5em]"
    style="grid-column: {element.column}; grid-row: {element.row}; background: {colors[
        element.category
    ]};"
    aria-label={element.name}
    on:click={() => onClick(element)}
>
    <div>{element.symbol}</div></button
>

<style>
    .element-btn:hover {
        filter: brightness(90%);
        cursor: pointer;
    }
</style>
