(() => {
    // When the mdBook theme changes, rerender diagrams with a suitable Mermaid theme.
    const mermaids = [...document.querySelectorAll(".mermaid")];
    const texts = mermaids.map(x => x.textContent);
    const observer = new MutationObserver((mutations, observer) => {
        reinitMermaid();
    });
    observer.observe(document.documentElement, {
        attributeFilter: ["class"],
    });
    reinitMermaid();

    function reinitMermaid() {
        // Restore the original state of each diagram.
        for (const [i, pre] of mermaids.entries()) {
            delete pre.dataset.processed;
            pre.textContent = texts[i];
        }
        // Select a theme based on the mdBook theme, then rerender the diagrams.
        const rootClasses = document.documentElement.classList;
        mermaid.initialize({
            startOnLoad: false,
            theme: rootClasses.contains("light") || rootClasses.contains("rust") ? "default"
                : rootClasses.contains("coal") || rootClasses.contains("navy") || rootClasses.contains("ayu") ? "dark"
                : "default",
        });
        mermaid.run();
    }
})();
