import { useEffect, useState } from 'react';
import {
  Box,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Heading,
  Card,
  CardHeader,
  CardBody,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Alert,
  AlertIcon,
  Spinner,
  Center,
  useToast,
  Text,
  Image,
  HStack,
  Tooltip
} from '@chakra-ui/react';
import apiService from '../services/api';
import { pollingService } from '../services/polling';

function Dashboard() {
  const [stats, setStats] = useState({
    totalMatches: 0,
    totalTeams: 0,
    totalPlayers: 0,
    upcomingMatches: [],
    topScorers: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const toast = useToast();

  useEffect(() => {
    // Initial data fetch
    fetchDashboardData();

    // Set up polling for real-time updates
    const unsubscribeStats = pollingService.subscribe('/dashboard/stats/', handleStatsUpdate, 10000);
    const unsubscribeMatches = pollingService.subscribe('/dashboard/matches/', handleMatchesUpdate, 30000);
    const unsubscribeScorers = pollingService.subscribe('/dashboard/scorers/', handleScorersUpdate, 30000);

    // Cleanup function
    return () => {
      unsubscribeStats();
      unsubscribeMatches();
      unsubscribeScorers();
    };
  }, []);

  const handleStatsUpdate = (data) => {
    if (!data) return;
    
    setStats(prevStats => ({
      ...prevStats,
      totalMatches: data.total_matches || 0,
      totalTeams: data.total_teams || 0,
      totalPlayers: data.total_players || 0
    }));
  };

  const handleMatchesUpdate = (data) => {
    if (!Array.isArray(data)) return;
    
    setStats(prevStats => ({
      ...prevStats,
      upcomingMatches: data
    }));
  };

  const handleScorersUpdate = (data) => {
    if (!Array.isArray(data)) return;
    
    setStats(prevStats => ({
      ...prevStats,
      topScorers: data
    }));
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all data in parallel
      const [statsRes, matchesRes, scorersRes] = await Promise.all([
        apiService.getDashboardStats(),
        apiService.getDashboardMatches(),
        apiService.getDashboardScorers()
      ]);

      // Update state with all data
      setStats({
        totalMatches: statsRes.data.total_matches || 0,
        totalTeams: statsRes.data.total_teams || 0,
        totalPlayers: statsRes.data.total_players || 0,
        upcomingMatches: Array.isArray(matchesRes.data) ? matchesRes.data : [],
        topScorers: Array.isArray(scorersRes.data) ? scorersRes.data : []
      });

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError({
        message: error.message || 'Failed to fetch dashboard data',
        status: error.status
      });
      toast({
        title: 'Error',
        description: error.message || 'Failed to fetch dashboard data',
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Center h="100vh">
        <Spinner size="xl" />
      </Center>
    );
  }

  if (error) {
    return (
      <Alert status="error" mb={6}>
        <AlertIcon />
        <Box>
          <Text fontWeight="bold">Error loading dashboard</Text>
          <Text>{error.message}</Text>
        </Box>
      </Alert>
    );
  }

  return (
    <Box>
      <Heading mb={6}>Dashboard</Heading>
      
      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} mb={8}>
        <StatCard
          label="Total Matches"
          value={stats.totalMatches.toLocaleString()}
          helpText="All recorded matches"
        />
        <StatCard
          label="Total Teams"
          value={stats.totalTeams.toLocaleString()}
          helpText="Active teams"
        />
        <StatCard
          label="Total Players"
          value={stats.totalPlayers.toLocaleString()}
          helpText="Registered players"
        />
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
        <Card>
          <CardHeader>
            <Heading size="md">Upcoming Matches</Heading>
          </CardHeader>
          <CardBody>
            {Array.isArray(stats.upcomingMatches) && stats.upcomingMatches.length > 0 ? (
              <Table variant="simple">
                <Thead>
                  <Tr>
                    <Th>Home Team</Th>
                    <Th>Away Team</Th>
                    <Th>Date</Th>
                    <Th>Competition</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {stats.upcomingMatches.map((match, index) => (
                    <Tr key={match.id || `match-${index}`}>
                      <Td>
                        <HStack spacing={2}>
                          {match.home_team_crest && (
                            <Image
                              src={match.home_team_crest}
                              alt={`${match.home_team_name} crest`}
                              boxSize="24px"
                              objectFit="contain"
                            />
                          )}
                          <Text>{match.home_team_name}</Text>
                        </HStack>
                      </Td>
                      <Td>
                        <HStack spacing={2}>
                          {match.away_team_crest && (
                            <Image
                              src={match.away_team_crest}
                              alt={`${match.away_team_name} crest`}
                              boxSize="24px"
                              objectFit="contain"
                            />
                          )}
                          <Text>{match.away_team_name}</Text>
                        </HStack>
                      </Td>
                      <Td>{match.match_date ? new Date(match.match_date).toLocaleDateString() : 'N/A'}</Td>
                      <Td>
                        <HStack spacing={2}>
                          {match.competition_emblem && (
                            <Image
                              src={match.competition_emblem}
                              alt={`${match.competition_name} emblem`}
                              boxSize="24px"
                              objectFit="contain"
                            />
                          )}
                          <Text>{match.competition_name}</Text>
                        </HStack>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            ) : (
              <Text textAlign="center" py={4} color="gray.500">No upcoming matches</Text>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Top Scorers</Heading>
          </CardHeader>
          <CardBody>
            {Array.isArray(stats.topScorers) && stats.topScorers.length > 0 ? (
              <Table variant="simple">
                <Thead>
                  <Tr>
                    <Th>Player</Th>
                    <Th>Team</Th>
                    <Th isNumeric>Goals</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {stats.topScorers.map((scorer, index) => (
                    <Tr key={scorer.id || `scorer-${index}`}>
                      <Td>
                        <Tooltip label={scorer.player_nationality} placement="top">
                          <HStack spacing={2}>
                            <Text fontWeight="medium">{index + 1}.</Text>
                            <Text>{scorer.player_name || 'Unknown Player'}</Text>
                          </HStack>
                        </Tooltip>
                      </Td>
                      <Td>
                        <HStack spacing={2}>
                          {scorer.team_crest && (
                            <Image
                              src={scorer.team_crest}
                              alt={`${scorer.team_name} crest`}
                              boxSize="24px"
                              objectFit="contain"
                            />
                          )}
                          <Text>{scorer.team_name || 'Unknown Team'}</Text>
                        </HStack>
                      </Td>
                      <Td isNumeric>
                        <HStack justify="flex-end" spacing={2}>
                          <Text fontWeight="bold">{scorer.goals}</Text>
                          {scorer.penalties > 0 && (
                            <Tooltip label={`Including ${scorer.penalties} penalties`} placement="top">
                              <Text fontSize="xs" color="gray.500">({scorer.penalties}p)</Text>
                            </Tooltip>
                          )}
                        </HStack>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            ) : (
              <Text textAlign="center" py={4} color="gray.500">No top scorers data available</Text>
            )}
          </CardBody>
        </Card>
      </SimpleGrid>
    </Box>
  );
}

const StatCard = ({ label, value, helpText }) => (
  <Card>
    <CardBody>
      <Stat>
        <StatLabel>{label}</StatLabel>
        <StatNumber>{value}</StatNumber>
        <StatHelpText>{helpText}</StatHelpText>
      </Stat>
    </CardBody>
  </Card>
);

export default Dashboard;
