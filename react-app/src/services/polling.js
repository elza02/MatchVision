import apiService from './api';

class PollingService {
    constructor() {
        this.pollingIntervals = new Map();
        this.subscribers = new Map();
        this.DEFAULT_INTERVAL = 5000; // 5 seconds
        this.retryCount = new Map();
        this.MAX_RETRIES = 3;
    }

    // Subscribe to updates for a specific endpoint
    subscribe(endpoint, callback, interval = this.DEFAULT_INTERVAL) {
        if (!this.subscribers.has(endpoint)) {
            this.subscribers.set(endpoint, new Set());
            this.retryCount.set(endpoint, 0);
        }
        this.subscribers.get(endpoint).add(callback);

        // Start polling if it's not already started for this endpoint
        if (!this.pollingIntervals.has(endpoint)) {
            this.startPolling(endpoint, interval);
        }

        // Return unsubscribe function
        return () => this.unsubscribe(endpoint, callback);
    }

    // Unsubscribe from updates
    unsubscribe(endpoint, callback) {
        const subscribers = this.subscribers.get(endpoint);
        if (subscribers) {
            subscribers.delete(callback);
            if (subscribers.size === 0) {
                this.stopPolling(endpoint);
                this.subscribers.delete(endpoint);
                this.retryCount.delete(endpoint);
            }
        }
    }

    // Start polling for an endpoint
    startPolling(endpoint, interval) {
        const poll = async () => {
            try {
                const response = await apiService.get(endpoint);
                this.retryCount.set(endpoint, 0); // Reset retry count on success

                // Transform response data based on endpoint
                const transformedData = this.transformResponseData(endpoint, response.data);
                
                const subscribers = this.subscribers.get(endpoint);
                if (subscribers) {
                    subscribers.forEach(callback => callback(transformedData, null));
                }
            } catch (error) {
                const retryCount = (this.retryCount.get(endpoint) || 0) + 1;
                this.retryCount.set(endpoint, retryCount);

                const errorMessage = this.getErrorMessage(error);
                
                const subscribers = this.subscribers.get(endpoint);
                if (subscribers) {
                    subscribers.forEach(callback => callback(null, { 
                        message: errorMessage,
                        retryCount,
                        maxRetries: this.MAX_RETRIES
                    }));
                }

                // Stop polling if max retries reached
                if (retryCount >= this.MAX_RETRIES) {
                    this.stopPolling(endpoint);
                    console.error(`Max retries (${this.MAX_RETRIES}) reached for endpoint: ${endpoint}`);
                    return;
                }
            }
        };

        // Execute immediately and then start interval
        poll();
        const intervalId = setInterval(poll, interval);
        this.pollingIntervals.set(endpoint, intervalId);
    }

    // Stop polling for an endpoint
    stopPolling(endpoint) {
        const intervalId = this.pollingIntervals.get(endpoint);
        if (intervalId) {
            clearInterval(intervalId);
            this.pollingIntervals.delete(endpoint);
        }
    }

    // Transform response data based on endpoint
    transformResponseData(endpoint, data) {
        switch (endpoint) {
            case '/dashboard/stats/':
                return {
                    totalMatches: data.totalMatches || 0,
                    totalTeams: data.totalTeams || 0,
                    totalPlayers: data.totalPlayers || 0
                };
            case '/dashboard/upcoming-matches/':
                return {
                    upcomingMatches: data.upcomingMatches?.map(match => ({
                        id: match.id,
                        homeTeam: match.homeTeam,
                        awayTeam: match.awayTeam,
                        date: new Date(match.date),
                        competition: match.competition
                    })) || []
                };
            case '/dashboard/top-scorers/':
                return {
                    topScorers: data.topScorers?.map(scorer => ({
                        playerId: scorer.playerId,
                        playerName: scorer.playerName,
                        team: scorer.team,
                        goals: scorer.goals
                    })) || []
                };
            default:
                return data;
        }
    }

    // Get user-friendly error message
    getErrorMessage(error) {
        if (error.response) {
            // Server responded with error status
            switch (error.response.status) {
                case 404:
                    return 'Resource not found';
                case 401:
                    return 'Unauthorized access';
                case 403:
                    return 'Access forbidden';
                case 500:
                    return 'Internal server error';
                default:
                    return error.response.data?.message || 'Server error occurred';
            }
        } else if (error.request) {
            return 'No response from server';
        } else {
            return error.message || 'An unexpected error occurred';
        }
    }
}

export const pollingService = new PollingService();
export default pollingService;
