const https = require('https');

// Supabase REST API configuration
const SUPABASE_URL = process.env.SUPABASE_URL || 'https://nbohnrjmtoyrxrxqulrj.supabase.co';
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5ib2hucmptdG95cnhyeHF1bHJqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYxNTY4NDEsImV4cCI6MjA4MTczMjg0MX0.95sUDYi4hEPgZ1kXYUOvLMpxTb6O4VIYLf_3nckBbdQ';

// Helper function to make HTTPS requests
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const req = https.request(url, options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          resolve({ status: res.statusCode, data: jsonData });
        } catch (e) {
          resolve({ status: res.statusCode, data: data });
        }
      });
    });
    
    req.on('error', (error) => {
      reject(error);
    });
    
    if (options.body) {
      req.write(options.body);
    }
    
    req.end();
  });
}

exports.handler = async (event, context) => {
  console.log('='.repeat(50));
  console.log('STATS FUNCTION CALLED');
  console.log('Event:', JSON.stringify(event, null, 2));
  
  try {
    // Get total document count using Supabase REST API
    console.log('Fetching stats from Supabase REST API...');
    
    const countUrl = `${SUPABASE_URL}/rest/v1/rpc/get_doc_count`;
    const statsUrl = `${SUPABASE_URL}/rest/v1/rpc/get_doc_stats`;
    
    // First, try to get count using a simple query
    const countQueryUrl = `${SUPABASE_URL}/rest/v1/docs?select=id&limit=1`;
    const countResponse = await makeRequest(countQueryUrl, {
      method: 'HEAD',
      headers: {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Prefer': 'count=exact'
      }
    });
    
    // Get total count from Content-Range header or use a different approach
    // Use a direct SQL query via REST API
    const sqlUrl = `${SUPABASE_URL}/rest/v1/rpc/exec_sql`;
    
    // Since we can't use RPC directly, let's use the PostgREST query
    // Get count by selecting all and using count
    const queryUrl = `${SUPABASE_URL}/rest/v1/docs?select=*&limit=0`;
    
    // Actually, let's use a simpler approach - query with limit 0 to get count
    const response = await makeRequest(queryUrl, {
      method: 'GET',
      headers: {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Prefer': 'count=exact',
        'Range': '0-0'
      }
    });
    
    // Parse count from Content-Range header if available
    // For now, let's use a different approach - make multiple queries
    const totalQuery = `${SUPABASE_URL}/rest/v1/docs?select=id&limit=1`;
    const totalResponse = await makeRequest(totalQuery, {
      method: 'HEAD',
      headers: {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Prefer': 'count=exact'
      }
    });
    
    // Since we can't easily get count, let's create a view or use a different method
    // For now, let's return a placeholder and use a workaround
    
    // Better approach: Use Supabase's built-in count via PostgREST
    // We'll need to create a function or use a workaround
    
    // For now, let's use a simple query that gets some data and estimate
    // Actually, the best way is to use the database directly but with proper connection
    
    // Let's try using the connection string with proper format
    const { Client } = require('pg');
    
    // Use the connection string format that Supabase provides
    const connectionString = process.env.DATABASE_URL || 
      'postgresql://postgres.xxxxxxxxxxxxx:10Stomathima!@aws-0-eu-central-1.pooler.supabase.com:6543/postgres';
    
    // Actually, let's use the direct connection with the project ref
    const directConnection = {
      host: 'db.nbohnrjmtoyrxrxqulrj.supabase.co',
      port: 5432,
      database: 'postgres',
      user: 'postgres.nbohnrjmtoyrxrxqulrj',
      password: '10Stomathima!',
      ssl: { rejectUnauthorized: false }
    };
    
    console.log('Connecting to database with direct connection...');
    const client = new Client(directConnection);
    
    try {
      await client.connect();
      console.log('✓ Database connection established');
      
      // Get total document count
      console.log('Executing COUNT query...');
      const countResult = await client.query('SELECT COUNT(*) AS total FROM docs;');
      const total = parseInt(countResult.rows[0].total);
      console.log(`Total documents: ${total}`);
      
      // Get documents with title/abstract
      console.log('Executing stats query...');
      const statsResult = await client.query(`
        SELECT 
          COUNT(*) FILTER (WHERE title IS NOT NULL AND title != '') AS with_title,
          COUNT(*) FILTER (WHERE abstract IS NOT NULL AND abstract != '') AS with_abstract
        FROM docs;
      `);
      const stats = statsResult.rows[0];
      console.log(`Stats: with_title=${stats.with_title}, with_abstract=${stats.with_abstract}`);
      
      await client.end();
      console.log('Database connection closed');
      
      const response = {
        statusCode: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify({
          total_documents: total,
          with_title: parseInt(stats.with_title),
          with_abstract: parseInt(stats.with_abstract)
        })
      };
      
      console.log('Returning stats response:', response.body);
      return response;
      
    } catch (dbError) {
      console.error('Database connection error:', dbError.message);
      throw dbError;
    }
    
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
