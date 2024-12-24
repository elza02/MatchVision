import React, { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Heading,
  SimpleGrid,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Card,
  CardHeader,
  CardBody,
  Text,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  useColorMode,
  Flex,
  Icon,
  Skeleton,
  Alert,
  AlertIcon,
  Select,
  Center,
} from '@chakra-ui/react';
import { FiUsers, FiActivity, FiAward, FiTrendingUp } from 'react-icons/fi';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';
import { PieChart, Pie, Cell } from 'recharts';
import apiService from '../../services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28'];

function OverviewCard({ title, stat, trend, icon, description }) {
  const { colorMode } = useColorMode();
  return (
    <Stat
      px={{ base: 4, md: 8 }}
      py={5}
      shadow="base"
      rounded="lg"
      bg={colorMode === 'light' ? 'white' : 'gray.800'}
    >
      <Flex justifyContent="space-between">
        <Box pl={2}>
          <StatLabel fontWeight="medium" isTruncated>
            {title}
          </StatLabel>
          <StatNumber fontSize="2xl" fontWeight="medium">
            {stat}
          </StatNumber>
          <StatHelpText mb={0}>
            {description}
          </StatHelpText>
        </Box>
        <Box p={2}>
          <Icon as={icon} w={8} h={8} />
        </Box>
      </Flex>
    </Stat>
  );
}

