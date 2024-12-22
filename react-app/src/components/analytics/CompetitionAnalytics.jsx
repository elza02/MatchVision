import { useState, useEffect } from 'react';
import {
  Box,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  Heading,
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
  Spinner,
  useToast,
} from '@chakra-ui/react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';
import apiService from '../../services/api';

function CompetitionAnalytics({ competitionId }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    fetchCompetitionAnalytics();
  }, [competitionId]);

  const fetchCompetitionAnalytics = async () => {
    try {
      setLoading(true);
      const response = await apiService.getCompetitionAnalytics(competitionId);
      setAnalytics(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load competition analytics',
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

  return (
    <Box>
      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6} mb={6}>
        <Card>
          <CardHeader>
            <Heading size="md">Competition Overview</Heading>
          </CardHeader>
          <CardBody>
            <StatGroup>
              <Stat>
                <StatLabel>Teams</StatLabel>
                <StatNumber>{analytics.overview.total_teams}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Matches Played</StatLabel>
                <StatNumber>{analytics.overview.matches_played}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Total Goals</StatLabel>
                <StatNumber>{analytics.overview.total_goals}</StatNumber>
              </Stat>
            </StatGroup>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Average Stats</Heading>
          </CardHeader>
          <CardBody>
            <StatGroup>
              <Stat>
                <StatLabel>Goals per Match</StatLabel>
                <StatNumber>{analytics.overview.goals_per_match.toFixed(2)}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Cards per Match</StatLabel>
                <StatNumber>{analytics.overview.cards_per_match.toFixed(2)}</StatNumber>
              </Stat>
            </StatGroup>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Records</Heading>
          </CardHeader>
          <CardBody>
            <StatGroup>
              <Stat>
                <StatLabel>Highest Score</StatLabel>
                <StatNumber>{analytics.records.highest_score}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Most Goals</StatLabel>
                <StatNumber>{analytics.records.most_goals_in_match}</StatNumber>
              </Stat>
            </StatGroup>
          </CardBody>
        </Card>
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6} mb={6}>
        <Card>
          <CardHeader>
            <Heading size="md">Top Scorers</Heading>
          </CardHeader>
          <CardBody>
            <Box h="300px">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analytics.top_scorers.slice(0, 5)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="player_name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="goals" fill="#2196f3" name="Goals" />
                  <Bar dataKey="assists" fill="#4caf50" name="Assists" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Goals per Matchday</Heading>
          </CardHeader>
          <CardBody>
            <Box h="300px">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={analytics.goals_per_matchday}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="matchday" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="goals" stroke="#2196f3" name="Goals" />
                  <Line type="monotone" dataKey="average" stroke="#f50057" name="Average" />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>
      </SimpleGrid>

      <Card>
        <CardHeader>
          <Heading size="md">League Standings</Heading>
        </CardHeader>
        <CardBody>
          <Table>
            <Thead>
              <Tr>
                <Th>Pos</Th>
                <Th>Team</Th>
                <Th isNumeric>P</Th>
                <Th isNumeric>W</Th>
                <Th isNumeric>D</Th>
                <Th isNumeric>L</Th>
                <Th isNumeric>GF</Th>
                <Th isNumeric>GA</Th>
                <Th isNumeric>GD</Th>
                <Th isNumeric>Pts</Th>
              </Tr>
            </Thead>
            <Tbody>
              {analytics.standings.map((team, index) => (
                <Tr key={team.id}>
                  <Td>{index + 1}</Td>
                  <Td>{team.name}</Td>
                  <Td isNumeric>{team.matches_played}</Td>
                  <Td isNumeric>{team.wins}</Td>
                  <Td isNumeric>{team.draws}</Td>
                  <Td isNumeric>{team.losses}</Td>
                  <Td isNumeric>{team.goals_for}</Td>
                  <Td isNumeric>{team.goals_against}</Td>
                  <Td isNumeric>{team.goal_difference}</Td>
                  <Td isNumeric fontWeight="bold">{team.points}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </CardBody>
      </Card>
    </Box>
  );
}

export default CompetitionAnalytics;
