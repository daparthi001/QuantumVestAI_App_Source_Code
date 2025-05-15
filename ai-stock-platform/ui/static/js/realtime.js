# ui/static/js/realtime.js
class RealtimeService {
    constructor(token) {
        this.token = token;
        this.socket = null;
        this.listeners = {};
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }
    
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws?token=${this.token}`;
        
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
            console.log('WebSocket connection established');
            this.reconnectAttempts = 0;
        };
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type && this.listeners[data.type]) {
                this.listeners[data.type].forEach(callback => callback(data.payload));
            }
        };
        
        this.socket.onclose = (event) => {
            console.log('WebSocket connection closed', event.code);
            
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                setTimeout(() => this.connect(), 1000 * Math.pow(2, this.reconnectAttempts));
            }
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error', error);
        };
    }
    
    subscribe(eventType, callback) {
        if (!this.listeners[eventType]) {
            this.listeners[eventType] = [];
            
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({
                    action: 'subscribe',
                    eventType: eventType
                }));
            }
        }
        
        this.listeners[eventType].push(callback);
    }
    
    unsubscribe(eventType, callback) {
        if (this.listeners[eventType]) {
            this.listeners[eventType] = this.listeners[eventType]
                .filter(cb => cb !== callback);
                
            if (this.listeners[eventType].length === 0) {
                delete this.listeners[eventType];
                
                if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                    this.socket.send(JSON.stringify({
                        action: 'unsubscribe',
                        eventType: eventType
                    }));
                }
            }
        }
    }
    
    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }
}