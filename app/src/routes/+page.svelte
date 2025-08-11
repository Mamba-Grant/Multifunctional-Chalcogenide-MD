<script lang="ts">
    import Card from "$lib/components/v3_Card.svelte";
    import PeriodicTable from "$lib/components/PeriodicTable.svelte";
    import SearchBox from "$lib/components/SearchBox.svelte";
    import Title from "$lib/components/Title.svelte";
    import { writable, derived } from "svelte/store";
    import { searchQuery, materials } from "$lib/store";
    import Fuse from "fuse.js";

    // Load materials on mount
    import { onMount } from "svelte";
    onMount(async () => {
        try {
            const res = await fetch("/api/get_all");
            const data = await res.json();
            materials.set(data);
            console.log(data);
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

<div class="flex flex-col items-center">
    <!-- Header -->
    <div
        class="flex p-3 min-h-12 bg-background hover:bg-primary/5"
        style="font-weight: bold; width: 90%;"
    >
        <div class="flex gap-4 flex-1">
            <div class="text-left text-muted-foreground w-24 break-words">
                MP-ID
            </div>
            <div class="text-left w-32 break-words">Formula</div>
            <div class="text-left text-muted-foreground w-28 break-words">
                Spacegroup
            </div>
            <div class="text-left text-muted-foreground w-28 break-words">
                Bandgap
            </div>
        </div>
        <div class="ml-2">
            <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
            ></svg>
        </div>
    </div>

    <!-- Results -->
    {#each $filteredMaterials as item}
        <Card {item} />
    {/each}

    <!-- Show results count -->
    <div class="text-sm text-gray-600 mt-4">
        Showing {$filteredMaterials.length} materials
    </div>
</div>
