import axios from 'axios';

// Base API configuration
const BASE_URL = 'http://192.168.1.8:8001/api';

const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});

// Add request interceptor for debugging
api.interceptors.request.use(
    (config) => {
        const fullUrl = `${config.baseURL}${config.url}`;
        console.log('Making API request:', {
            method: config.method,
            url: fullUrl,
            headers: config.headers,
            data: config.data
        });
        return config;
    },
    (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
    }
);

// Add response interceptor for debugging
api.interceptors.response.use(
    (response) => {
        console.log('API Response:', {
            url: response.config.url,
            status: response.status,
            data: response.data
        });
        return response;
    },
    (error) => {
        console.error('API Response Error:', {
            message: error.message,
            response: error.response ? {
                status: error.response.status,
                data: error.response.data
            } : 'No response'
        });
        return Promise.reject(error);
    }
);

const apiService = {
    // Dashboard
    getDashboardStats: async () => {
        try {
            const response = await api.get('/dashboard/stats/');
            return response.data;
        } catch (error) {
            console.error('Error fetching dashboard stats:', error);
            throw error;
        }
    },

    getUpcomingMatches: async () => {
        try {
            const response = await api.get('/dashboard/upcoming-matches/');
            return response.data;
        } catch (error) {
            console.error('Error fetching upcoming matches:', error);
            throw error;
        }
    },

    getTopScorers: async () => {
        try {
            const response = await api.get('/dashboard/top-scorers/');
            return response.data;
        } catch (error) {
            console.error('Error fetching top scorers:', error);
            throw error;
        }
    },

    // Matches
    getMatches: async (page = 1, filters = {}) => {
        try {
            console.log('Fetching matches with filters:', filters);
            let url = `/matches/?page=${page}`;
            
            // Add filters to URL
            if (filters.status) url += `&status=${filters.status}`;
            if (filters.competition) url += `&competition=${filters.competition}`;
            if (filters.team) url += `&team=${filters.team}`;
            if (filters.dateFrom) url += `&date_from=${filters.dateFrom}`;
            if (filters.dateTo) url += `&date_to=${filters.dateTo}`;

            const response = await api.get(url);
            
            // Validate response structure
            if (!response || !response.results) {
                throw new Error('Invalid matches response format');
            }

            // Format the matches data
            const formattedMatches = response.results.map(match => ({
                ...match,
                match_date: match.match_date || new Date().toISOString(),
                home_team_score: match.home_team_score || 0,
                away_team_score: match.away_team_score || 0,
                status: match.status || 'SCHEDULED'
            }));

            return {
                results: formattedMatches,
                count: response.count || 0,
                next: response.next || null,
                previous: response.previous || null
            };
        } catch (error) {
            console.error('Error in getMatches:', error);
            throw error;
        }
    },
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
            console.log('Fetching team analytics for ID:', teamId);
            // Use the same URL pattern that works with direct axios call
            const response = await api.get(`/analytics/team/${teamId}/`);
            console.log('Team analytics raw response:', response);

            // Extract data from response
            const data = response.data;
            console.log('Team analytics data:', data);

            if (!data) {
                throw new Error('No data received from server');
            }

            return data;
        } catch (error) {
            console.error('Error in getTeamAnalytics:', error);
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
    getCompetitions: async () => {
        try {
            const response = await api.get('/competitions/');
            // Return the data directly since it's already an array
            return response.data;
        } catch (error) {
            console.error('Error fetching competitions:', error);
            throw error;
        }
    },

    // Standings
    getStandings: async (competitionId, season) => {
        try {
            // Get standings for the specific competition and season
            const response = await api.get('/standings/', {
                params: {
                    competition: competitionId,
                    season: season
                }
            });
            
            // Return the standings array
            return { standings: response.data };
        } catch (error) {
            console.error('Error fetching standings:', error);
            throw error;
        }
    },
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
    get: async (url) => {
        try {
            console.log(`Making GET request to: ${url}`);
            const response = await api.get(url);
            console.log('GET response:', response);
            return response.data;
        } catch (error) {
            console.error(`GET request failed for ${url}:`, error);
            throw error;
        }
    },
    post: (endpoint, data) => api.post(endpoint, data),
    put: (endpoint, data) => api.put(endpoint, data),
    patch: (endpoint, data) => api.patch(endpoint, data),
    delete: (endpoint) => api.delete(endpoint),
};

export default apiService;
