import { useState, useEffect } from 'react';
import {
  Box,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Select,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Stack,
  Text,
  Progress,
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
import api from '../../services/api';

function Analytics() {
  const [competitions, setCompetitions] = useState([]);
  const [selectedCompetition, setSelectedCompetition] = useState('');
  const [analyticsData, setAnalyticsData] = useState({
    standings: [],
    topScorers: [],
    matches: [],
  });
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    fetchCompetitions();
  }, []);

  useEffect(() => {
    if (selectedCompetition) {
      fetchAnalyticsData();
    }
  }, [selectedCompetition]);

  const fetchCompetitions = async () => {
    try {
      const response = await api.get('/competitions/');
      setCompetitions(response.data);
      if (response.data.length > 0) {
        setSelectedCompetition(response.data[0].id);
      }
    } catch (error) {
      console.error('Error fetching competitions:', error);
      setLoading(false);
    }
  };

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const [standingsRes, scorersRes, matchesRes] = await Promise.all([
        api.get(`/competitions/${selectedCompetition}/standings/`),
        api.get(`/top-scorers/?competition=${selectedCompetition}`),
        api.get(`/matches/?competition=${selectedCompetition}`),
      ]);

      setAnalyticsData({
        standings: standingsRes.data || [],
        topScorers: scorersRes.data || [],
        matches: matchesRes.data?.results || [], // Access the results array from the paginated response
      });
    } catch (error) {
      console.error('Error fetching analytics data:', error);
      toast({
        title: 'Error',
        description: 'Failed to load analytics data. Please try again later.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const prepareMatchData = () => {
    if (!analyticsData?.matches?.length) return [];

    return analyticsData.matches
      .slice(-10)
      .map((match) => ({
        date: new Date(match.match_date).toLocaleDateString(),
        goals: (match.home_team_score !== null && match.away_team_score !== null) 
          ? match.home_team_score + match.away_team_score 
          : 0,
      }))
      .reverse();
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minH="500px">
        <Spinner size="xl" />
      </Box>
    );
  }

  return (
    <Box>
      <Box mb={6}>
        <Heading mb={4}>Analytics</Heading>
        <Select
          value={selectedCompetition}
          onChange={(e) => setSelectedCompetition(e.target.value)}
          maxW="300px"
        >
          {competitions.map((competition) => (
            <option key={competition.id} value={competition.id}>
              {competition.name}
            </option>
          ))}
        </Select>
      </Box>

      <Tabs>
        <TabList>
          <Tab>Overview</Tab>
          <Tab>Team Performance</Tab>
          <Tab>Player Stats</Tab>
        </TabList>

        <TabPanels>
          <TabPanel>
            <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
              <Card>
                <CardHeader>
                  <Heading size="md">Goals per Match Trend</Heading>
                </CardHeader>
                <CardBody>
                  <Box h="300px">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={prepareMatchData()}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="goals" stroke="#2196f3" />
                      </LineChart>
                    </ResponsiveContainer>
                  </Box>
                </CardBody>
              </Card>

              <Card>
                <CardHeader>
                  <Heading size="md">Top Scorers</Heading>
                </CardHeader>
                <CardBody>
                  <Box h="300px">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={analyticsData?.topScorers.slice(0, 5)}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="player_name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="goals" fill="#2196f3" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                </CardBody>
              </Card>
            </SimpleGrid>
          </TabPanel>

          <TabPanel>
            <Card>
              <CardHeader>
                <Heading size="md">Team Standings</Heading>
              </CardHeader>
              <CardBody>
                <Table variant="simple">
                  <Thead>
                    <Tr>
                      <Th>Team</Th>
                      <Th isNumeric>Matches</Th>
                      <Th isNumeric>Goals</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {analyticsData?.standings.map((team) => (
                      <Tr key={team.team.id}>
                        <Td>{team.team.name}</Td>
                        <Td isNumeric>{team.matches_played}</Td>
                        <Td isNumeric>{team.goals_scored}</Td>
                      </Tr>
                    ))}
                  </Tbody>
                </Table>
              </CardBody>
            </Card>
          </TabPanel>

          <TabPanel>
            <Card>
              <CardHeader>
                <Heading size="md">Top Scorers</Heading>
              </CardHeader>
              <CardBody>
                <Stack spacing={4}>
                  {analyticsData?.topScorers.slice(0, 10).map((scorer) => (
                    <Box key={scorer.player_id}>
                      <Stack direction="row" justify="space-between" mb={1}>
                        <Text>{scorer.player_name}</Text>
                        <Text>{scorer.goals} goals</Text>
                      </Stack>
                      <Progress
                        value={(scorer.goals / analyticsData.topScorers[0].goals) * 100}
                        colorScheme="brand"
                      />
                    </Box>
                  ))}
                </Stack>
              </CardBody>
            </Card>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
}

export default Analytics;
