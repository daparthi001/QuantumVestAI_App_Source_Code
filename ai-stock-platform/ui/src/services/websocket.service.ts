/**
 * WebSocket Service for Real-time Data
 * Created: 2025-06-19 18:06:43
 * Author: daparthi001
 */
import io from 'socket.io-client';
import type { Socket } from 'socket.io-client';
import { BehaviorSubject } from 'rxjs';
import authService from './auth.service';

// WebSocket connection states
export enum ConnectionState {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error'
}

// WebSocket event types
export enum EventTypes {
  // Market data events
  PRICE_UPDATE = 'price_update',
  MARKET_STATUS = 'market_status',
  PRICE_ALERT = 'price_alert',
  VOLUME_SPIKE = 'volume_spike',
  
  // User-specific events
  WATCHLIST_UPDATE = 'watchlist_update',
  PORTFOLIO_UPDATE = 'portfolio_update',
  ALERT_TRIGGERED = 'alert_triggered',
  ORDER_STATUS = 'order_status',
  
  // System events
  SYSTEM_NOTIFICATION = 'system_notification',
  MAINTENANCE_ALERT = 'maintenance_alert',
  
  // Chat events
  CHAT_MESSAGE = 'chat_message',
  USER_TYPING = 'user_typing'
}

// Socket message interface
export interface SocketMessage {
  type: EventTypes;
  data: any;
  timestamp: string;
}

class WebSocketService {
  private socket: Socket | null = null;
  private connectionStateSubject = new BehaviorSubject<ConnectionState>(ConnectionState.DISCONNECTED);
  private messagesSubject = new BehaviorSubject<SocketMessage[]>([]);
  private subscribedSymbols = new Set<string>();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private baseReconnectDelay = 2000; // 2 seconds
  private reconnectTimer: NodeJS.Timeout | null = null;
  
  // Observable streams
  public connectionState$ = this.connectionStateSubject.asObservable();
  public messages$ = this.messagesSubject.asObservable();
  
  // Event-specific streams
  private eventStreams: Record<EventTypes, BehaviorSubject<any>> = {} as Record<EventTypes, BehaviorSubject<any>>;
  
  constructor() {
    // Initialize event streams
    Object.values(EventTypes).forEach(eventType => {
      this.eventStreams[eventType] = new BehaviorSubject<any>(null);
    });
    
    // Auto-connect if we have auth token
    if (authService.getToken()) {
      this.connect();
    }
    
    // Listen for auth changes
    authService.token.subscribe(token => {
      if (token) {
        this.connect();
      } else {
        this.disconnect();
      }
    });
  }
  
  /**
   * Connect to WebSocket
   */
  public connect(): void {
    if (this.socket) {
      return; // Already connected or connecting
    }
    
    const token = authService.getToken();
    if (!token) {
      console.error('Cannot connect to WebSocket: No auth token');
      return;
    }
    
    const wsUrl = process.env.REACT_APP_WEBSOCKET_URL || 'wss://dev.quantumvestai.com/ws';
    
    this.connectionStateSubject.next(ConnectionState.CONNECTING);
    
    this.socket = io(wsUrl, {
      transports: ['websocket'],
      auth: {
        token
      },
      reconnection: false, // We'll handle reconnection ourselves
      timeout: 10000 // 10 seconds connection timeout
    });
    
    // Set up event listeners
    this.setupSocketEventListeners();
  }
  
  /**
   * Disconnect from WebSocket
   */
  public disconnect(): void {
    if (!this.socket) {
      return;
    }
    
    this.socket.disconnect();
    this.socket = null;
    this.connectionStateSubject.next(ConnectionState.DISCONNECTED);
    this.clearReconnectTimer();
    this.reconnectAttempts = 0;
  }
  
  /**
   * Subscribe to real-time updates for a stock symbol
   * @param symbol Stock symbol
   */
  public subscribeToSymbol(symbol: string): void {
    if (!this.socket || this.connectionStateSubject.value !== ConnectionState.CONNECTED) {
      // Queue the subscription for when we're connected
      this.subscribedSymbols.add(symbol);
      this.connect();
      return;
    }
    
    if (!this.subscribedSymbols.has(symbol)) {
      this.subscribedSymbols.add(symbol);
      this.socket.emit('subscribe', { symbols: [symbol] });
    }
  }
  
  /**
   * Unsubscribe from real-time updates for a stock symbol
   * @param symbol Stock symbol
   */
  public unsubscribeFromSymbol(symbol: string): void {
    if (!this.socket || this.connectionStateSubject.value !== ConnectionState.CONNECTED) {
      this.subscribedSymbols.delete(symbol);
      return;
    }
    
    if (this.subscribedSymbols.has(symbol)) {
      this.subscribedSymbols.delete(symbol);
      this.socket.emit('unsubscribe', { symbols: [symbol] });
    }
  }
  
  /**
   * Get an observable for a specific event type
   * @param eventType WebSocket event type
   */
  public on<T>(eventType: EventTypes): BehaviorSubject<T> {
    return this.eventStreams[eventType] as BehaviorSubject<T>;
  }
  
  /**
   * Get current connection state
   */
  public getConnectionState(): ConnectionState {
    return this.connectionStateSubject.value;
  }
  
  /**
   * Send a message through the WebSocket
   * @param type Event type
   * @param data Data to send
   */
  public send(type: string, data: any): void {
    if (!this.socket || this.connectionStateSubject.value !== ConnectionState.CONNECTED) {
      console.error('Cannot send message: WebSocket not connected');
      return;
    }
    
    this.socket.emit(type, data);
  }
  
  // Setup WebSocket event listeners
  private setupSocketEventListeners(): void {
    if (!this.socket) {
      return;
    }
    
    // Connection events
    this.socket.on('connect', this.handleConnect.bind(this));
    this.socket.on('disconnect', this.handleDisconnect.bind(this));
    this.socket.on('connect_error', this.handleError.bind(this));
    
    // Message event
    this.socket.on('message', this.handleMessage.bind(this));
    
    // Set up listeners for all event types
    Object.values(EventTypes).forEach(eventType => {
      this.socket?.on(eventType, (data: any) => {
        this.eventStreams[eventType].next(data);
        
        // Also add to general messages stream
        const message: SocketMessage = {
          type: eventType,
          data,
          timestamp: new Date().toISOString()
        };
        
        const currentMessages = this.messagesSubject.value;
        this.messagesSubject.next([...currentMessages, message]);
      });
    });
  }
  
  // Handle successful connection
  private handleConnect(): void {
    console.log('WebSocket connected');
    this.connectionStateSubject.next(ConnectionState.CONNECTED);
    this.reconnectAttempts = 0;
    
    // Subscribe to all previously subscribed symbols
    if (this.subscribedSymbols.size > 0) {
      this.socket?.emit('subscribe', { symbols: Array.from(this.subscribedSymbols) });
    }
  }
  
  // Handle disconnection
  private handleDisconnect(): void {
    console.log('WebSocket disconnected');
    this.connectionStateSubject.next(ConnectionState.DISCONNECTED);
    this.socket = null;
    
    // Try to reconnect
    this.attemptReconnect();
  }
  
  // Handle connection error
  private handleError(error: Error): void {
    console.error('WebSocket error:', error);
    // You can implement reconnection or error reporting logic here
  }

  // Handle incoming messages
  private handleMessage(message: any): void {
    // Implement message handling if needed
  }

  // Attempt to reconnect
  private attemptReconnect(): void {
    // Implement reconnection logic if needed
  }

  // Clear the reconnect timer
  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
} // <-- THIS closes the class!

// Export the singleton instance
const wsService = new WebSocketService();
export default wsService;