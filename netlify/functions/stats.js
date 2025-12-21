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
  console.log('STATS FUNCTION CALLED');
  
  try {
    console.log('Fetching stats from Supabase REST API...');
    
    // Get total count using HEAD request with Prefer: count=exact
    const countUrl = `${SUPABASE_URL}/rest/v1/docs?select=id&limit=1`;
    console.log('Requesting count from:', countUrl);
    
    const countResponse = await makeRequest(countUrl, {
      method: 'HEAD',
      headers: {
        'Prefer': 'count=exact'
      }
    });
    
    // Parse count from Content-Range header
    const contentRange = countResponse.headers['content-range'];
    let total = 0;
    if (contentRange) {
      // Format: "0-0/1234" or "*/1234"
      const match = contentRange.match(/\/(\d+)/);
      if (match) {
        total = parseInt(match[1]);
      }
    }
    
    console.log(`Total documents from header: ${total}`);
    
    // If we didn't get count from header, fetch with a limit to get count
    if (total === 0) {
      const countQuery = `${SUPABASE_URL}/rest/v1/rpc/count_docs`;
      try {
        const rpcResponse = await makeRequest(countQuery, {
          method: 'POST',
          headers: {
            'Prefer': 'return=representation'
          }
        });
        if (rpcResponse.data && typeof rpcResponse.data === 'number') {
          total = rpcResponse.data;
        } else if (rpcResponse.data && rpcResponse.data[0] && rpcResponse.data[0].count) {
          total = parseInt(rpcResponse.data[0].count);
        }
      } catch (rpcError) {
        console.log('RPC count failed, using alternative method');
      }
    }
    
    // If still no count, use a workaround - fetch all and count (limited)
    if (total === 0) {
      const allDocs = await makeRequest(`${SUPABASE_URL}/rest/v1/docs?select=id&limit=1000`, {
        method: 'GET'
      });
      if (allDocs.data && Array.isArray(allDocs.data)) {
        total = allDocs.data.length;
        // If we got 1000, there might be more
        if (total === 1000) {
          total = 1000; // At least 1000
        }
      }
    }
    
    // Get documents with title/abstract
    const withTitleQuery = `${SUPABASE_URL}/rest/v1/docs?select=id&title=not.is.null&title=neq.&limit=1`;
    const withTitleResponse = await makeRequest(withTitleQuery, {
      method: 'HEAD',
      headers: {
        'Prefer': 'count=exact'
      }
    });
    
    let withTitle = 0;
    const titleRange = withTitleResponse.headers['content-range'];
    if (titleRange) {
      const match = titleRange.match(/\/(\d+)/);
      if (match) {
        withTitle = parseInt(match[1]);
      }
    }
    
    const withAbstractQuery = `${SUPABASE_URL}/rest/v1/docs?select=id&abstract=not.is.null&abstract=neq.&limit=1`;
    const withAbstractResponse = await makeRequest(withAbstractQuery, {
      method: 'HEAD',
      headers: {
        'Prefer': 'count=exact'
      }
    });
    
    let withAbstract = 0;
    const abstractRange = withAbstractResponse.headers['content-range'];
    if (abstractRange) {
      const match = abstractRange.match(/\/(\d+)/);
      if (match) {
        withAbstract = parseInt(match[1]);
      }
    }
    
    console.log(`Stats: total=${total}, with_title=${withTitle}, with_abstract=${withAbstract}`);
    
    const response = {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        total_documents: total,
        with_title: withTitle,
        with_abstract: withAbstract
      })
    };
    
    console.log('Returning stats response:', response.body);
    return response;
    
  } catch (error) {
    console.error('ERROR in stats function:', error);
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
