const expanders = document.querySelectorAll(".frame .expander");

for (const expander of expanders) {
  expander.addEventListener("click", (evt) => {
    const currentSnippet = evt.currentTarget.closest(".frame");
    const snippetWrapper = currentSnippet.querySelector(
      ".code-snippet-wrapper",
    );
    if (currentSnippet.classList.contains("collapsed")) {
      snippetWrapper.style.height = `${snippetWrapper.scrollHeight}px`;
      currentSnippet.classList.remove("collapsed");
    } else {
      currentSnippet.classList.add("collapsed");
      snippetWrapper.style.height = "0px";
    }
  });
}

// init height for non-collapsed code snippets so animation will be show
// their first collapse
const nonCollapsedSnippets = document.querySelectorAll(
  ".frame:not(.collapsed) .code-snippet-wrapper",
);

for (const snippet of nonCollapsedSnippets) {
  snippet.style.height = `${snippet.scrollHeight}px`;
}
