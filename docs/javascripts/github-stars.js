// Live GitHub star counts for project cards and project pages.
// Cached in localStorage for 24 hours to stay well within GitHub's anonymous API rate limits.
const STAR_CACHE_TTL = 24 * 60 * 60 * 1000

document$.subscribe(() => {
  for (const el of document.querySelectorAll("[data-github-stars]")) {
    const repo = el.dataset.githubStars
    if (!repo) continue
    const key = `github-stars:${repo}`
    const show = (stars) => {
      el.lastElementChild.textContent = Number(stars).toLocaleString("en")
      el.hidden = false
    }
    try {
      const cached = JSON.parse(localStorage.getItem(key))
      if (cached && Date.now() - cached.time < STAR_CACHE_TTL) {
        show(cached.stars)
        continue
      }
    } catch (_) {}

    fetch(`https://api.github.com/repos/${repo}`)
      .then((res) => (res.ok ? res.json() : Promise.reject(res.status)))
      .then(({ stargazers_count: stars }) => {
        try {
          localStorage.setItem(key, JSON.stringify({ stars, time: Date.now() }))
        } catch (_) {}
        show(stars)
      })
      .catch(() => {})
  }
})
