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
  Progress,
  Spinner,
  useToast,
} from '@chakra-ui/react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
} from 'recharts';
import apiService from '../../services/api';

function MatchAnalytics({ matchId }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    fetchMatchAnalytics();
  }, [matchId]);

  const fetchMatchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await apiService.getMatchAnalytics(matchId);
      setAnalytics(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load match analytics',
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

  const radarData = [
    {
      stat: 'Possession',
      home: analytics.match_stats.home_team.possession,
      away: analytics.match_stats.away_team.possession,
    },
    {
      stat: 'Shots',
      home: analytics.match_stats.home_team.shots,
      away: analytics.match_stats.away_team.shots,
    },
    {
      stat: 'Shots on Target',
      home: analytics.match_stats.home_team.shots_on_target,
      away: analytics.match_stats.away_team.shots_on_target,
    },
    {
      stat: 'Corners',
      home: analytics.match_stats.home_team.corners,
      away: analytics.match_stats.away_team.corners,
    },
    {
      stat: 'Fouls',
      home: analytics.match_stats.home_team.fouls,
      away: analytics.match_stats.away_team.fouls,
    },
  ];

  return (
    <Box>
      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} mb={6}>
        <Card>
          <CardHeader>
            <Heading size="md">Match Statistics</Heading>
          </CardHeader>
          <CardBody>
            <StatGroup mb={4}>
              <Stat>
                <StatLabel>Possession</StatLabel>
                <Progress
                  value={analytics.match_stats.home_team.possession}
                  colorScheme="blue"
                  hasStripe
                />
                <StatNumber>
                  {analytics.match_stats.home_team.possession}% - {analytics.match_stats.away_team.possession}%
                </StatNumber>
              </Stat>
            </StatGroup>

            <Table size="sm">
              <Thead>
                <Tr>
                  <Th>{analytics.home_team.name}</Th>
                  <Th textAlign="center">Stat</Th>
                  <Th textAlign="right">{analytics.away_team.name}</Th>
                </Tr>
              </Thead>
              <Tbody>
                <Tr>
                  <Td>{analytics.match_stats.home_team.shots}</Td>
                  <Td textAlign="center">Shots</Td>
                  <Td textAlign="right">{analytics.match_stats.away_team.shots}</Td>
                </Tr>
                <Tr>
                  <Td>{analytics.match_stats.home_team.shots_on_target}</Td>
                  <Td textAlign="center">Shots on Target</Td>
                  <Td textAlign="right">{analytics.match_stats.away_team.shots_on_target}</Td>
                </Tr>
                <Tr>
                  <Td>{analytics.match_stats.home_team.corners}</Td>
                  <Td textAlign="center">Corners</Td>
                  <Td textAlign="right">{analytics.match_stats.away_team.corners}</Td>
                </Tr>
                <Tr>
                  <Td>{analytics.match_stats.home_team.fouls}</Td>
                  <Td textAlign="center">Fouls</Td>
                  <Td textAlign="right">{analytics.match_stats.away_team.fouls}</Td>
                </Tr>
              </Tbody>
            </Table>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Performance Comparison</Heading>
          </CardHeader>
          <CardBody>
            <Box h="300px">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="stat" />
                  <PolarRadiusAxis />
                  <Radar
                    name={analytics.home_team.name}
                    dataKey="home"
                    stroke="#2196f3"
                    fill="#2196f3"
                    fillOpacity={0.6}
                  />
                  <Radar
                    name={analytics.away_team.name}
                    dataKey="away"
                    stroke="#f50057"
                    fill="#f50057"
                    fillOpacity={0.6}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
        <Card>
          <CardHeader>
            <Heading size="md">Head to Head History</Heading>
          </CardHeader>
          <CardBody>
            <Table size="sm">
              <Thead>
                <Tr>
                  <Th>Date</Th>
                  <Th>Score</Th>
                  <Th>Competition</Th>
                </Tr>
              </Thead>
              <Tbody>
                {analytics.head_to_head.map((match, index) => (
                  <Tr key={index}>
                    <Td>{new Date(match.date).toLocaleDateString()}</Td>
                    <Td>{match.score}</Td>
                    <Td>{match.competition}</Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">Team Form</Heading>
          </CardHeader>
          <CardBody>
            <Box>
              <Text fontWeight="bold" mb={2}>{analytics.home_team.name}</Text>
              <Table size="sm" mb={4}>
                <Tbody>
                  {analytics.home_team.recent_form.map((match, index) => (
                    <Tr key={index}>
                      <Td>{new Date(match.date).toLocaleDateString()}</Td>
                      <Td>{match.opponent}</Td>
                      <Td>{match.score}</Td>
                      <Td>
                        <Text
                          color={match.result === 'W' ? 'green.500' : match.result === 'L' ? 'red.500' : 'yellow.500'}
                          fontWeight="bold"
                        >
                          {match.result}
                        </Text>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>

              <Text fontWeight="bold" mb={2}>{analytics.away_team.name}</Text>
              <Table size="sm">
                <Tbody>
                  {analytics.away_team.recent_form.map((match, index) => (
                    <Tr key={index}>
                      <Td>{new Date(match.date).toLocaleDateString()}</Td>
                      <Td>{match.opponent}</Td>
                      <Td>{match.score}</Td>
                      <Td>
                        <Text
                          color={match.result === 'W' ? 'green.500' : match.result === 'L' ? 'red.500' : 'yellow.500'}
                          fontWeight="bold"
                        >
                          {match.result}
                        </Text>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </Box>
          </CardBody>
        </Card>
      </SimpleGrid>
    </Box>
  );
}

export default MatchAnalytics;
