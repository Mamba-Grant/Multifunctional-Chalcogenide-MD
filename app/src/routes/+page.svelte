<script lang="ts">
    let testitem = {
        "MP-ID": 123,
        formula: "H2O",
        spacegroup: "P2₁/c",
        "band gap": 1.23,
    };

    // import Card from "$lib/components/v3_Card.svelte";
    import PeriodicTable from "$lib/components/PeriodicTable.svelte";
    import SearchBox from "$lib/components/SearchBox.svelte";
    import { writable, derived } from "svelte/store";
    import { searchQuery, materials } from "$lib/store";
    import Fuse from "fuse.js";
    import TableRow from "$lib/components/TableRow.svelte";

    // Load materials on mount
    import { onMount } from "svelte";
    onMount(async () => {
        try {
            const res = await fetch("/api/get_all");
            // const res = await fetch("http://127.0.0.1:8000/v1/material_data");
            const data = await res.json();
            materials.set(data);
        } catch (err) {
            console.error("Failed to load materials:", err);
        }
    });

    interface Filter {
        field: string;
        operator: string;
        value: any;
    }

    function parseQuery(query: string): {
        filters: Filter[];
        generalSearch: string;
    } {
        const filters: Filter[] = [];

        // Enhanced regex to capture field:operator:value patterns
        const filterPattern = /(\w+):([<>=!]*)([\w\d.,\-\+]+)/g;
        const matches = [...query.matchAll(filterPattern)];

        // Extract all filters and keep track of what to remove
        const filterStrings: string[] = [];

        for (const match of matches) {
            const [fullMatch, field, operator, value] = match;
            filterStrings.push(fullMatch);

            let processedValue: any = value;

            // Handle comma-separated values (chemical_symbols)
            if (value.includes(",")) {
                processedValue = value.split(",").map((v) => v.trim());
            }
            // Handle numeric values
            else if (!isNaN(Number(value))) {
                processedValue = Number(value);
            }

            // Additionally make sure that this kind of filter wraps in array (necessary in cases like elements:Sb)
            if (field === "elements") {
                processedValue = Array.isArray(processedValue)
                    ? processedValue
                    : [processedValue];
            }

            filters.push({
                field: field.toLowerCase(),
                operator: operator || "=",
                value: processedValue,
            });
        }

        // Remove all filter strings from the query to get the general search
        let remainingQuery = query;
        for (const filterStr of filterStrings) {
            remainingQuery = remainingQuery.replace(filterStr, "");
        }

        return {
            filters,
            generalSearch: remainingQuery.trim(),
        };
    }

    function applyFilters(materials: any[], filters: Filter[]): any[] {
        return materials.filter((material, index) => {
            const result = filters.every((filter) => {
                const { field, operator, value } = filter;

                // Assign field value as objects to compare against
                let fieldValue = null;
                switch (field) {
                    case "elements":
                        fieldValue = material.chemical_symbols || [];
                        break;

                    case "bandgap":
                        fieldValue = material["band gap"];
                        break;

                    case "spacegroup":
                        fieldValue = material.spacegroup;
                        break;
                }

                // Check all values in the array (e.g. elements filter)
                if (Array.isArray(value)) {
                    if (Array.isArray(fieldValue)) {
                        const hasMatch = value
                            .map((str) => str.toLowerCase())
                            .every((v) => fieldValue.includes(v));
                        return hasMatch;
                    }
                }

                // Numeric comparisons (e.g. bandgap)
                if (
                    typeof value === "number" &&
                    typeof fieldValue === "number"
                ) {
                    let result = false;
                    switch (operator) {
                        case "<":
                            result = fieldValue < value;
                            break;
                        case "<=":
                            result = fieldValue <= value;
                            break;
                        case ">":
                            result = fieldValue > value;
                            break;
                        case ">=":
                            result = fieldValue >= value;
                            break;
                        case "!=":
                        case "!":
                            result = fieldValue !== value;
                            break;
                        case "=":
                        default:
                            result = fieldValue === value;
                    }
                    return result;
                }

                // String comparisons (e.g. spacegroup)
                if (typeof fieldValue === "string") {
                    const fieldStr = fieldValue.toLowerCase();
                    const valueStr = value.toString().toLowerCase();
                    let result = false;

                    switch (operator) {
                        case "!=":
                        case "!":
                            result = fieldStr !== valueStr;
                            break;
                        case "=":
                        default:
                            result = fieldStr.includes(valueStr);
                    }
                    return result;
                }

                // Default equality check
                const defaultResult = fieldValue === value;
                return defaultResult;
            });

            return result;
        });
    }

    const filteredMaterials = derived(
        [materials, searchQuery],
        ([$materials, $searchQuery]) => {
            if (!$searchQuery.trim()) {
                return $materials;
            }

            const { filters, generalSearch } = parseQuery($searchQuery);

            // Apply filters first
            let filtered = $materials;
            if (filters.length > 0) {
                filtered = applyFilters(filtered, filters);
            }

            // Apply general search using Fuse if there's remaining text
            if (generalSearch) {
                const fuse = new Fuse(filtered, {
                    keys: [
                        "formula",
                        "MP-ID",
                        "spacegroup",
                        "chemical_symbols",
                    ],
                    threshold: 0.3,
                });
                filtered = fuse.search(generalSearch).map((r) => r.item);
            }

            return filtered;
        },
    );
</script>

<div class="mb-4 flex flex-col items-center w-auto shrink">
    <PeriodicTable />
    <SearchBox />
</div>

<div class="flex flex-col items-center max-w-[60vw] w-auto shrink mx-auto">
    <!-- Header -->
    <div class="grid grid-cols-[15vw_15vw_15vw_15vw] gap-4 font-bold">
        <div class="text-center text-[clamp(0.75rem,1.5vw,1rem)]">MP-ID</div>
        <div class="text-center text-[clamp(0.75rem,1.5vw,1rem)]">Formula</div>
        <div class="text-center text-[clamp(0.75rem,1.5vw,1rem)]">
            Spacegroup
        </div>
        <div class="text-center text-[clamp(0.75rem,1.5vw,1rem)]">Bandgap</div>
        <!-- <div class="ml-2"> -->
        <!--     <svg -->
        <!--         width="16" -->
        <!--         height="16" -->
        <!--         viewBox="0 0 24 24" -->
        <!--         fill="none" -->
        <!--         stroke="currentColor" -->
        <!--         stroke-width="2" -->
        <!--     ></svg> -->
        <!-- </div> -->
    </div>

    <!-- <TableRow {item} /> -->

    <!-- Results -->
    {#each $filteredMaterials as item}
        <!-- <Card {item} /> -->
        <!-- <TableRow {testitem} /> -->
        <TableRow {item} />
    {/each}

    <!-- Show results count -->
    <div class="text-sm text-gray-600 mt-4">
        Showing {$filteredMaterials.length} materials
    </div>
</div>
