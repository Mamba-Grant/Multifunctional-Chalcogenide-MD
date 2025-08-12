export function loadPlotly() {
    if ((window as any).Plotly) return Promise.resolve();
    return new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src = "https://cdn.plot.ly/plotly-3.0.1.min.js";
        script.onload = () => resolve();
        script.onerror = () =>
            reject(new Error("Failed to load Plotly.js"));
        document.body.appendChild(script);
    });
}
