import axios from 'axios';

const BASE_URL = 'http://localhost:8001/api';

const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
    timeout: 30000, // Increased to 30 seconds
    withCredentials: true,
});

// Add request interceptor for logging and error handling
api.interceptors.request.use(
    (config) => {
        // Log request details
        console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
        return config;
    },
    (error) => {
        console.error('API Request Error:', error);
        return Promise.reject({
            message: 'Failed to connect to server. Please check your connection.',
            originalError: error
        });
    }
);

// Add response interceptor for error handling
api.interceptors.response.use(
    (response) => {
        // Log successful response
        console.log(`API Response from ${response.config.url}:`, response.status);
        return response;
    },
    (error) => {
        console.error('API Response Error:', error);
        
        if (!error.response) {
            // Network error or server not responding
            return Promise.reject({
                message: 'Unable to reach server. Please check your connection and try again.',
                status: 'NETWORK_ERROR',
                originalError: error
            });
        }
        
        // Handle different types of errors
        if (error.response) {
            const message = error.response.data?.message || 
                          error.response.data?.detail ||
                          'An unexpected error occurred. Please try again.';
            return Promise.reject({
                message,
                status: error.response.status,
                originalError: error
            });
        }
        
        return Promise.reject(error);
    }
);

const apiService = {
    // Dashboard endpoints
    getDashboardStats: () => api.get('/dashboard/stats/'),
    getDashboardMatches: () => api.get('/dashboard/upcoming-matches/'),
    getDashboardScorers: () => api.get('/dashboard/top-scorers/'),

    // Matches endpoints
    getMatches: () => api.get('/matches/'),
    getMatchDetails: (id) => api.get(`/matches/${id}/`),
    getMatchStats: (id) => api.get(`/matches/${id}/stats/`),
    
    // Teams endpoints
    getTeams: () => api.get('/teams/'),
    getTeamDetails: (id) => api.get(`/teams/${id}/`),
    getTeamStats: (id) => api.get(`/teams/${id}/stats/`),
    
    // Players endpoints
    getPlayers: () => api.get('/players/'),
    getPlayerDetails: (id) => api.get(`/players/${id}/`),
    getPlayerStats: (id) => api.get(`/players/${id}/stats/`),
    
    // Competitions endpoints
    getCompetitions: () => api.get('/competitions/'),
    getCompetitionDetails: (id) => api.get(`/competitions/${id}/`),
    
    // Predictions endpoints
    getMatchPredictions: (matchId) => api.get(`/predictions/match/${matchId}/`),
    
    // Generic CRUD operations
    get: (endpoint) => api.get(endpoint),
    post: (endpoint, data) => api.post(endpoint, data),
    put: (endpoint, data) => api.put(endpoint, data),
    patch: (endpoint, data) => api.patch(endpoint, data),
    delete: (endpoint) => api.delete(endpoint),
};

export default apiService;
