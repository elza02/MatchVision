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
  Text
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
    const unsubscribeMatches = pollingService.subscribe('/dashboard/upcoming-matches/', handleMatchesUpdate, 30000);
    const unsubscribeScorers = pollingService.subscribe('/dashboard/top-scorers/', handleScorersUpdate, 30000);

    // Cleanup function
    return () => {
      unsubscribeStats();
      unsubscribeMatches();
      unsubscribeScorers();
    };
  }, []);

  const handleStatsUpdate = (data, error) => {
    if (error) {
      const { message, retryCount, maxRetries } = error;
      toast({
        title: 'Error updating stats',
        description: `${message}${retryCount ? ` (Attempt ${retryCount}/${maxRetries})` : ''}`,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }

    if (data) {
      setStats(prevStats => ({
        ...prevStats,
        totalMatches: data.totalMatches,
        totalTeams: data.totalTeams,
        totalPlayers: data.totalPlayers,
      }));
    }
  };

  const handleMatchesUpdate = (data, error) => {
    if (error) {
      const { message, retryCount, maxRetries } = error;
      toast({
        title: 'Error updating matches',
        description: `${message}${retryCount ? ` (Attempt ${retryCount}/${maxRetries})` : ''}`,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }

    if (data) {
      setStats(prevStats => ({
        ...prevStats,
        upcomingMatches: data.upcomingMatches,
      }));
    }
  };

  const handleScorersUpdate = (data, error) => {
    if (error) {
      const { message, retryCount, maxRetries } = error;
      toast({
        title: 'Error updating top scorers',
        description: `${message}${retryCount ? ` (Attempt ${retryCount}/${maxRetries})` : ''}`,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }

    if (data) {
      setStats(prevStats => ({
        ...prevStats,
        topScorers: data.topScorers,
      }));
    }
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [statsResponse, matchesResponse, scorersResponse] = await Promise.all([
        apiService.getDashboardStats(),
        apiService.getDashboardMatches(),
        apiService.getDashboardScorers()
      ]);

      setStats({
        totalMatches: statsResponse.data.totalMatches,
        totalTeams: statsResponse.data.totalTeams,
        totalPlayers: statsResponse.data.totalPlayers,
        upcomingMatches: matchesResponse.data.upcomingMatches,
        topScorers: scorersResponse.data.topScorers
      });
    } catch (err) {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to load dashboard data';
      setError(errorMessage);
      toast({
        title: 'Error loading dashboard',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
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
          <Text>{error}</Text>
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
          value={stats.totalMatches}
          helpText="All recorded matches"
        />
        <StatCard
          label="Total Teams"
          value={stats.totalTeams}
          helpText="Active teams"
        />
        <StatCard
          label="Total Players"
          value={stats.totalPlayers}
          helpText="Registered players"
        />
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
        <Card>
          <CardHeader>
            <Heading size="md">Upcoming Matches</Heading>
          </CardHeader>
          <CardBody>
            {stats.upcomingMatches.length > 0 ? (
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
                  {stats.upcomingMatches.map((match) => (
                    <Tr key={match.id}>
                      <Td>{match.homeTeam}</Td>
                      <Td>{match.awayTeam}</Td>
                      <Td>{match.date instanceof Date ? match.date.toLocaleDateString() : new Date(match.date).toLocaleDateString()}</Td>
                      <Td>{match.competition}</Td>
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
            {stats.topScorers.length > 0 ? (
              <Table variant="simple">
                <Thead>
                  <Tr>
                    <Th>Player</Th>
                    <Th>Team</Th>
                    <Th isNumeric>Goals</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {stats.topScorers.map((scorer) => (
                    <Tr key={scorer.playerId}>
                      <Td>{scorer.playerName}</Td>
                      <Td>{scorer.team}</Td>
                      <Td isNumeric>{scorer.goals}</Td>
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
