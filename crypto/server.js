const express = require('express');
const axios = require('axios');

const app = express();

// Route to fetch data from the Flask API
app.get('/fetch-data', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:5000/api/data'); // Call Flask API
        res.json(response.data); // Send Flask data to the client
    } catch (error) {
        console.error(error);
        res.status(500).send('Error communicating with Flask server');
    }
});

app.listen(3000, () => {
    console.log('Node.js server running on http://localhost:3000');
});

