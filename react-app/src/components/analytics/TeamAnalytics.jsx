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
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
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
import axios from 'axios';

function TeamAnalytics({ teamId }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const toast = useToast();

  useEffect(() => {
    const fetchTeamAnalytics = async () => {
      if (!teamId) {
        console.log('No team ID provided, skipping fetch');
        return;
      }

      try {
        setLoading(true);
        setError(null);
        console.log('Fetching analytics for team:', teamId);
        
        const data = await apiService.getTeamAnalytics(teamId);
        console.log('Team analytics response:', data);

        if (!data || !data.performance || !data.summary) {
          console.error('Invalid data structure:', data);
          throw new Error('Invalid data structure received');
        }

        setAnalytics(data);
      } catch (error) {
        console.error('Error fetching team analytics:', error);
        setError(error.message || 'Failed to fetch team analytics');
        toast({
          title: 'Error',
          description: error.message || 'Failed to fetch team analytics',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchTeamAnalytics();
  }, [teamId, toast]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minH="300px">
        <Spinner size="xl" />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert status="error" mb={4}>
        <AlertIcon />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!analytics || !analytics.performance || !analytics.summary) {
    return (
      <Alert status="info" mb={4}>
        <AlertIcon />
        <AlertTitle>No Data</AlertTitle>
        <AlertDescription>No analytics data available for this team.</AlertDescription>
      </Alert>
    );
  }

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
                <StatNumber>{analytics.summary.total_matches}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Goals Scored</StatLabel>
                <StatNumber>{analytics.summary.goals_for}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Win Rate</StatLabel>
                <StatNumber>
                  {((analytics.summary.wins / analytics.summary.total_matches) * 100).toFixed(1)}%
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
              {analytics.performance.slice(-5).map((match, index) => (
                <Badge
                  key={index}
                  colorScheme={match.result === 'W' ? 'green' : match.result === 'D' ? 'yellow' : 'red'}
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
            <Heading size="md">Points Trend</Heading>
          </CardHeader>
          <CardBody>
            <Box h="300px">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart 
                  data={analytics.performance}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="match_date" 
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    formatter={(value, name) => [value, name === 'running_points' ? 'Total Points' : 'Average Points']}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="running_points"
                    stroke="#8884d8"
                    name="Total Points"
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="average_points"
                    stroke="#82ca9d"
                    name="Average Points"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
        <Card>
          <CardHeader>
            <Heading size="md">Results Distribution</Heading>
          </CardHeader>
          <CardBody>
            <Box h="300px">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={[
                    {
                      name: 'Wins',
                      value: analytics.summary.wins,
                    },
                    {
                      name: 'Draws',
                      value: analytics.summary.draws,
                    },
                    {
                      name: 'Losses',
                      value: analytics.summary.losses,
                    },
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8884d8" />
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
                <BarChart
                  data={[
                    {
                      name: 'Goals For',
                      value: analytics.summary.goals_for,
                    },
                    {
                      name: 'Goals Against',
                      value: analytics.summary.goals_against,
                    },
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>
      </SimpleGrid>
    </Box>
  );
}

export default TeamAnalytics;
