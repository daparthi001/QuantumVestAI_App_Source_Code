import { Subject } from 'rxjs';

export interface WebSocketMessage {
  type: string;
  data: any;
}

class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private readonly maxReconnectAttempts = 5;
  private readonly reconnectDelay = 3000;
  private eventCallbacks: Record<string, Set<(data: any) => void>> = {};
  private messageSubject = new Subject<WebSocketMessage>();
  private readonly baseUrl: string;

  constructor() {
    this.baseUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
    const token = localStorage.getItem('qvai_token') || '';
    if (token) {
      this.connect(token);
    }
  }

  private connect(token: string): void {
    if (this.socket) return;
    try {
      this.socket = new WebSocket(`${this.baseUrl}?token=${token}`);
      this.setupListeners();
    } catch (error) {
      console.error('WebSocket connection failed:', error);
      this.scheduleReconnect();
    }
  }

  private setupListeners(): void {
    if (!this.socket) return;
    this.socket.onopen = () => {
      this.reconnectAttempts = 0;
      Object.keys(this.eventCallbacks).forEach((evt) => {
        this.send('subscribe', { type: evt });
      });
    };

    this.socket.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        const cbs = this.eventCallbacks[message.type];
        cbs?.forEach((cb) => cb(message.data));
        this.messageSubject.next(message);
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };

    this.socket.onclose = () => {
      this.socket = null;
      this.scheduleReconnect();
    };

    this.socket.onerror = (err) => {
      console.error('WebSocket error:', err);
    };
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) return;
    this.reconnectAttempts += 1;
    setTimeout(() => {
      const token = localStorage.getItem('qvai_token') || '';
      if (token) {
        this.connect(token);
      }
    }, this.reconnectDelay);
  }

  private send(type: string, data: any): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ type, data }));
    }
  }

  subscribe(eventType: string, callback: (data: any) => void): void {
    if (!this.eventCallbacks[eventType]) {
      this.eventCallbacks[eventType] = new Set();
    }
    this.eventCallbacks[eventType].add(callback);
    this.send('subscribe', { type: eventType });
  }

  unsubscribe(eventType: string): void {
    this.eventCallbacks[eventType]?.clear();
    delete this.eventCallbacks[eventType];
    this.send('unsubscribe', { type: eventType });
  }

  subscribeSymbol(symbol: string): void {
    this.send('subscribe', { symbol });
  }

  unsubscribeSymbol(symbol: string): void {
    this.send('unsubscribe', { symbol });
  }

  onMessage(): Subject<WebSocketMessage> {
    return this.messageSubject;
  }
}

const wsService = new WebSocketService();export default wsService;
