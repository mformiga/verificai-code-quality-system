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
    const backendUrl = process.env.BACKEND_URL || 'https://verificai-backend-1mmrfd0n7-mauricios-projects-b3859180.vercel.app';
    const { url, method, headers, body } = req;

    // Remove host header to avoid conflicts
    const { host, ...forwardHeaders } = headers;

    // If the URL starts with /api, we need to forward it as is to the backend
    // The frontend will call /api/v1/login/json and we forward it to backend + /api/v1/login/json
    const targetUrl = url.startsWith('/api') ? url : `/api${url}`;
    const fullUrl = `${backendUrl}${targetUrl}`;

    console.log('Proxying request:', {
      method,
      originalUrl: url,
      targetUrl,
      fullUrl,
      headers: forwardHeaders,
      body: body ? 'present' : 'none'
    });

    // Make the request to the backend
    const response = await fetch(fullUrl, {
      method,
      headers: {
        ...forwardHeaders,
        'Content-Type': headers['content-type'] || 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      },
      body: method !== 'GET' && method !== 'HEAD' ? body : undefined,
      redirect: 'manual', // Don't follow redirects automatically
    });

    // Forward the response
    const responseText = await response.text();

    console.log('Backend response:', {
      status: response.status,
      statusText: response.statusText,
      headers: Object.fromEntries(response.headers.entries()),
      responseLength: responseText.length
    });

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