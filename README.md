# Grampian Passage Planner

A passage planner for the Grampian 234 (1.5 m draught, ~5 kn), built to run as an iPhone home-screen app and work offline at sea.

- Multi-leg voyages with a departure-window strip for each leg
- Tidal heights and streams, under-keel clearance at shallow waypoints, wind-over-tide warnings
- Navionics GPX import, pasted waypoints, ~70 UK and near-Continent marinas
- Bail-out ports, sunrise/sunset, pre-departure checklist (WOBBLE, rig, safety)
- Live tides (UKHO Admiralty UK Tidal API) and wind (Open-Meteo), saved on the phone for offline use

## Files

| File | What it does |
|---|---|
| `index.html` | The whole app |
| `manifest.webmanifest` | Name, icon and full-screen launch for Add to Home Screen |
| `sw.js` | Stores the app on the phone so it opens offline |
| `icons/` | App icons |
| `relay/worker.js` | Optional Cloudflare Worker, only needed if Admiralty refuses direct requests |

## Hosting on GitHub Pages

1. Create a public repository called `passage-planner` and upload these files (keep the `icons` folder).
2. In the repository, open **Settings → Pages**, set **Source** to *Deploy from a branch*, branch `main`, folder `/ (root)`, and save.
3. After a minute the app is live at `https://<your-username>.github.io/passage-planner/`.

## Installing on the iPhone

Open the link in **Safari**, tap **Share → Add to Home Screen**. Launch it once with signal so it saves itself for offline use.

## Live data

- **Tides:** paste your Admiralty API key into *Live data* (section 09). Fetch in harbour; the 7 days of tides stay saved.
- **Wind:** no key needed.
- **If tide fetches fail with signal**, Admiralty is probably refusing requests from web pages. Deploy `relay/worker.js` as a free Cloudflare Worker, add your key there as the secret `ADMIRALTY_KEY`, and paste the worker's URL into *Relay URL*.

## Updating

Change `index.html`, bump `VERSION` in `sw.js`, and push. The phone picks up the new version next time it opens with signal.

Positions in the built-in marina list and route library are approximate. Check them against the chart, and use your own GPX routes for pilotage.
