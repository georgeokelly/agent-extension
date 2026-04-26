# arXiv-Like HTML Document Reference

Use this reference when producing a standalone academic HTML document from
Markdown or existing HTML. It is inspired by arXiv/ar5iv document pages, but it
must not copy branding or imply affiliation.

Useful external references:

- arXiv HTML announcement paper: <https://arxiv.org/abs/2402.08954>
- Example ar5iv HTML document: <https://ar5iv.labs.arxiv.org/html/2402.08954v1>
- ar5iv service repository: <https://github.com/dginev/ar5iv>
- ar5iv CSS repository: <https://github.com/dginev/ar5iv-css>

## Document Structure

Prefer this shell:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Document title</title>
  <style>
    /* Inline CSS here. */
  </style>
</head>
<body>
  <main class="page">
    <article class="paper">
      <header class="paper-header">
        <h1>Document title</h1>
        <p class="paper-meta">Optional authors, date, or source note</p>
      </header>
      <!-- Rendered Markdown or HTML content -->
    </article>
  </main>
</body>
</html>
```

## Baseline CSS

Use this as a compact starting point and adapt to the document:

```css
:root {
  color-scheme: light dark;
  --page-bg: #ffffff;
  --text: #222222;
  --muted: #555555;
  --border: #d6d6d6;
  --link: #1f5f9f;
  --code-bg: #f5f5f5;
  --figure-bg: #fafafa;
  --main-width: 52rem;
}

@media (prefers-color-scheme: dark) {
  :root {
    --page-bg: #101418;
    --text: #d8dee9;
    --muted: #a7b0bc;
    --border: #3a4552;
    --link: #8ab4f8;
    --code-bg: #171d24;
    --figure-bg: #151b22;
  }
}

* {
  box-sizing: border-box;
}

html {
  background: var(--page-bg);
  color: var(--text);
}

body {
  margin: 0;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 17px;
  line-height: 1.65;
  text-rendering: optimizeLegibility;
}

.page {
  width: 100%;
  padding: 3rem 1rem 5rem;
}

.paper {
  max-width: var(--main-width);
  margin: 0 auto;
}

.paper-header {
  margin: 0 0 2.5rem;
  text-align: center;
}

h1,
h2,
h3,
h4,
h5,
h6 {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.25;
  margin: 2rem 0 0.8rem;
}

h1 {
  font-size: 2rem;
  font-weight: 650;
  margin-top: 0;
}

h2 {
  font-size: 1.35rem;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.25rem;
}

h3 {
  font-size: 1.1rem;
}

.paper-meta {
  color: var(--muted);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 0.95rem;
  line-height: 1.45;
}

a {
  color: var(--link);
  text-decoration-thickness: 0.08em;
  text-underline-offset: 0.16em;
}

p {
  margin: 0 0 1rem;
}

blockquote {
  border-left: 3px solid var(--border);
  color: var(--muted);
  margin: 1.3rem 0;
  padding: 0.1rem 0 0.1rem 1rem;
}

figure {
  margin: 1.8rem auto;
  padding: 1rem;
  background: var(--figure-bg);
  border: 1px solid var(--border);
}

figure img {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 0 auto;
}

figcaption {
  color: var(--muted);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 0.9rem;
  line-height: 1.45;
  margin-top: 0.75rem;
  text-align: center;
}

pre {
  overflow-x: auto;
  padding: 1rem;
  background: var(--code-bg);
  border: 1px solid var(--border);
}

code,
kbd,
samp {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.92em;
}

:not(pre) > code {
  background: var(--code-bg);
  border: 1px solid var(--border);
  padding: 0.05rem 0.25rem;
}

table {
  display: block;
  width: 100%;
  overflow-x: auto;
  border-collapse: collapse;
  margin: 1.4rem 0;
}

th,
td {
  border: 1px solid var(--border);
  padding: 0.45rem 0.6rem;
  vertical-align: top;
}

th {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  text-align: left;
}

hr {
  border: 0;
  border-top: 1px solid var(--border);
  margin: 2rem 0;
}

@media (max-width: 640px) {
  body {
    font-size: 16px;
  }

  .page {
    padding: 1.5rem 0.9rem 3rem;
  }

  h1 {
    font-size: 1.6rem;
  }
}
```

## Local Image Embedding

Resolve each local image reference relative to the source file or the supplied
asset root:

```markdown
![Training curve](assets/curve.png)
```

Convert it to:

```html
<img src="data:image/png;base64,..." alt="Training curve">
```

Rules:

- Preserve meaningful `alt` text from Markdown or HTML.
- If the source has an image followed by an italic paragraph such as
  `*Figure 1: ...*`, wrap the image and caption in `<figure>`.
- Keep remote `https://` image URLs external unless strict offline output is
  requested and the user approves fetching remote assets.
- Do not embed files with unknown MIME types.

## Verification Checklist

Before delivery, verify:

- The file opens locally.
- No `src="assets/..."`
  or other unresolved local image path remains in the final HTML.
- Images render at desktop and mobile widths.
- Long code blocks and wide tables scroll horizontally instead of breaking page layout.
- Text does not require horizontal scrolling on mobile.
- Strict offline output has no unintended `http://` or `https://` dependencies.
