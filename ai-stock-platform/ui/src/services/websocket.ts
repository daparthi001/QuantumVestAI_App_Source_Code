/**
 * WebSocket Service
 * Created: 2025-05-19 04:08:26
 * Author: daparthi001
 */
import { Subject } from 'rxjs';

interface WebSocketMessage {
    type: string;
    data: any;
}

class WebSocketService {
    private socket: WebSocket | null = null;
    private messageSubject = new Subject<WebSocketMessage>();
    private reconnectAttempts = 0;
    private readonly maxReconnectAttempts = 5;
    private readonly reconnectDelay = 3000;

    constructor(private baseUrl: string) {}

    public connect(token: string): void {
        try {
            this.socket = new WebSocket(`${this.baseUrl}?token=${token}`);
            this.setupSocketListeners();
        } catch (error) {
            console.error('WebSocket connection failed:', error);
            this.handleReconnection();
        }
    }

    private setupSocketListeners(): void {
        if (!this.socket) return;

        this.socket.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
        };

        this.socket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.messageSubject.next(message);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        this.socket.onclose = () => {
            console.log('WebSocket disconnected');
            this.handleReconnection();
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    private handleReconnection(): void {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
                console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                this.connect(localStorage.getItem('token') || '');
            }, this.reconnectDelay);
        } else {
            console.error('Max reconnection attempts reached');
            this.messageSubject.error(new Error('WebSocket connection failed'));
        }
    }

    public subscribe(symbol: string): void {
        if (this.socket?.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'subscribe',
                symbol: symbol
            }));
        }
    }

    public unsubscribe(symbol: string): void {
        if (this.socket?.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'unsubscribe',
                symbol: symbol
            }));
        }
    }

    public onMessage(): Subject<WebSocketMessage> {
        return this.messageSubject;
    }

    public disconnect(): void {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }
}

export const wsService = new WebSocketService(
    process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws'
);