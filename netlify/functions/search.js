const https = require('https');

// Supabase REST API configuration
const SUPABASE_URL = process.env.SUPABASE_URL || 'https://nbohnrjmtoyrxrxqulrj.supabase.co';
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5ib2hucmptdG95cnhyeHF1bHJqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYxNTY4NDEsImV4cCI6MjA4MTczMjg0MX0.95sUDYi4hEPgZ1kXYUOvLMpxTb6O4VIYLf_3nckBbdQ';

// Helper function to make HTTPS requests
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const reqOptions = {
      hostname: urlObj.hostname,
      port: urlObj.port || 443,
      path: urlObj.pathname + urlObj.search,
      method: options.method || 'GET',
      headers: {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    };

    const req = https.request(reqOptions, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          resolve({ status: res.statusCode, data: jsonData, headers: res.headers });
        } catch (e) {
          resolve({ status: res.statusCode, data: data, headers: res.headers });
        }
      });
    });
    
    req.on('error', (error) => {
      reject(error);
    });
    
    if (options.body) {
      req.write(JSON.stringify(options.body));
    }
    
    req.end();
  });
}

exports.handler = async (event, context) => {
  console.log('='.repeat(50));
  console.log('SEARCH FUNCTION CALLED');
  
  try {
    // Get query parameter
    const queryParams = event.queryStringParameters || {};
    const query = (queryParams.q || '').trim();
    console.log('Search query:', query);
    
    if (!query) {
      return {
        statusCode: 400,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify({ error: 'Query is required' })
      };
    }
    
    // Use Supabase REST API with PostgREST full-text search
    // We need to use a stored function or use the text search directly
    // For now, let's use a simpler approach with ilike for partial matching
    // and then we can enhance with full-text search via RPC
    
    console.log('Searching via Supabase REST API...');
    
    // Try using RPC function for full-text search
    const searchRpcUrl = `${SUPABASE_URL}/rest/v1/rpc/search_docs`;
    let results = [];
    
    try {
      const rpcResponse = await makeRequest(searchRpcUrl, {
        method: 'POST',
        headers: {
          'Prefer': 'return=representation'
        },
        body: {
          search_query: query
        }
      });
      
      if (rpcResponse.status === 200 && Array.isArray(rpcResponse.data)) {
        results = rpcResponse.data;
        console.log(`Found ${results.length} results via RPC`);
      }
    } catch (rpcError) {
      console.log('RPC search failed, trying direct query:', rpcError.message);
      
      // Fallback: Use ilike for basic text search
      // URL encode the query
      const encodedQuery = encodeURIComponent(query);
      const searchUrl = `${SUPABASE_URL}/rest/v1/docs?select=id,title,abstract&or=(title.ilike.*${encodedQuery}*,abstract.ilike.*${encodedQuery}*)&limit=50`;
      
      const searchResponse = await makeRequest(searchUrl, {
        method: 'GET'
      });
      
      if (searchResponse.status === 200 && Array.isArray(searchResponse.data)) {
        results = searchResponse.data.map(doc => ({
          id: doc.id,
          title: doc.title || '',
          abstract_preview: (doc.abstract || '').substring(0, 500),
          rank: 1.0 // Simple rank for ilike search
        }));
        console.log(`Found ${results.length} results via ilike search`);
      }
    }
    
    const response = {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        query: query,
        count: results.length,
        results: results
      })
    };
    
    console.log(`Returning response with ${results.length} results`);
    return response;
    
  } catch (error) {
    console.error('ERROR in search function:', error);
    console.error('Stack:', error.stack);
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({ 
        error: error.message,
        stack: error.stack
      })
    };
  }
};
