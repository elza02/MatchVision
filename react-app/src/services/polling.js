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

                // Notify all subscribers
                const subscribers = this.subscribers.get(endpoint);
                if (subscribers) {
                    subscribers.forEach(callback => {
                        try {
                            callback(response.data);
                        } catch (error) {
                            console.error(`Error in subscriber callback for ${endpoint}:`, error);
                        }
                    });
                }
            } catch (error) {
                const currentRetries = this.retryCount.get(endpoint) || 0;
                this.retryCount.set(endpoint, currentRetries + 1);

                // Notify subscribers of the error
                const subscribers = this.subscribers.get(endpoint);
                if (subscribers) {
                    const errorInfo = {
                        message: error.response?.data?.message || error.message || 'An error occurred while fetching updates',
                        retryCount: currentRetries + 1,
                        maxRetries: this.MAX_RETRIES
                    };

                    subscribers.forEach(callback => {
                        try {
                            callback(null, errorInfo);
                        } catch (callbackError) {
                            console.error(`Error in error callback for ${endpoint}:`, callbackError);
                        }
                    });
                }

                // Stop polling if max retries reached
                if (currentRetries >= this.MAX_RETRIES) {
                    console.error(`Max retries (${this.MAX_RETRIES}) reached for ${endpoint}. Stopping polling.`);
                    this.stopPolling(endpoint);
                    return;
                }
            }
        };

        // Start the polling interval
        this.pollingIntervals.set(endpoint, setInterval(poll, interval));
        
        // Execute immediately
        poll();
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
        if (!data) return null;

        switch (endpoint) {
            case '/dashboard/stats/':
                return {
                    totalMatches: data.total_matches || 0,
                    totalTeams: data.total_teams || 0,
                    totalPlayers: data.total_scorers || 0,
                    upcomingMatches: data.recent_matches || [],
                    topScorers: data.top_scorers || []
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
