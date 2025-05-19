/**
 * Alert Types
 * Created: 2025-05-19 04:17:48
 * Author: daparthi001
 */

export enum AlertType {
    PRICE = 'PRICE',
    VOLUME = 'VOLUME',
    TECHNICAL = 'TECHNICAL',
    SENTIMENT = 'SENTIMENT',
    NEWS = 'NEWS'
}

export enum AlertCondition {
    ABOVE = 'ABOVE',
    BELOW = 'BELOW',
    CROSSES_ABOVE = 'CROSSES_ABOVE',
    CROSSES_BELOW = 'CROSSES_BELOW',
    PERCENTAGE_CHANGE = 'PERCENTAGE_CHANGE'
}

export enum AlertSeverity {
    LOW = 'LOW',
    MEDIUM = 'MEDIUM',
    HIGH = 'HIGH'
}

export interface AlertConfig {
    id?: string;
    symbol: string;
    type: AlertType;
    condition: AlertCondition;
    threshold: number;
    severity: AlertSeverity;
    active: boolean;
    createdAt?: string;
    updatedAt?: string;
}

export interface AlertHistory {
    id: string;
    alertId: string;
    triggeredAt: string;
    value: number;
    message: string;
}