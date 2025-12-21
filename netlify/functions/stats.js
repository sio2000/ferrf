const { Client } = require('pg');

// Database configuration
const getDbConfig = () => {
  // Use Supabase connection with project ref in username
  return {
    host: process.env.DB_HOST || 'db.nbohnrjmtoyrxrxqulrj.supabase.co',
    port: parseInt(process.env.DB_PORT || '5432'),
    database: process.env.DB_NAME || 'postgres',
    user: process.env.DB_USER || 'postgres.nbohnrjmtoyrxrxqulrj',
    password: process.env.DB_PASSWORD || '10Stomathima!',
    ssl: {
      rejectUnauthorized: false
    }
  };
};

exports.handler = async (event, context) => {
  console.log('='.repeat(50));
  console.log('STATS FUNCTION CALLED');
  console.log('Event:', JSON.stringify(event, null, 2));
  
  try {
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
