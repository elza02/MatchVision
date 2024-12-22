import { useState, useEffect } from 'react';
import {
  Box,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Select,
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
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
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
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import api from '../../services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

function Analytics() {
  const [overview, setOverview] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [teams, setTeams] = useState([]);
  const [teamAnalytics, setTeamAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    fetchOverview();
    fetchTeams();
  }, []);

  useEffect(() => {
    if (selectedTeam) {
      fetchTeamAnalytics(selectedTeam);
    }
  }, [selectedTeam]);

  const fetchOverview = async () => {
    try {
      const response = await api.get('/analytics/overview/');
      setOverview(response.data);
    } catch (error) {
      console.error('Error fetching overview:', error);
      toast({
        title: 'Error',
        description: 'Failed to load analytics overview',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const fetchTeams = async () => {
    try {
      const response = await api.get('/teams/');
      setTeams(response.data.results);
      if (response.data.results.length > 0) {
        setSelectedTeam(response.data.results[0].id);
      }
    } catch (error) {
      console.error('Error fetching teams:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTeamAnalytics = async (teamId) => {
    try {
      setLoading(true);
      const response = await api.get(`/analytics/team/${teamId}/`);
      setTeamAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching team analytics:', error);
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
      <Box p={4} display="flex" justifyContent="center" alignItems="center">
        <Spinner size="xl" />
      </Box>
    );
  }

  return (
    <Box p={4}>
      <Tabs>
        <TabList>
          <Tab>Overview</Tab>
          <Tab>Team Analysis</Tab>
        </TabList>

        <TabPanels>
          <TabPanel>
            {overview && (
              <>
                <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4} mb={8}>
                  <Card>
                    <CardBody>
                      <Stat>
                        <StatLabel>Total Matches</StatLabel>
                        <StatNumber>{overview.summary.total_matches}</StatNumber>
                      </Stat>
                    </CardBody>
                  </Card>
                  <Card>
                    <CardBody>
                      <Stat>
                        <StatLabel>Total Goals</StatLabel>
                        <StatNumber>{overview.summary.total_goals}</StatNumber>
                        <StatHelpText>
                          Avg: {overview.summary.average_goals_per_match} per match
                        </StatHelpText>
                      </Stat>
                    </CardBody>
                  </Card>
                </SimpleGrid>

                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                  <Card>
                    <CardHeader>
                      <Heading size="md">Goals Trend</Heading>
                    </CardHeader>
                    <CardBody>
                      <Box h="300px">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={overview.goals_trend}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="matchday" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line
                              type="monotone"
                              dataKey="average_goals"
                              stroke="#8884d8"
                              name="Average Goals"
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </Box>
                    </CardBody>
                  </Card>

                  <Card>
                    <CardHeader>
                      <Heading size="md">Teams by Area</Heading>
                    </CardHeader>
                    <CardBody>
                      <Box h="300px">
                        <ResponsiveContainer width="100%" height="100%">
                          <PieChart>
                            <Pie
                              data={overview.area_stats}
                              dataKey="team_count"
                              nameKey="name"
                              cx="50%"
                              cy="50%"
                              outerRadius={100}
                              fill="#8884d8"
                            >
                              {overview.area_stats.map((entry, index) => (
                                <Cell
                                  key={`cell-${index}`}
                                  fill={COLORS[index % COLORS.length]}
                                />
                              ))}
                            </Pie>
                            <Tooltip />
                            <Legend />
                          </PieChart>
                        </ResponsiveContainer>
                      </Box>
                    </CardBody>
                  </Card>
                </SimpleGrid>
              </>
            )}
          </TabPanel>

          <TabPanel>
            <Box mb={4}>
              <Select
                value={selectedTeam}
                onChange={(e) => setSelectedTeam(e.target.value)}
              >
                {teams.map((team) => (
                  <option key={team.id} value={team.id}>
                    {team.name}
                  </option>
                ))}
              </Select>
            </Box>

            {teamAnalytics && (
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                <Card>
                  <CardHeader>
                    <Heading size="md">Points Progression</Heading>
                  </CardHeader>
                  <CardBody>
                    <Box h="300px">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={teamAnalytics.performance}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="match_date" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Line
                            type="monotone"
                            dataKey="running_points"
                            stroke="#8884d8"
                            name="Total Points"
                          />
                          <Line
                            type="monotone"
                            dataKey="average_points"
                            stroke="#82ca9d"
                            name="Average Points"
                          />
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
                        <BarChart data={teamAnalytics.top_scorers}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="player" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Bar dataKey="goals" fill="#8884d8" name="Goals" />
                          <Bar dataKey="assists" fill="#82ca9d" name="Assists" />
                        </BarChart>
                      </ResponsiveContainer>
                    </Box>
                  </CardBody>
                </Card>
              </SimpleGrid>
            )}
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
}

export default Analytics;
