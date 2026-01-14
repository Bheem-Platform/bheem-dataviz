/**
 * Bheem DataViz JavaScript SDK
 * 
 * Usage:
 *   import { DataVizClient } from '@bheem/dataviz-sdk';
 *   const client = new DataVizClient({ apiUrl: 'https://api.dataviz.bheemkodee.com' });
 *   const dashboards = await client.dashboards.list();
 */

class DataVizClient {
  constructor({ apiUrl, apiKey }) {
    this.apiUrl = apiUrl.replace(/\/$/, '');
    this.apiKey = apiKey;
    this.headers = {
      'Content-Type': 'application/json',
      ...(apiKey && { 'Authorization': `Bearer ${apiKey}` })
    };

    this.connections = new ConnectionsAPI(this);
    this.datasets = new DatasetsAPI(this);
    this.dashboards = new DashboardsAPI(this);
    this.charts = new ChartsAPI(this);
    this.queries = new QueriesAPI(this);
  }

  async request(method, path, data) {
    const response = await fetch(`${this.apiUrl}/api/v1${path}`, {
      method,
      headers: this.headers,
      body: data ? JSON.stringify(data) : undefined
    });
    return response.json();
  }
}

class ConnectionsAPI {
  constructor(client) { this.client = client; }
  list() { return this.client.request('GET', '/connections'); }
  create(data) { return this.client.request('POST', '/connections', data); }
  get(id) { return this.client.request('GET', `/connections/${id}`); }
  test(id) { return this.client.request('POST', `/connections/${id}/test`); }
}

class DatasetsAPI {
  constructor(client) { this.client = client; }
  list() { return this.client.request('GET', '/datasets'); }
  create(data) { return this.client.request('POST', '/datasets', data); }
  preview(id, limit = 100) { return this.client.request('GET', `/datasets/${id}/preview?limit=${limit}`); }
}

class DashboardsAPI {
  constructor(client) { this.client = client; }
  list() { return this.client.request('GET', '/dashboards'); }
  create(data) { return this.client.request('POST', '/dashboards', data); }
  get(id) { return this.client.request('GET', `/dashboards/${id}`); }
  update(id, data) { return this.client.request('PUT', `/dashboards/${id}`, data); }
}

class ChartsAPI {
  constructor(client) { this.client = client; }
  list() { return this.client.request('GET', '/charts'); }
  create(data) { return this.client.request('POST', '/charts', data); }
  render(id) { return this.client.request('GET', `/charts/${id}/render`); }
}

class QueriesAPI {
  constructor(client) { this.client = client; }
  execute(connectionId, sql, limit = 1000) {
    return this.client.request('POST', '/queries/execute', { connection_id: connectionId, sql, limit });
  }
}

export { DataVizClient };
