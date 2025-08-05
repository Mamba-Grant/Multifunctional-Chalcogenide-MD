<script>
    export let item;

    // const structureInfo = [
    //     // { label: "Spacegroup", key: "spacegroup" },
    //     { label: "Layer group number", key: null },
    //     { label: "Structure origin", key: null },
    //     { label: "MP-ID", key: "MP-ID" },
    // ];

    const otherInfo = [
        { label: "Mass density", key: "mass density" },
        { label: "Total energy", key: "total energy" },
        {
            label: "Total energy with Spin-Orbit Coupling",
            key: "total energy_soc",
        },
        { label: "Cohesive Energy", key: "cohesive energy" },
        {
            label: "Born Effective Charge Tensor",
            key: "born effective charge tensor",
        },
        { label: "Born Effective q_xy", key: "born effective charge q_xy" },
        { label: "Born Effective q_z", key: "born effective charge q_z" },
        { label: "Dielectric Constant (xy)", key: "dielectric constant XY" },
        { label: "Dielectric Constant (z)", key: "dielectric constant Z" },
        {
            label: "Density of States at Fermi",
            key: "density of states at fermi",
        },
        // { label: "Effective Mass", key: "effective mass" },
        // { label: "vbm", key: "vbm" },
        // { label: "cbm", key: "cbm" },
        // { label: "Band Gap", key: "band gap" },
        // { label: "vbm With Spin-Orbit Coupling", key: "vbm soc" },
        // { label: "cbm With Spin-Orbit Coupling", key: "cbm soc" },
        // { label: "Band Gap With Spin-Orbit Coupling", key: "band gap soc" },
    ];
</script>

<!-- <h2 class="font-bold">Structure Info</h2> -->
<!-- <table class="table-fixed w-11/12 border border-gray-300"> -->
<!--     <tbody> -->
<!--         {#each structureInfo as row, i} -->
<!--             <tr class={i % 2 === 0 ? "bg-gray-100" : ""}> -->
<!--                 <th -->
<!--                     class="text-left border border-gray-300 px-4 py-2 font-medium" -->
<!--                 > -->
<!--                     {row.label} -->
<!--                 </th> -->
<!--                 <td class="border border-gray-300 px-4 py-2"> -->
<!--                     {row.key ? (item[row.key] ?? "N/A") : "N/A"} -->
<!--                 </td> -->
<!--             </tr> -->
<!--         {/each} -->
<!--     </tbody> -->
<!-- </table> -->

<!-- <h2 class="font-bold mt-6">Other Info</h2> -->
<table class="table-fixed w-11/12 border border-gray-300">
    <tbody>
        {#each otherInfo as row, i}
            <tr class={i % 2 === 0 ? "bg-gray-100" : ""}>
                <th
                    class="text-left border border-gray-300 px-4 py-2 font-medium"
                >
                    {row.label}
                </th>
                <td class="border border-gray-300 px-4 py-2">
                    {item[row.key] ?? "N/A"}
                </td>
            </tr>
        {/each}
    </tbody>
</table>

