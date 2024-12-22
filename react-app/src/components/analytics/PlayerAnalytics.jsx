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
} from 'recharts';
import apiService from '../../services/api';

function PlayerAnalytics({ playerId }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    fetchPlayerAnalytics();
  }, [playerId]);

  const fetchPlayerAnalytics = async () => {
    try {
      setLoading(true);
      const response = await apiService.getPlayerAnalytics(playerId);
      setAnalytics(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load player analytics',
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
            <Heading size="md">Season Statistics</Heading>
          </CardHeader>
          <CardBody>
            <StatGroup>
              <Stat>
                <StatLabel>Matches</StatLabel>
                <StatNumber>{analytics.season_stats.matches_played}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Goals</StatLabel>
                <StatNumber>{analytics.season_stats.goals}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Assists</StatLabel>
                <StatNumber>{analytics.season_stats.assists}</StatNumber>
              </Stat>
            </StatGroup>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Performance Stats</Heading>
          </CardHeader>
          <CardBody>
            <StatGroup>
              <Stat>
                <StatLabel>Minutes Played</StatLabel>
                <StatNumber>{analytics.season_stats.minutes_played}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Yellow Cards</StatLabel>
                <StatNumber>{analytics.season_stats.yellow_cards}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Red Cards</StatLabel>
                <StatNumber>{analytics.season_stats.red_cards}</StatNumber>
              </Stat>
            </StatGroup>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Average Ratings</Heading>
          </CardHeader>
          <CardBody>
            <StatGroup>
              <Stat>
                <StatLabel>Overall Rating</StatLabel>
                <StatNumber>{analytics.season_stats.average_rating.toFixed(1)}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Form Rating</StatLabel>
                <StatNumber>{analytics.recent_form.average_rating.toFixed(1)}</StatNumber>
              </Stat>
            </StatGroup>
          </CardBody>
        </Card>
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
        <Card>
          <CardHeader>
            <Heading size="md">Performance Trend</Heading>
          </CardHeader>
          <CardBody>
            <Box h="300px">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={analytics.performance_trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="match_date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="rating" stroke="#2196f3" name="Match Rating" />
                  <Line type="monotone" dataKey="minutes_played" stroke="#4caf50" name="Minutes Played" />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Recent Matches</Heading>
          </CardHeader>
          <CardBody>
            <Table size="sm">
              <Thead>
                <Tr>
                  <Th>Date</Th>
                  <Th>Opponent</Th>
                  <Th>Result</Th>
                  <Th isNumeric>Goals</Th>
                  <Th isNumeric>Assists</Th>
                  <Th isNumeric>Rating</Th>
                </Tr>
              </Thead>
              <Tbody>
                {analytics.recent_matches.map((match, index) => (
                  <Tr key={index}>
                    <Td>{new Date(match.date).toLocaleDateString()}</Td>
                    <Td>{match.opponent}</Td>
                    <Td>
                      <Text
                        color={match.result === 'W' ? 'green.500' : match.result === 'L' ? 'red.500' : 'yellow.500'}
                        fontWeight="bold"
                      >
                        {match.score}
                      </Text>
                    </Td>
                    <Td isNumeric>{match.goals}</Td>
                    <Td isNumeric>{match.assists}</Td>
                    <Td isNumeric>{match.rating.toFixed(1)}</Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </CardBody>
        </Card>
      </SimpleGrid>
    </Box>
  );
}

export default PlayerAnalytics;