function Analytics() {
  const [tabIndex, setTabIndex] = useState(0);
  const [overview, setOverview] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [teams, setTeams] = useState([]);
  const [teamAnalytics, setTeamAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { colorMode } = useColorMode();

  useEffect(() => {
    fetchOverview();
    fetchTeams();
  }, []);

  const fetchOverview = async () => {
    try {
      const response = await apiService.getAnalyticsOverview();
      setOverview(response);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError('Failed to load analytics data');
      setLoading(false);
    }
  };

  const fetchTeams = async () => {
    try {
      const response = await apiService.getTeams();
      if (response?.data?.results) {
        setTeams(response.data.results);
      }
    } catch (err) {
      console.error('Error fetching teams:', err);
      setTeams([]);
    }
  };

  const fetchTeamAnalytics = async (teamId) => {
    try {
      setLoading(true);
      const response = await apiService.getTeamAnalytics(teamId);
      setTeamAnalytics(response);
    } catch (err) {
      console.error('Error fetching team analytics:', err);
      setError('Failed to load team analytics');
    } finally {
      setLoading(false);
    }
  };

  const renderMatchStatusPieChart = () => {
    if (!overview?.summary?.matches_by_status) return null;

    const chartData = [
      { name: 'Finished', value: overview.summary.matches_by_status.finished },
      { name: 'Scheduled', value: overview.summary.matches_by_status.scheduled },
      { name: 'Other', value: overview.summary.matches_by_status.other },
    ];

    return (
      <Card>
        <CardHeader>
          <Heading size="md">Match Status Distribution</Heading>
        </CardHeader>
        <CardBody>
          <Box height="300px">
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip formatter={(value) => [value, 'Matches']} />
              </PieChart>
            </ResponsiveContainer>
          </Box>
        </CardBody>
      </Card>
    );
  };

  if (loading && !overview) {
    return (
      <Container maxW="container.xl" p={4}>
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} height="200px" />
          ))}
        </SimpleGrid>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxW="container.xl" p={4}>
        <Alert status="error">
          <AlertIcon />
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxW="container.xl" p={4}>
      <Tabs index={tabIndex} onChange={setTabIndex}>
        <TabList mb={4}>
          <Tab>Overview</Tab>
          <Tab>Teams</Tab>
          <Tab>Players</Tab>
        </TabList>

        <TabPanels>
          <TabPanel p={0}>
            {overview && (
              <>
                <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mb={6}>
                  <OverviewCard
                    title="Total Teams"
                    stat={overview.summary.total_teams}
                    icon={FiUsers}
                    description="Active teams"
                  />
                  <OverviewCard
                    title="Total Matches"
                    stat={overview.summary.matches_by_status.total}
                    icon={FiActivity}
                    description={`${overview.summary.matches_by_status.finished} finished matches`}
                  />
                  <OverviewCard
                    title="Total Goals"
                    stat={overview.summary.total_goals}
                    icon={FiAward}
                    description={`Avg ${overview.summary.average_goals_per_match} per match`}
                  />
                  <OverviewCard
                    title="Goals Trend"
                    stat={overview.goals_trend?.[overview.goals_trend.length - 1]?.average_goals || '-'}
                    icon={FiTrendingUp}
                    description="Average goals per match"
                  />
                </SimpleGrid>

                <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6} mb={6}>
                  {renderMatchStatusPieChart()}
                  <Card>
                    <CardHeader>
                      <Heading size="md">Goals Trend</Heading>
                    </CardHeader>
                    <CardBody>
                      <Box height="300px">
                        <ResponsiveContainer>
                          <LineChart data={overview.goals_trend}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="matchday" />
                            <YAxis />
                            <RechartsTooltip />
                            <Line
                              type="monotone"
                              dataKey="average_goals"
                              stroke="#8884d8"
                              strokeWidth={2}
                              dot={false}
                            />
                          </LineChart>
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
                value={selectedTeam || ''}
                onChange={(e) => {
                  const value = parseInt(e.target.value);
                  setSelectedTeam(value);
                  fetchTeamAnalytics(value);
                }}
                placeholder="Select a team"
                isDisabled={!teams || teams.length === 0}
              >
                {teams.map((team) => (
                  <option key={team.id} value={team.id}>
                    {team.name}
                  </option>
                ))}
              </Select>
            </Box>

            {loading && <Center p={8}><Skeleton height="200px" /></Center>}

            {teamAnalytics && !loading && (
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                <Card>
                  <CardHeader>
                    <Heading size="md">Team Summary</Heading>
                  </CardHeader>
                  <CardBody>
                    <SimpleGrid columns={2} spacing={4}>
                      <Stat>
                        <StatLabel>Matches</StatLabel>
                        <StatNumber>{teamAnalytics.summary?.total_matches || 0}</StatNumber>
                      </Stat>
                      <Stat>
                        <StatLabel>Points</StatLabel>
                        <StatNumber>{teamAnalytics.summary?.points || 0}</StatNumber>
                        <StatHelpText>
                          Avg: {teamAnalytics.summary?.average_points || 0} per match
                        </StatHelpText>
                      </Stat>
                      <Stat>
                        <StatLabel>Record</StatLabel>
                        <StatNumber>
                          {teamAnalytics.summary?.wins || 0}W-{teamAnalytics.summary?.draws || 0}D-{teamAnalytics.summary?.losses || 0}L
                        </StatNumber>
                      </Stat>
                      <Stat>
                        <StatLabel>Goals</StatLabel>
                        <StatNumber>
                          {teamAnalytics.summary?.goals_for || 0}-{teamAnalytics.summary?.goals_against || 0}
                        </StatNumber>
                        <StatHelpText>
                          Diff: {teamAnalytics.summary?.goal_difference || 0}
                        </StatHelpText>
                      </Stat>
                    </SimpleGrid>
                  </CardBody>
                </Card>

                {teamAnalytics.performance && (
                  <Card>
                    <CardHeader>
                      <Heading size="md">Points Progression</Heading>
                    </CardHeader>
                    <CardBody>
                      <Box height="300px">
                        <ResponsiveContainer>
                          <LineChart data={teamAnalytics.performance}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis 
                              dataKey="match_date" 
                              tickFormatter={(value) => new Date(value).toLocaleDateString()}
                            />
                            <YAxis />
                            <RechartsTooltip 
                              labelFormatter={(value) => new Date(value).toLocaleDateString()}
                            />
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
                )}
              </SimpleGrid>
            )}
          </TabPanel>
          <TabPanel>
            <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
              <Card>
                <CardHeader>
                  <Heading size="md">Goals Distribution</Heading>
                  <Text mt={2} color="gray.600">Distribution of players by goals scored</Text>
                </CardHeader>
                <CardBody>
                  <Box height="300px">
                    <ResponsiveContainer>
                      <PieChart>
                        <Pie
                          data={overview.scorer_stats.goals_distribution}
                          dataKey="value"
                          nameKey="name"
                          cx="50%"
                          cy="50%"
                          outerRadius={100}
                          label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                        >
                          {overview.scorer_stats.goals_distribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <RechartsTooltip formatter={(value) => [`${value} players`]} />
                      </PieChart>
                    </ResponsiveContainer>
                  </Box>
                </CardBody>
              </Card>

              <Card>
                <CardHeader>
                  <Heading size="md">Player Performance Types</Heading>
                  <Text mt={2} color="gray.600">Classification of players by their impact</Text>
                </CardHeader>
                <CardBody>
                  <Box height="300px">
                    <ResponsiveContainer>
                      <PieChart>
                        <Pie
                          data={overview.scorer_stats.performance_types}
                          dataKey="value"
                          nameKey="name"
                          cx="50%"
                          cy="50%"
                          outerRadius={100}
                          label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                        >
                          {overview.scorer_stats.performance_types.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <RechartsTooltip formatter={(value) => [`${value} players`]} />
                      </PieChart>
                    </ResponsiveContainer>
                  </Box>
                </CardBody>
              </Card>
            </SimpleGrid>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Container>
  );
}

export default Analytics;
