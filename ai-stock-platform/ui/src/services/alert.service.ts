/**
 * Alert Service
 * Created: 2025-05-19 04:17:48
 * Author: daparthi001
 */
import { api } from './api';
import { AlertConfig } from '../types/alerts';

export const alertService = {
    async getAlerts() {
        return await api.get('/alerts');
    },

    async createAlert(alert: AlertConfig) {
        return await api.post('/alerts', alert);
    },

    async updateAlert(alertId: string, update: Partial<AlertConfig>) {
        return await api.patch(`/alerts/${alertId}`, update);
    },

    async deleteAlert(alertId: string) {
        return await api.delete(`/alerts/${alertId}`);
    },

    async getAlertHistory(alertId: string) {
        return await api.get(`/alerts/${alertId}/history`);
    }
};