require('dotenv').config();

const express = require('express');
const app = express();
const PORT = process.env.PORT || 8888;


app.use(express.json());
app.use(express.static('src'));


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
            return res.status(response.status).json({ error: 'Failed to get an OK response from SearxNG.' });
        }

        const jsonResponse = await response.json();
        res.json(jsonResponse);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Internal server error.' });
    }
});



app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});