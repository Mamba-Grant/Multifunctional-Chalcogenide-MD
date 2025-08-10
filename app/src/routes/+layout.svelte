<script>
    import { injectSpeedInsights } from "@vercel/speed-insights/sveltekit";
    let { children } = $props();
    import "../app.css";
    injectSpeedInsights();
</script>

{@render children()}
