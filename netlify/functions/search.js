const { Client } = require('pg');

// Database configuration
const getDbConfig = () => {
  // Use individual parameters instead of connection string for better DNS resolution
  return {
    host: process.env.DB_HOST || 'db.nbohnrjmtoyrxrxqulrj.supabase.co',
    port: parseInt(process.env.DB_PORT || '5432'),
    database: process.env.DB_NAME || 'postgres',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD || '10Stomathima!',
    ssl: {
      rejectUnauthorized: false
    }
  };
};

exports.handler = async (event, context) => {
  console.log('='.repeat(50));
  console.log('SEARCH FUNCTION CALLED');
  console.log('Event:', JSON.stringify(event, null, 2));
  console.log('Context:', context);
  
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
    
    // Connect to database
    console.log('Connecting to database...');
    const dbConfig = getDbConfig();
    console.log('Using config:', { 
      host: dbConfig.host, 
      port: dbConfig.port, 
      database: dbConfig.database, 
      user: dbConfig.user 
    });
    const client = new Client(dbConfig);
    await client.connect();
    console.log('✓ Database connection established');
    
    // Build full-text search query
    const searchQuery = `
      SELECT 
        id,
        title,
        LEFT(abstract, 500) AS abstract_preview,
        ts_rank_cd(
          (title_tsv || abstract_tsv),
          plainto_tsquery('english', $1)
        ) AS rank
      FROM docs
      WHERE (title_tsv || abstract_tsv) @@ plainto_tsquery('english', $1)
      ORDER BY rank DESC
      LIMIT 50
    `;
    
    console.log('Executing search query...');
    const result = await client.query(searchQuery, [query]);
    const results = result.rows;
    console.log(`Found ${results.length} results`);
    
    await client.end();
    console.log('Database connection closed');
    
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

