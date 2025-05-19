/**
 * QuantumVestAI Realtime Service
 * Created: 2025-05-19 03:38:30
 * Author: daparthi001
 */
class RealtimeService {
    constructor(token, options = {}) {
        this.token = token;
        this.socket = null;
        this.listeners = {};
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = options.maxReconnectAttempts || 5;
        this.reconnectDelay = options.reconnectDelay || 1000;
        this.debug = options.debug || false;
    }
    
    connect() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws?token=${encodeURIComponent(this.token)}`;
            
            this.socket = new WebSocket(wsUrl);
            
            this.socket.onopen = this._handleOpen.bind(this);
            this.socket.onmessage = this._handleMessage.bind(this);
            this.socket.onclose = this._handleClose.bind(this);
            this.socket.onerror = this._handleError.bind(this);
        } catch (error) {
            this._log('Error connecting to WebSocket:', error);
            this._attemptReconnect();
        }
    }
    
    _handleOpen() {
        this._log('WebSocket connection established');
        this.reconnectAttempts = 0;
        
        // Resubscribe to existing topics
        Object.keys(this.listeners).forEach(eventType => {
            this._sendSubscription(eventType, 'subscribe');
        });
    }
    
    _handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            if (data.type && this.listeners[data.type]) {
                this.listeners[data.type].forEach(callback => {
                    try {
                        callback(data.payload);
                    } catch (error) {
                        this._log('Error in listener callback:', error);
                    }
                });
            }
        } catch (error) {
            this._log('Error handling message:', error);
        }
    }
    
    _handleClose(event) {
        this._log('WebSocket connection closed', event.code);
        this._attemptReconnect();
    }
    
    _handleError(error) {
        this._log('WebSocket error:', error);
    }
    
    _attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
            setTimeout(() => this.connect(), delay);
        }
    }
    
    _sendSubscription(eventType, action) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                action,
                eventType,
                timestamp: new Date().toISOString()
            }));
        }
    }
    
    subscribe(eventType, callback) {
        if (!this.listeners[eventType]) {
            this.listeners[eventType] = [];
            this._sendSubscription(eventType, 'subscribe');
        }
        
        if (!this.listeners[eventType].includes(callback)) {
            this.listeners[eventType].push(callback);
        }
    }
    
    unsubscribe(eventType, callback) {
        if (this.listeners[eventType]) {
            this.listeners[eventType] = this.listeners[eventType]
                .filter(cb => cb !== callback);
                
            if (this.listeners[eventType].length === 0) {
                delete this.listeners[eventType];
                this._sendSubscription(eventType, 'unsubscribe');
            }
        }
    }
    
    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
        this.listeners = {};
        this.reconnectAttempts = 0;
    }
    
    _log(...args) {
        if (this.debug) {
            console.log('[RealtimeService]', ...args);
        }
    }
}

// Export for both ES modules and CommonJS
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RealtimeService;
} else {
    window.RealtimeService = RealtimeService;
}