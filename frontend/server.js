const express = require('express');
const path = require('path');
const app = express();

const PORT = 5001;

app.use(express.static(path.join(__dirname, 'public')));

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log('='.repeat(60));
  console.log('TrustWise Premium Frontend v2');
  console.log('='.repeat(60));
  console.log(`Frontend running at http://localhost:${PORT}`);
  console.log('Backend API expected at http://localhost:5000');
  console.log('Press Ctrl+C to stop');
  console.log('='.repeat(60));
});
