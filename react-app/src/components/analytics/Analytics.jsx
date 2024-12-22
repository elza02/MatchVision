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
  const [isMounted, setIsMounted] = useState(false);
  const [tabIndex, setTabIndex] = useState(0);
  const toast = useToast();

  useEffect(() => {
    setIsMounted(true);
    return () => setIsMounted(false);
  }, []);

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
      <Box p={4} display="flex" justifyContent="center" alignItems="center" height={CHART_HEIGHT}>
        <Spinner size="xl" />
      </Box>
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
            {overview && isMounted && (
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

                <Card>
                  <CardHeader>
                    <Heading size="md">Goals Trend</Heading>
                  </CardHeader>
                  <CardBody>
                    <ChartContainer>
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
                    </ChartContainer>
                  </CardBody>
                </Card>
              </>
            )}
          </TabPanel>

          <TabPanel>
            <Box mb={4}>
              <Select
                value={selectedTeam || ''}
                onChange={(e) => setSelectedTeam(e.target.value)}
                placeholder="Select a team"
              >
                {teams.map((team) => (
                  <option key={team.id} value={team.id}>
                    {team.name}
                  </option>
                ))}
              </Select>
            </Box>

            {teamAnalytics && isMounted && (
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                <Card>
                  <CardHeader>
                    <Heading size="md">Points Progression</Heading>
                  </CardHeader>
                  <CardBody>
                    <ChartContainer>
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
                    </ChartContainer>
                  </CardBody>
                </Card>

                <Card>
                  <CardHeader>
                    <Heading size="md">Top Scorers</Heading>
                  </CardHeader>
                  <CardBody>
                    <ChartContainer>
                      <BarChart data={teamAnalytics.top_scorers}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="player" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="goals" fill="#8884d8" name="Goals" />
                        <Bar dataKey="assists" fill="#82ca9d" name="Assists" />
                      </BarChart>
                    </ChartContainer>
                  </CardBody>
                </Card>
              </SimpleGrid>
            )}
          </TabPanel>

          <TabPanel>
            {overview && isMounted && (
              <Box>
                <Card>
                  <CardHeader>
                    <Heading size="md">Teams Distribution by Area</Heading>
                    <Text mt={2} color="gray.600">
                      Overview of how teams are distributed across different areas
                    </Text>
                  </CardHeader>
                  <CardBody p={0}>
                    <Box height="800px" position="relative">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart margin={{ right: 200 }}>
                          <Pie
                            data={overview.area_stats}
                            dataKey="team_count"
                            nameKey="name"
                            cx="45%"
                            cy="50%"
                            outerRadius="85%"
                            innerRadius="35%"
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
                              position: 'absolute',
                              right: 20,
                              top: '50%',
                              transform: 'translateY(-50%)',
                              maxHeight: '70%',
                              overflowY: 'auto',
                              backgroundColor: 'rgba(255, 255, 255, 0.9)',
                              borderRadius: '8px',
                              padding: '12px',
                              boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
                              width: '180px'
                            }}
                            formatter={(value, entry) => (
                              <span style={{ 
                                color: '#333',
                                fontSize: '13px',
                                display: 'block',
                                lineHeight: '1.4'
                              }}>
                                {`${value} (${overview.area_stats.find(stat => stat.name === value)?.team_count})`}
                              </span>
                            )}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </Box>
                  </CardBody>
                </Card>

                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} mt={4}>
                  {overview.area_stats.map((stat, index) => {
                    const percentage = overview.summary.total_teams > 0 
                      ? ((stat.team_count / overview.summary.total_teams) * 100).toFixed(1) 
                      : 0;
                    return (
                      <Card key={stat.name}>
                        <CardBody>
                          <Stat>
                            <StatLabel>{stat.name}</StatLabel>
                            <StatNumber>{stat.team_count}</StatNumber>
                            <StatHelpText>
                              {percentage}% of total teams ({overview.summary.total_teams})
                            </StatHelpText>
                          </Stat>
                        </CardBody>
                      </Card>
                    );
                  })}
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
