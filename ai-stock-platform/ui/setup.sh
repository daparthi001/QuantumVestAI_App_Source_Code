#!/bin/bash

# Setup script for QuantumVestAI
echo "Setting up QuantumVestAI..."

# Create required directories
mkdir -p ai-stock-platform/ui/templates
mkdir -p ai-stock-platform/ui/static
mkdir -p ai-stock-platform/ui/static/css
mkdir -p ai-stock-platform/ui/static/js
mkdir -p ai-stock-platform/ui/static/img

# Create a basic CSS file
cat > ai-stock-platform/ui/static/css/main.css << EOF
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
}
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
}
header {
    background: #0066cc;
    color: white;
    padding: 1rem;
}
footer {
    background: #333;
    color: white;
    padding: 1rem;
    text-align: center;
}
EOF

# Create a basic JS file
cat > ai-stock-platform/ui/static/js/main.js << EOF
document.addEventListener('DOMContentLoaded', function() {
    console.log('QuantumVestAI initialized');
});
EOF

# Create a basic index template
mkdir -p ai-stock-platform/ui/templates
cat > ai-stock-platform/ui/templates/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>QuantumVestAI</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>QuantumVestAI</h1>
        </div>
    </header>
    <main class="container">
        <h2>Welcome to QuantumVestAI</h2>
        <p>Advanced AI-powered investment platform</p>
        <div>
            <a href="/login">Login</a> | <a href="/register">Register</a>
        </div>
    </main>
    <footer>
        <div class="container">
            <p>&copy; 2025 QuantumVestAI. All rights reserved.</p>
        </div>
    </footer>
    <script src="/static/js/main.js"></script>
</body>
</html>
EOF

echo "Setup complete. You can now start the application with: docker-compose up"