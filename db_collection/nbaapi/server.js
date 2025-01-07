const express = require('express');
const app = express();
const path = require('path');
const PORT = process.env.PORT || 8080;
const fs = require("fs");


// Middleware to parse JSON bodies
app.use(express.json({ limit: '10mb' })); 

// Serve static files (e.g., CSS, JS, images) from the "public" directory
app.use(express.static(path.join(__dirname, 'public')));

// Route for the homepage (Random Photo Page)
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'index.html')); // Main homepage with random photo
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

