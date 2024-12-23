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
  Spinner,
  useToast,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Container,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Center
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
const CHART_HEIGHT = 400;
const CHART_WIDTH = 800;
const CHART_ASPECT = 2;
const PIE_CHART_HEIGHT = 600;

const ChartContainer = ({ children, height = CHART_HEIGHT, aspect = CHART_ASPECT }) => (
  <Box width="100%" minH={height}>
    <ResponsiveContainer width="100%" height={height} aspect={aspect} debounce={1}>
      {children}
    </ResponsiveContainer>
  </Box>
);

function Analytics() {
  const [overview, setOverview] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [teams, setTeams] = useState([]);
  const [teamAnalytics, setTeamAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabIndex, setTabIndex] = useState(0);
  const toast = useToast();

  const fetchOverview = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.getAnalyticsOverview();
      console.log('Overview data:', response);
      setOverview(response);
    } catch (err) {
      console.error('Error fetching overview:', err);
      setError(err.message || 'Failed to fetch analytics overview');
      toast({
        title: 'Error',
        description: 'Failed to fetch analytics overview',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchTeams = async () => {
    try {
      const response = await api.getTeams();
      console.log('Teams data:', response);
      if (response && response.data) {
        setTeams(response.data);
      } else {
        setTeams([]);
        console.error('Invalid teams response:', response);
      }
    } catch (err) {
      console.error('Error fetching teams:', err);
      setTeams([]);
      toast({
        title: 'Error',
        description: 'Failed to fetch teams',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const fetchTeamAnalytics = async (teamId) => {
    if (!teamId) return;
    
    try {
      setLoading(true);
      setError(null);
      const response = await api.getTeamAnalytics(teamId);
      console.log('Team analytics data:', response);
      setTeamAnalytics(response.data);
    } catch (err) {
      console.error('Error fetching team analytics:', err);
      setError(err.message || 'Failed to fetch team analytics');
      toast({
        title: 'Error',
        description: 'Failed to fetch team analytics',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
    fetchTeams();
  }, []);

  useEffect(() => {
    if (selectedTeam) {
      fetchTeamAnalytics(selectedTeam);
    } else {
      setTeamAnalytics(null);
    }
  }, [selectedTeam]);

  if (loading && !overview && !teamAnalytics) {
    return (
      <Center p={8}>
        <Spinner size="xl" />
      </Center>
    );
  }

  if (error) {
    return (
      <Alert status="error">
        <AlertIcon />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <Container maxW="container.xl" p={4}>
      <Tabs index={tabIndex} onChange={setTabIndex}>
        <TabList mb={4}>
          <Tab>Overview</Tab>
          <Tab>Team Analysis</Tab>
          <Tab>Teams by Area</Tab>
        </TabList>

        <TabPanels>
          <TabPanel>
            {overview?.summary && (
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
                  <Card>
                    <CardBody>
                      <Stat>
                        <StatLabel>Total Teams</StatLabel>
                        <StatNumber>{overview.summary.total_teams}</StatNumber>
                      </Stat>
                    </CardBody>
                  </Card>
                </SimpleGrid>

                {overview.goals_trend && overview.goals_trend.length > 0 && (
                  <Card>
                    <CardHeader>
                      <Heading size="md">Goals Trend</Heading>
                    </CardHeader>
                    <CardBody>
                      <Box height="400px">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={overview.goals_trend}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis 
                              dataKey="date"
                              tickFormatter={(value) => new Date(value).toLocaleDateString()}
                            />
                            <YAxis />
                            <Tooltip 
                              labelFormatter={(value) => new Date(value).toLocaleDateString()}
                            />
                            <Legend />
                            <Line
                              type="monotone"
                              dataKey="average_goals"
                              stroke="#8884d8"
                              name="Average Goals"
                              dot={false}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </Box>
                    </CardBody>
                  </Card>
                )}
              </>
            )}
          </TabPanel>

          <TabPanel>
            <Box mb={4}>
              <Select
                value={selectedTeam || ''}
                onChange={(e) => setSelectedTeam(e.target.value)}
                placeholder="Select a team"
                isDisabled={!teams || teams.length === 0}
              >
                {Array.isArray(teams) && teams.map((team) => (
                  <option key={team.id} value={team.id}>
                    {team.name}
                  </option>
                ))}
              </Select>
            </Box>

            {teamAnalytics?.summary && (
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                <Card>
                  <CardHeader>
                    <Heading size="md">Team Summary</Heading>
                  </CardHeader>
                  <CardBody>
                    <SimpleGrid columns={2} spacing={4}>
                      <Stat>
                        <StatLabel>Matches</StatLabel>
                        <StatNumber>{teamAnalytics.summary.total_matches}</StatNumber>
                      </Stat>
                      <Stat>
                        <StatLabel>Points</StatLabel>
                        <StatNumber>{teamAnalytics.summary.points}</StatNumber>
                        <StatHelpText>
                          Avg: {teamAnalytics.summary.average_points} per match
                        </StatHelpText>
                      </Stat>
                      <Stat>
                        <StatLabel>Record</StatLabel>
                        <StatNumber>
                          {teamAnalytics.summary.wins}W-{teamAnalytics.summary.draws}D-{teamAnalytics.summary.losses}L
                        </StatNumber>
                      </Stat>
                      <Stat>
                        <StatLabel>Goals</StatLabel>
                        <StatNumber>
                          {teamAnalytics.summary.goals_for}-{teamAnalytics.summary.goals_against}
                        </StatNumber>
                        <StatHelpText>
                          Diff: {teamAnalytics.summary.goal_difference}
                        </StatHelpText>
                      </Stat>
                    </SimpleGrid>
                  </CardBody>
                </Card>

                {teamAnalytics.performance && teamAnalytics.performance.length > 0 && (
                  <Card>
                    <CardHeader>
                      <Heading size="md">Points Progression</Heading>
                    </CardHeader>
                    <CardBody>
                      <Box height="300px">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={teamAnalytics.performance}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis 
                              dataKey="match_date"
                              tickFormatter={(value) => new Date(value).toLocaleDateString()}
                            />
                            <YAxis />
                            <Tooltip 
                              labelFormatter={(value) => new Date(value).toLocaleDateString()}
                            />
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
                )}
              </SimpleGrid>
            )}
          </TabPanel>

          <TabPanel>
            {overview?.area_stats && overview.area_stats.length > 0 && (
              <Box>
                <Card>
                  <CardHeader>
                    <Heading size="md">Teams Distribution by Area</Heading>
                    <Text mt={2} color="gray.600">
                      Overview of how teams are distributed across different areas
                    </Text>
                  </CardHeader>
                  <CardBody p={0}>
                    <Box height="800px">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={overview.area_stats}
                            dataKey="team_count"
                            nameKey="name"
                            cx="50%"
                            cy="50%"
                            outerRadius="90%"
                            innerRadius="40%"
                            paddingAngle={2}
                            label={({
                              cx,
                              cy,
                              midAngle,
                              innerRadius,
                              outerRadius,
                              value,
                              name
                            }) => {
                              const RADIAN = Math.PI / 180;
                              const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
                              const x = cx + radius * Math.cos(-midAngle * RADIAN);
                              const y = cy + radius * Math.sin(-midAngle * RADIAN);
                              return (
                                <text
                                  x={x}
                                  y={y}
                                  fill="white"
                                  textAnchor={x > cx ? 'start' : 'end'}
                                  dominantBaseline="central"
                                  style={{
                                    fontSize: '16px',
                                    fontWeight: 'bold',
                                    textShadow: '2px 2px 4px rgba(0,0,0,0.5)'
                                  }}
                                >
                                  {`${name}`}
                                </text>
                              );
                            }}
                          >
                            {overview.area_stats.map((entry, index) => (
                              <Cell
                                key={`cell-${index}`}
                                fill={COLORS[index % COLORS.length]}
                              />
                            ))}
                          </Pie>
                          <Tooltip 
                            formatter={(value, name) => [`${value} teams`, name]}
                            contentStyle={{
                              backgroundColor: 'rgba(255, 255, 255, 0.95)',
                              borderRadius: '8px',
                              padding: '12px',
                              fontSize: '14px',
                              boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
                            }}
                          />
                          <Legend 
                            verticalAlign="middle"
                            align="right"
                            layout="vertical"
                            iconSize={12}
                            wrapperStyle={{
                              fontSize: '14px',
                              paddingRight: '20px',
                              right: 0,
                              width: 'auto'
                            }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </Box>
                  </CardBody>
                </Card>

                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} mt={4}>
                  {overview.area_stats.map((stat) => (
                    <Card key={stat.name}>
                      <CardBody>
                        <Stat>
                          <StatLabel>{stat.name}</StatLabel>
                          <StatNumber>{stat.team_count}</StatNumber>
                          <StatHelpText>
                            {((stat.team_count / overview.summary.total_teams) * 100).toFixed(1)}% of total teams
                          </StatHelpText>
                        </Stat>
                      </CardBody>
                    </Card>
                  ))}
                </SimpleGrid>
              </Box>
            )}
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Container>
  );
}

export default Analytics;
