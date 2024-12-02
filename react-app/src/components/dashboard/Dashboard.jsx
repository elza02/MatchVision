import { useState, useEffect } from 'react';
import {
  Box,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Card,
  CardBody,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Progress,
  Select,
  HStack,
  Text,
  Flex,
  Icon,
  Spinner,
  useToast,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react';
import { FiActivity, FiAward, FiBarChart2, FiTarget } from 'react-icons/fi';
import api from '../../services/api';

const StatCard = ({ title, value, icon }) => (
  <Card>
    <CardBody>
      <Stat>
        <HStack spacing={4}>
          <Box>
            <StatLabel>{title}</StatLabel>
            <StatNumber>{value}</StatNumber>
          </Box>
          <Icon as={icon} boxSize={8} color="brand.500" />
        </HStack>
      </Stat>
    </CardBody>
  </Card>
);

const TopScorersTable = ({ data = [] }) => (
  <Table size="sm">
    <Thead>
      <Tr>
        <Th>Player</Th>
        <Th isNumeric>Goals</Th>
      </Tr>
    </Thead>
    <Tbody>
      {data.map((scorer, index) => (
        <Tr key={index}>
          <Td>{scorer.player_name}</Td>
          <Td isNumeric>{scorer.goals}</Td>
        </Tr>
      ))}
    </Tbody>
  </Table>
);

const TeamStatsTable = ({ data = [], statKey, label }) => (
  <Box>
    <Text fontWeight="bold" mb={2}>{label}</Text>
    {data.map((team, index) => (
      <HStack key={index} justify="space-between" mb={2}>
        <Text>{team.team.name}</Text>
        <Badge colorScheme={statKey === 'total_goals' ? 'green' : 'red'}>
          {team[statKey]}
        </Badge>
      </HStack>
    ))}
  </Box>
);

const Dashboard = () => {
  const [selectedCompetition, setSelectedCompetition] = useState('');
  const [competitions, setCompetitions] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const toast = useToast();

  useEffect(() => {
    fetchCompetitions();
  }, []);

  useEffect(() => {
    if (selectedCompetition) {
      fetchCompetitionStats();
    }
  }, [selectedCompetition]);

  const fetchCompetitions = async () => {
    try {
      setError(null);
      setLoading(true);
      console.log('Fetching competitions...');
      const response = await api.get('/competitions/');
      console.log('Competitions response:', response.data);
      
      if (response.data && response.data.length > 0) {
        setCompetitions(response.data);
        console.log('Setting initial competition:', response.data[0].id);
        setSelectedCompetition(response.data[0].id);
      } else {
        throw new Error('No competitions found');
      }
    } catch (err) {
      console.error('Error fetching competitions:', err);
      const errorMessage = err.message || 'Failed to fetch competitions';
      setError(errorMessage);
      toast({
        title: 'Error',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchCompetitionStats = async () => {
    if (!selectedCompetition) return;
    
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching stats for competition:', selectedCompetition);
      
      const response = await api.get(`/competitions/${selectedCompetition}/statistics/`);
      console.log('Competition stats response:', response.data);
      
      if (response.data) {
        setStats(response.data);
      } else {
        throw new Error('No statistics available for this competition');
      }
    } catch (err) {
      console.error('Error fetching competition stats:', err);
      const errorMessage = err.message || 'Failed to fetch statistics';
      setError(errorMessage);
      toast({
        title: 'Error',
        description: errorMessage,
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
      <Flex justify="center" align="center" minH="500px">
        <Spinner size="xl" />
      </Flex>
    );
  }

  if (error) {
    return (
      <Box p={4}>
        <Alert status="error">
          <AlertIcon />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </Box>
    );
  }

  if (!stats) {
    return (
      <Box p={4}>
        <Alert status="info">
          <AlertIcon />
          <AlertDescription>No statistics available</AlertDescription>
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={4}>
      <HStack spacing={4} mb={6}>
        <Heading size="lg">Competition Dashboard</Heading>
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
      </HStack>

      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4} mb={8}>
        <StatCard
          title="Total Matches"
          value={stats.total_matches}
          icon={FiBarChart2}
        />
        <StatCard
          title="Goals Scored"
          value={stats.goals_scored}
          icon={FiTarget}
        />
        <StatCard
          title="Avg Goals/Match"
          value={stats.avg_goals_per_match}
          icon={FiActivity}
        />
        <StatCard
          title="Matches Played"
          value={stats.matches_played}
          icon={FiAward}
        />
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
        {stats.top_scorers && (
          <Card>
            <CardBody>
              <Heading size="md" mb={4}>Top Scorers</Heading>
              <TopScorersTable data={stats.top_scorers} />
            </CardBody>
          </Card>
        )}

        <Card>
          <CardBody>
            <Heading size="md" mb={4}>Team Statistics</Heading>
            <SimpleGrid columns={2} spacing={4}>
              <TeamStatsTable
                data={stats.team_stats.most_goals}
                statKey="total_goals"
                label="Most Goals"
              />
              <TeamStatsTable
                data={stats.team_stats.best_defense}
                statKey="goals_conceded"
                label="Best Defense"
              />
            </SimpleGrid>
          </CardBody>
        </Card>
      </SimpleGrid>
    </Box>
  );
};

export default Dashboard;
