// Optional relay for the Admiralty UK Tidal API.
// Deploy as a Cloudflare Worker. Set a secret called ADMIRALTY_KEY to your API key,
// then paste the worker URL into the planner's "Relay URL" field.
// The planner calls  <relay>/Stations  and  <relay>/Stations/{id}/TidalEvents?duration=7

const UPSTREAM = 'https://admiraltyapi.azure-api.net/uktidalapi/api/V1';
const ALLOWED_ORIGIN = '*'; // tighten to 'https://<your-username>.github.io' once it works

export default {
  async fetch(request, env) {
    const cors = {
      'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
      'Access-Control-Allow-Headers': 'Ocp-Apim-Subscription-Key',
      'Access-Control-Allow-Methods': 'GET, OPTIONS'
    };
    if (request.method === 'OPTIONS') return new Response(null, { headers: cors });
    if (request.method !== 'GET') return new Response('Method not allowed', { status: 405, headers: cors });

    const url = new URL(request.url);
    if (!/^\/Stations(\/[\w-]+\/TidalEvents)?$/.test(url.pathname)) {
      return new Response('Not found', { status: 404, headers: cors });
    }
    const upstream = await fetch(UPSTREAM + url.pathname + url.search, {
      headers: { 'Ocp-Apim-Subscription-Key': env.ADMIRALTY_KEY }
    });
    const body = await upstream.text();
    return new Response(body, {
      status: upstream.status,
      headers: { ...cors, 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=3600' }
    });
  }
};
