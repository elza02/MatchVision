import { useState, useEffect } from 'react';
import {
  Box,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Text,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Stat,
  StatLabel,
  StatNumber,
  StatGroup,
  Badge,
  Spinner,
  useToast,
} from '@chakra-ui/react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import apiService from '../../services/api';

function TeamAnalytics({ teamId }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    fetchTeamAnalytics();
  }, [teamId]);

  const fetchTeamAnalytics = async () => {
    try {
      setLoading(true);
      const response = await apiService.getTeamAnalytics(teamId);
      setAnalytics(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load team analytics',
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
      <Box display="flex" justifyContent="center" alignItems="center" minH="300px">
        <Spinner size="xl" />
      </Box>
    );
  }

  if (!analytics) {
    return <Box>No analytics data available</Box>;
  }

  const formColors = {
    W: 'green',
    D: 'yellow',
    L: 'red',
  };

  return (
    <Box>
      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6} mb={6}>
        <Card>
          <CardHeader>
            <Heading size="md">Overall Statistics</Heading>
          </CardHeader>
          <CardBody>
            <StatGroup>
              <Stat>
                <StatLabel>Matches</StatLabel>
                <StatNumber>{analytics.match_statistics.total_matches}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Goals Scored</StatLabel>
                <StatNumber>{analytics.match_statistics.total_goals_scored}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Win Rate</StatLabel>
                <StatNumber>
                  {((analytics.match_statistics.total_wins / analytics.match_statistics.total_matches) * 100).toFixed(1)}%
                </StatNumber>
              </Stat>
            </StatGroup>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Recent Form</Heading>
          </CardHeader>
          <CardBody>
            <Box display="flex" gap={2}>
              {analytics.form_analysis.map((match, index) => (
                <Badge
                  key={index}
                  colorScheme={formColors[match.result]}
                  fontSize="lg"
                  p={2}
                >
                  {match.result}
                  <Text fontSize="xs">{match.score}</Text>
                </Badge>
              ))}
            </Box>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Top Scorers</Heading>
          </CardHeader>
          <CardBody>
            <Table size="sm">
              <Thead>
                <Tr>
                  <Th>Player</Th>
                  <Th isNumeric>Goals</Th>
                  <Th isNumeric>Assists</Th>
                </Tr>
              </Thead>
              <Tbody>
                {analytics.top_scorers.map((scorer) => (
                  <Tr key={scorer.id}>
                    <Td>{scorer.player_name}</Td>
                    <Td isNumeric>{scorer.goals}</Td>
                    <Td isNumeric>{scorer.assists}</Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </CardBody>
        </Card>
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
        <Card>
          <CardHeader>
            <Heading size="md">Home vs Away Performance</Heading>
          </CardHeader>
          <CardBody>
            <Box h="300px">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={[
                    {
                      name: 'Wins',
                      home: analytics.match_statistics.home_performance.wins,
                      away: analytics.match_statistics.away_performance.wins,
                    },
                    {
                      name: 'Draws',
                      home: analytics.match_statistics.home_performance.draws,
                      away: analytics.match_statistics.away_performance.draws,
                    },
                    {
                      name: 'Losses',
                      home: analytics.match_statistics.home_performance.losses,
                      away: analytics.match_statistics.away_performance.losses,
                    },
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="home" fill="#2196f3" name="Home" />
                  <Bar dataKey="away" fill="#f50057" name="Away" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Goals Analysis</Heading>
          </CardHeader>
          <CardBody>
            <Box h="300px">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={[
                    {
                      name: 'Home',
                      scored: analytics.match_statistics.home_performance.goals_scored,
                      conceded: analytics.match_statistics.home_performance.goals_conceded,
                    },
                    {
                      name: 'Away',
                      scored: analytics.match_statistics.away_performance.goals_scored,
                      conceded: analytics.match_statistics.away_performance.goals_conceded,
                    },
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="scored" stroke="#4caf50" name="Goals Scored" />
                  <Line type="monotone" dataKey="conceded" stroke="#f44336" name="Goals Conceded" />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>
      </SimpleGrid>
    </Box>
  );
}

export default TeamAnalytics;
