// Rogue Scholar (InvenioRDM) live DOI resolution & one-click BibTeX citation copy.
// Queries rogue-scholar.org/api/records once per 24h (cached in localStorage) to hydrate
// newly minted DOIs on the Home ledger and Article pages, and handles COPY BIBTEX.

const ROGUE_CACHE_KEY = "rogue-scholar:tomdstanton.com:v2"
const ROGUE_CACHE_TTL = 24 * 60 * 60 * 1000

function normalizePostUrl(url) {
  if (!url) return ""
  return url.trim().replace(/^https?:\/\//, "").replace(/\/+$/, "").toLowerCase()
}

function cleanDoi(doi) {
  if (!doi) return ""
  return doi.trim().replace(/^https?:\/\/(dx\.)?doi\.org\//i, "")
}

function extractRecordUrls(rec) {
  const urls = []
  const meta = (rec && rec.metadata) || {}
  for (const item of meta.identifiers || []) {
    if (item && item.identifier && (item.scheme === "url" || /^https?:\/\//i.test(item.identifier))) {
      urls.push(item.identifier)
    }
  }
  for (const item of meta.related_identifiers || []) {
    if (item && item.identifier && (item.scheme === "url" || /^https?:\/\//i.test(item.identifier))) {
      urls.push(item.identifier)
    }
  }
  if (rec && rec.url) urls.push(rec.url)
  return urls
}

async function fetchRogueScholarMap() {
  try {
    const cached = JSON.parse(localStorage.getItem(ROGUE_CACHE_KEY))
    if (cached && Date.now() - cached.time < ROGUE_CACHE_TTL && cached.map) {
      return cached.map
    }
  } catch (_) {}

  try {
    const res = await fetch(
      "https://rogue-scholar.org/api/records?q=tomdstanton.com&size=100",
      { headers: { Accept: "application/json" } }
    )
    if (!res.ok) return {}
    const data = await res.json()
    const records = (data.hits && Array.isArray(data.hits.hits))
      ? data.hits.hits
      : Array.isArray(data.hits)
        ? data.hits
        : []

    const map = {}
    for (const rec of records) {
      const doi = cleanDoi(rec?.pids?.doi?.identifier || rec?.doi)
      if (!doi) continue
      for (const rawUrl of extractRecordUrls(rec)) {
        const urlKey = normalizePostUrl(rawUrl)
        if (urlKey.includes("tomdstanton.com/")) {
          map[urlKey] = doi
        }
      }
    }
    try {
      localStorage.setItem(ROGUE_CACHE_KEY, JSON.stringify({ map, time: Date.now() }))
    } catch (_) {}
    return map
  } catch (_) {
    return {}
  }
}

function buildFallbackBibtex({ title, year, date, slug, url, doi }) {
  const key = `stanton${year}${String(slug || "dispatch").replace(/[^a-z0-9]/gi, "")}`
  const lines = [
    `@article{${key},`,
    `  author = {Stanton, Tom D.},`,
    `  title = {{${title}}},`,
    `  journal = {Bytes \\& Bacteria},`,
    `  year = {${year}},`,
    `  date = {${date}},`,
  ]
  if (doi) {
    lines.push(`  doi = {${doi}},`)
    lines.push(`  url = {https://doi.org/${doi}}`)
  } else {
    lines.push(`  url = {${url}}`)
  }
  lines.push(`}`)
  return lines.join("\n")
}

function ensureCitationDoiMeta(doi) {
  if (!doi || document.querySelector('meta[name="citation_doi"]')) return
  const meta = document.createElement("meta")
  meta.name = "citation_doi"
  meta.content = doi
  document.head.appendChild(meta)
}

document$.subscribe(async () => {
  const pendingBadges = [...document.querySelectorAll("[data-rogue-doi-url]")]
  const citeBox = document.querySelector("[data-cite-box]")

  if (pendingBadges.length > 0 || (citeBox && !citeBox.dataset.citeDoi)) {
    const doiMap = await fetchRogueScholarMap()

    for (const el of pendingBadges) {
      const key = normalizePostUrl(el.dataset.rogueDoiUrl)
      const doi = doiMap[key]
      if (!doi) continue
      el.href = `https://doi.org/${doi}`
      const textSpan = el.querySelector("[data-rogue-doi-text]")
      if (textSpan) textSpan.textContent = doi
      el.hidden = false
    }

    if (citeBox && !citeBox.dataset.citeDoi) {
      const key = normalizePostUrl(citeBox.dataset.citeUrl)
      const doi = doiMap[key]
      if (doi) {
        citeBox.dataset.citeDoi = doi
        ensureCitationDoiMeta(doi)
        const link = citeBox.querySelector("[data-cite-doi-link]")
        if (link) {
          link.href = `https://doi.org/${doi}`
          link.textContent = `https://doi.org/${doi}`
          link.target = "_blank"
          link.rel = "noopener"
        }
      }
    }
  }

  for (const btn of document.querySelectorAll("[data-copy-bibtex]")) {
    if (btn.dataset.bound === "1") continue
    btn.dataset.bound = "1"
    btn.addEventListener("click", async () => {
      const box = btn.closest("[data-cite-box]")
      if (!box) return
      const doi = cleanDoi(box.dataset.citeDoi)
      let bibtex = ""

      if (doi) {
        try {
          const res = await fetch(`https://doi.org/${doi}`, {
            headers: { Accept: "application/x-bibtex" },
          })
          if (res.ok) {
            const text = (await res.text()).trim()
            if (text.startsWith("@")) bibtex = text
          }
        } catch (_) {}
      }

      if (!bibtex) {
        bibtex = buildFallbackBibtex({
          title: box.dataset.citeTitle,
          year: box.dataset.citeYear,
          date: box.dataset.citeDate,
          slug: box.dataset.citeSlug,
          url: box.dataset.citeUrl,
          doi,
        })
      }

      try {
        await navigator.clipboard.writeText(bibtex)
        const prev = btn.textContent
        btn.textContent = "COPIED BIBTEX ✓"
        setTimeout(() => {
          btn.textContent = prev
        }, 2000)
      } catch (_) {}
    })
  }
})
