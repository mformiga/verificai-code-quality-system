// Proxy serverless function to bypass CORS
module.exports = async (req, res) => {
  // Add CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  try {
    const backendUrl = 'https://verificai-backend-1mmrfd0n7-mauricios-projects-b3859180.vercel.app';
    const { url, method, headers, body } = req;

    // Remove host header to avoid conflicts
    const { host, ...forwardHeaders } = headers;

    // Make the request to the backend
    const response = await fetch(`${backendUrl}${url}`, {
      method,
      headers: {
        ...forwardHeaders,
        'Content-Type': headers['content-type'] || 'application/json',
      },
      body: method !== 'GET' && method !== 'HEAD' ? body : undefined,
    });

    // Forward the response
    const responseText = await response.text();

    res.status(response.status);

    // Copy response headers
    response.headers.forEach((value, name) => {
      if (name.toLowerCase() !== 'content-encoding') {
        res.setHeader(name, value);
      }
    });

    res.send(responseText);
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({
      error: 'Proxy error',
      message: error.message
    });
  }
};