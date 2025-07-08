/**
 * AI Assistant Component
 * Chat interface for AI-powered market analysis and recommendations
 */
import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Card, Form, Button, Spinner, Alert, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { ROUTES } from '../config/constants';

interface ChatMessage {
  id: number;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const AiAssistant: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Add welcome message
    const welcomeMessage: ChatMessage = {
      id: 1,
      type: 'assistant',
      content: 'Hello! I\'m your AI investment assistant. I can help you with stock analysis, portfolio recommendations, market insights, and investment strategies. What would you like to know?',
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  }, []);

  useEffect(() => {
    // Scroll to bottom when new messages are added
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = {
      id: messages.length + 1,
      type: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      // Simulate AI response for now
      // In real implementation, this would call the API: await apiService.chatWithAI(input);
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
      
      const aiResponse = generateMockAIResponse(input.trim());
      
      const assistantMessage: ChatMessage = {
        id: messages.length + 2,
        type: 'assistant',
        content: aiResponse,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to get AI response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const generateMockAIResponse = (userInput: string): string => {
    const lowerInput = userInput.toLowerCase();
    
    if (lowerInput.includes('stock') || lowerInput.includes('price')) {
      return 'I can help you analyze specific stocks! Please provide a stock symbol (like AAPL, MSFT, or TSLA) and I\'ll give you insights on its current performance, technical indicators, and potential price movements. You can also ask about sector analysis or market trends.';
    } else if (lowerInput.includes('portfolio')) {
      return 'For portfolio optimization, I recommend diversifying across different sectors and market caps. Based on current market conditions, consider allocating 60% to large-cap stocks, 25% to mid-cap, 10% to small-cap, and 5% to international exposure. Would you like me to analyze your current holdings?';
    } else if (lowerInput.includes('buy') || lowerInput.includes('sell')) {
      return 'Investment decisions should be based on thorough analysis. I can help you evaluate stocks using fundamental analysis (P/E ratios, earnings growth, debt levels) and technical analysis (moving averages, RSI, MACD). What specific stock are you considering?';
    } else if (lowerInput.includes('market') || lowerInput.includes('trend')) {
      return 'Current market trends show mixed signals. The tech sector has been experiencing volatility, while defensive sectors like utilities and consumer staples are showing stability. Consider using our Analytics section for detailed market overview and sector performance.';
    } else if (lowerInput.includes('risk')) {
      return 'Risk management is crucial for long-term success. I recommend setting stop-losses at 7-10% below your entry price, diversifying across uncorrelated assets, and never investing more than 5% of your portfolio in a single stock. Would you like me to analyze your portfolio\'s risk profile?';
    } else {
      return 'I\'m here to help with your investment questions! I can assist with:\n\n• Stock analysis and recommendations\n• Portfolio optimization strategies\n• Market trend analysis\n• Risk management advice\n• Technical and fundamental analysis\n• Sector rotation strategies\n\nWhat specific topic would you like to explore?';
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickQuestions = [
    "Analyze AAPL stock",
    "What are the best sectors to invest in?",
    "How should I diversify my portfolio?",
    "What's the current market outlook?",
    "Explain P/E ratio and its importance"
  ];

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>AI Investment Assistant</h1>
        <div>
          <Button as={Link as any} to={ROUTES.ANALYTICS} variant="outline-primary" className="me-2">
            View Analytics
          </Button>
          <Button as={Link as any} to={ROUTES.STOCKS} variant="primary">
            Browse Stocks
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
          <Button variant="link" onClick={() => setError(null)}>
            Dismiss
          </Button>
        </Alert>
      )}

      <Row>
        {/* Chat Interface */}
        <Col lg={8} className="mb-4">
          <Card style={{ height: '600px' }}>
            <Card.Header>
              <h5 className="mb-0">
                💬 Chat with AI Assistant 
                <Badge bg="success" className="ms-2">Online</Badge>
              </h5>
            </Card.Header>
            <Card.Body style={{ overflow: 'auto', padding: '1rem' }}>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`mb-3 d-flex ${message.type === 'user' ? 'justify-content-end' : 'justify-content-start'}`}
                >
                  <div
                    className={`p-3 rounded ${
                      message.type === 'user' 
                        ? 'bg-primary text-white' 
                        : 'bg-light border'
                    }`}
                    style={{ maxWidth: '80%' }}
                  >
                    <div className="mb-1" style={{ whiteSpace: 'pre-wrap' }}>
                      {message.content}
                    </div>
                    <small className={message.type === 'user' ? 'text-light' : 'text-muted'}>
                      {message.timestamp.toLocaleTimeString()}
                    </small>
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="d-flex justify-content-start mb-3">
                  <div className="bg-light border p-3 rounded">
                    <Spinner animation="border" size="sm" className="me-2" />
                    AI is thinking...
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </Card.Body>
            <Card.Footer>
              <Form.Group className="d-flex">
                <Form.Control
                  as="textarea"
                  rows={2}
                  placeholder="Type your investment question here..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={loading}
                />
                <Button
                  variant="primary"
                  onClick={handleSendMessage}
                  disabled={loading || !input.trim()}
                  className="ms-2"
                >
                  Send
                </Button>
              </Form.Group>
            </Card.Footer>
          </Card>
        </Col>

        {/* Quick Actions and Tips */}
        <Col lg={4}>
          {/* Quick Questions */}
          <Card className="mb-4">
            <Card.Header>
              <h6 className="mb-0">Quick Questions</h6>
            </Card.Header>
            <Card.Body>
              {quickQuestions.map((question, index) => (
                <Button
                  key={index}
                  variant="outline-secondary"
                  size="sm"
                  className="w-100 mb-2 text-start"
                  onClick={() => setInput(question)}
                  disabled={loading}
                >
                  {question}
                </Button>
              ))}
            </Card.Body>
          </Card>

          {/* AI Capabilities */}
          <Card className="mb-4">
            <Card.Header>
              <h6 className="mb-0">AI Capabilities</h6>
            </Card.Header>
            <Card.Body>
              <ul className="list-unstyled">
                <li className="mb-2">🔍 <strong>Stock Analysis</strong><br />
                  <small className="text-muted">Fundamental and technical analysis</small>
                </li>
                <li className="mb-2">📊 <strong>Portfolio Optimization</strong><br />
                  <small className="text-muted">Risk-adjusted recommendations</small>
                </li>
                <li className="mb-2">📈 <strong>Market Insights</strong><br />
                  <small className="text-muted">Trend analysis and predictions</small>
                </li>
                <li className="mb-2">⚠️ <strong>Risk Assessment</strong><br />
                  <small className="text-muted">Portfolio risk evaluation</small>
                </li>
                <li className="mb-2">💡 <strong>Investment Strategies</strong><br />
                  <small className="text-muted">Personalized recommendations</small>
                </li>
              </ul>
            </Card.Body>
          </Card>

          {/* Quick Actions */}
          <Card>
            <Card.Header>
              <h6 className="mb-0">Quick Actions</h6>
            </Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                <Button as={Link as any} to={ROUTES.ANALYTICS} variant="outline-primary" size="sm">
                  📊 View Market Analytics
                </Button>
                <Button as={Link as any} to={ROUTES.PORTFOLIO} variant="outline-success" size="sm">
                  💼 Analyze My Portfolio
                </Button>
                <Button as={Link as any} to={ROUTES.BACKTEST} variant="outline-info" size="sm">
                  🔄 Run Strategy Backtest
                </Button>
                <Button as={Link as any} to={ROUTES.ALERTS} variant="outline-warning" size="sm">
                  🔔 Set Price Alerts
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default AiAssistant;
