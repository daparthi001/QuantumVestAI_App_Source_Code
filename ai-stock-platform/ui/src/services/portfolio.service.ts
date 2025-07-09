/**
 * Portfolio Service
 * Created: 2025-05-19 04:22:18
 * Author: daparthi001
 */
import { api } from './api';
import wsService, { WebSocketMessage } from './websocket.service';
import authService from './auth.service';
import { Position, Transaction, PortfolioSummary } from '../types/portfolio';
import { Subject } from 'rxjs';

export const portfolioService = {
    async getPositions() {
        return await api.get<Position[]>('/portfolio/positions');
    },

    async getPortfolioSummary() {
        return await api.get<PortfolioSummary>('/portfolio/summary');
    },

    async addTransaction(transaction: Transaction) {
        return await api.post('/portfolio/transactions', transaction);
    },

    async getTransactionHistory(symbol?: string) {
        const params = symbol ? { symbol } : {};
        return await api.get('/portfolio/transactions', { params });
    },

    subscribeToUpdates(callback: (update: any) => void) {
        const subject = new Subject();
        
        const token = authService.getToken();
        if (token) {
            wsService.connect(token);
            wsService.subscribe('PORTFOLIO_UPDATES');
        }
        
        wsService.onMessage().subscribe((message: WebSocketMessage) => {
            if (message.type === 'PORTFOLIO_UPDATE') {
                subject.next(message.data);
                callback(message.data);
            }
        });

        return subject;
    }
};
export default portfolioService;