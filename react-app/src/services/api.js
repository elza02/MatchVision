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
    async getTeams(params = {}) {
        try {
            const queryString = Object.entries(params)
                .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
                .join('&');
            const endpoint = `teams/${queryString ? `?${queryString}` : ''}`;
            const response = await api.get(endpoint);
            return response;
        } catch (error) {
            console.error('Error fetching teams:', error);
            throw error;
        }
    },
    getTeamDetails: (id) => api.get(`teams/${id}/`),
    getTeamAnalytics: (id) => api.get(`analytics/team/${id}/`),
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
