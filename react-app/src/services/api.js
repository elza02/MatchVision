import axios from 'axios';

const BASE_URL = 'http://localhost:8001/api';

const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
    timeout: 30000,
    withCredentials: false,  // Changed to false since we're using CORS_ALLOW_ALL_ORIGINS
});

// Request Interceptor
api.interceptors.request.use(
    (config) => {
        console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
        return config;
    },
    (error) => {
        console.error('API Request Error:', error);
        return Promise.reject({
            message: 'Failed to connect to server. Please check your connection.',
            originalError: error,
        });
    }
);

// Response Interceptor
api.interceptors.response.use(
    (response) => {
        console.log(`API Response from ${response.config.url}:`, response.status);
        return response;
    },
    (error) => {
        console.error('API Response Error:', error);
        if (!error.response) {
            return Promise.reject({
                message: 'Unable to reach server. Please check your connection.',
                status: 'NETWORK_ERROR',
                originalError: error,
            });
        }
        const message =
            error.response.data?.message ||
            error.response.data?.detail ||
            error.response.data?.error ||
            'An unexpected error occurred. Please try again.';
        return Promise.reject({
            message,
            status: error.response.status,
            originalError: error,
        });
    }
);

const apiService = {
    // Dashboard
    getDashboardStats: () => api.get('dashboard/stats/'),
    getDashboardMatches: () => api.get('dashboard/upcoming-matches/'),
    getDashboardScorers: () => api.get('dashboard/top-scorers/'),

    // Matches
    getMatches: () => api.get('matches/'),
    getMatchDetails: (id) => api.get(`matches/${id}/`),
    getMatchAnalytics: (id) => api.get(`analytics/match/${id}/`),

    // Teams
    getTeams: async (params = {}) => {
        try {
            const response = await api.get('teams', { params });
            return response;
        } catch (error) {
            console.error('Error fetching teams:', error);
            throw error;
        }
    },
    getTeamDetails: async (id) => {
        try {
            const response = await api.get(`teams/${id}`);
            return response;
        } catch (error) {
            console.error('Error fetching team details:', error);
            throw error;
        }
    },
    getTeamAnalytics: async (teamId) => {
        try {
            console.log('Making API request for team analytics:', teamId);
            const url = `analytics/team/${teamId}/`;  // Added trailing slash
            console.log('Full API URL:', `${BASE_URL}/${url}`);
            
            const response = await api.get(url);
            console.log('Raw API response:', response);
            console.log('Response status:', response?.status);
            console.log('Response data:', response?.data);
            
            // Check if response has the expected structure
            if (!response || !response.data) {
                console.error('Invalid response:', response);
                throw new Error('No response data received from server');
            }

            // Log the actual response structure
            console.log('Response data structure:', {
                hasData: !!response.data,
                hasSummary: !!response.data.summary,
                hasPerformance: Array.isArray(response.data.performance),
                summaryKeys: response.data.summary ? Object.keys(response.data.summary) : [],
                performanceLength: Array.isArray(response.data.performance) ? response.data.performance.length : 0
            });

            // Validate summary object
            const summary = response.data.summary;
            if (!summary || typeof summary !== 'object') {
                throw new Error('Invalid summary data in response');
            }

            // Validate required summary fields
            const requiredSummaryFields = [
                'total_matches', 'wins', 'draws', 'losses',
                'goals_for', 'goals_against', 'goal_difference',
                'points', 'average_points'
            ];
            
            const missingSummaryFields = requiredSummaryFields.filter(field => !(field in summary));
            if (missingSummaryFields.length > 0) {
                throw new Error(`Missing required summary fields: ${missingSummaryFields.join(', ')}`);
            }

            // Validate performance array
            const performance = response.data.performance;
            if (!Array.isArray(performance)) {
                throw new Error('Performance data must be an array');
            }

            // If all validations pass, return the response
            return response;
        } catch (error) {
            console.error('Error fetching team analytics:', error);
            if (error.response) {
                console.error('Error response:', {
                    status: error.response.status,
                    statusText: error.response.statusText,
                    data: error.response.data
                });
            }
            throw error;
        }
    },
    getTeamComparison: (team1Id, team2Id) => 
        api.get(`analytics/team-comparison/${team1Id}/${team2Id}/`),

    // Players
    getPlayers: () => api.get('players/'),
    getPlayerDetails: (id) => api.get(`/players/${id}/`),
    getPlayerAnalytics: (id) => api.get(`/analytics/player/${id}/`),

    // Competitions
    getCompetitions: () => api.get('competitions/'),
    getCompetitionDetails: (id) => api.get(`/competitions/${id}/`),
    getCompetitionAnalytics: (id) => api.get(`/analytics/competition/${id}/`),

    // Analytics
    getAnalyticsOverview: async () => {
        try {
            const response = await api.get('analytics/overview/');
            console.log('Analytics Overview Response:', response.data);
            return response.data;
        } catch (error) {
            console.error('Error fetching analytics overview:', error);
            throw error;
        }
    },
    getTeamAnalytics: async (teamId) => {
        try {
            const response = await api.get(`/analytics/team/${teamId}/`);
            console.log('Team Analytics Response:', response.data);
            return response.data;
        } catch (error) {
            console.error('Error fetching team analytics:', error);
            throw error;
        }
    },

    // Generic CRUD
    get: async (endpoint) => {
        try {
            const response = await api.get(endpoint);
            console.log('API Response from ' + endpoint + ':', response.status);
            return response.data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    post: (endpoint, data) => api.post(endpoint, data),
    put: (endpoint, data) => api.put(endpoint, data),
    patch: (endpoint, data) => api.patch(endpoint, data),
    delete: (endpoint) => api.delete(endpoint),
};

export default apiService;
