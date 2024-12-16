import axios from 'axios';

const BASE_URL = 'http://localhost:8001/api';

const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
    timeout: 30000,
    withCredentials: true,
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
    getDashboardStats: () => api.get('/dashboard/stats/'),
    getDashboardMatches: () => api.get('/dashboard/upcoming-matches/'),
    getDashboardScorers: () => api.get('/dashboard/top-scorers/'),

    // Matches
    getMatches: () => api.get('/matches/'),
    getMatchDetails: (id) => api.get(`/matches/${id}/`),

    // Teams
    getTeams: () => api.get('/teams/'),
    getTeamDetails: (id) => api.get(`/teams/${id}/`),

    // Players
    getPlayers: () => api.get('/players/'),
    getPlayerDetails: (id) => api.get(`/players/${id}/`),

    // Competitions
    getCompetitions: () => api.get('/competitions/'),
    getCompetitionDetails: (id) => api.get(`/competitions/${id}/`),

    // Predictions
    getMatchPredictions: (matchId) => api.get(`/match-predictions/?match_id=${matchId}`),

    // Analytics
    getCompetitionAnalytics: (competitionId) =>
        api.get(`/analytics/competition/${competitionId}/`),
    getTeamAnalytics: (teamId) => api.get(`/analytics/team/${teamId}/`),
    getPlayerAnalytics: (playerId) => api.get(`/analytics/player/${playerId}/`),

    // Top Scorers
    getTopScorers: () => api.get('/top-scorers/'),

    // Generic CRUD
    get: (endpoint) => api.get(endpoint),
    post: (endpoint, data) => api.post(endpoint, data),
    put: (endpoint, data) => api.put(endpoint, data),
    patch: (endpoint, data) => api.patch(endpoint, data),
    delete: (endpoint) => api.delete(endpoint),
};

export default apiService;
