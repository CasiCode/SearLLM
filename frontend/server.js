require('dotenv').config();

const path = require('path');
const express = require('express');
const app = express();
const PORT = process.env.PORT || 8888;


app.use(express.json());
app.use(express.static(path.join(__dirname, 'src')));


app.get('/s/:slug', (req, res) => {
  res.sendFile(path.resolve(__dirname, 'src', 'index.html'));
});


app.post('/api/proxy-query', async (req, res) => {
    const { session_id, user_id, message } = req.body;

    try {
        const response = await fetch('http://backend:8000/queries/query', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "SearLLM-API-token": process.env.SEARLLM_API_TOKEN
            },
            body: JSON.stringify({ session_id, user_id, message })
        });

        if (!response.ok) {
            return res.status(response.status).json({ error: 'Failed to get an OK response from SearLLM.' });
        }

        const jsonResponse = await response.json();
        res.json(jsonResponse);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Internal server error.' });
    }
});


app.post('/api/proxy-share', async (req, res) => {
    const { query, highlight, text, source_documents } = req.body;

    try {
        const response = await fetch('http://backend:8000/shares/create', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "SearLLM-API-token": process.env.SEARLLM_API_TOKEN
            },
            body: JSON.stringify({ query, highlight, text, source_documents })
        });

        if (!response.ok) {
            return ""
        }

        const jsonResponse = await response.json();
        res.json(jsonResponse);
    } catch (error) {
        console.log("60")
        console.error(error);
        res.status(500).json({ error: 'Internal server error.' });
    }
});


app.post('/api/proxy-share-data', async (req, res) => {
    const { slug } = req.body || {};
    if (!slug || typeof slug !== 'string') {
        return res.status(400).json({ error: 'Missing or invalid slug' });
    }

    const upstreamUrl = `http://backend:8000/shares/s/${encodeURIComponent(slug)}`;
    try {
        const upstream = await fetch(upstreamUrl, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
            ...(process.env.SEARLLM_API_TOKEN
            ? { 'SearLLM-API-token': process.env.SEARLLM_API_TOKEN }
            : {})
        }
        });

        const ct = upstream.headers.get('content-type') || '';
        const raw = await upstream.text();

        if (!upstream.ok) {
        return res.status(upstream.status).type(ct || 'text/plain').send(raw);
        }

        if (ct.includes('application/json')) {
        try {
            return res.json(JSON.parse(raw));
        } catch {
            // fallthrough
        }
        }

        return res.status(502).json({ error: 'Upstream did not return JSON', body: raw });
    } catch (err) {
        console.error('proxy-share-data error:', err);
        return res.status(502).json({ error: 'Bad gateway' });
    }
    });


app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});