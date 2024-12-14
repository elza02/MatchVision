import { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Heading,
  Text,
  Stat,
  StatLabel,
  StatNumber,
  StatGroup,
  Card,
  CardBody,
  Badge,
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
  Progress,
  HStack,
  VStack,
  Spinner,
  useToast,
} from '@chakra-ui/react';
import api from '../../services/api';

const MatchStats = ({ stats }) => (
  <StatGroup>
    <Stat>
      <StatLabel>Goals</StatLabel>
      <StatNumber>{stats.goals}</StatNumber>
    </Stat>
    <Stat>
      <StatLabel>Assists</StatLabel>
      <StatNumber>{stats.assists}</StatNumber>
    </Stat>
  </StatGroup>
);

const Formation = ({ formation }) => {
  if (!formation) return null;
  
  return (
    <Box>
      <Text fontWeight="bold" mb={2}>Formation: {formation.formation}</Text>
      <Grid templateColumns="repeat(auto-fit, minmax(150px, 1fr))" gap={4}>
        {Object.entries(formation.players).map(([position, players]) => (
          <Box key={position}>
            <Text fontWeight="semibold">{position}</Text>
            {players.map((player, index) => (
              <Text key={index} fontSize="sm">{player}</Text>
            ))}
          </Box>
        ))}
      </Grid>
    </Box>
  );
};

const TopPerformers = ({ performers }) => (
  <Table size="sm">
    <Thead>
      <Tr>
        <Th>Player</Th>
        <Th isNumeric>Goals</Th>
        <Th isNumeric>Assists</Th>
      </Tr>
    </Thead>
    <Tbody>
      {performers.map((player, index) => (
        <Tr key={index}>
          <Td>{player.name}</Td>
          <Td isNumeric>{player.goals}</Td>
          <Td isNumeric>{player.assists}</Td>
        </Tr>
      ))}
    </Tbody>
  </Table>
);

const Predictions = ({ predictions, odds }) => {
  if (!predictions && !odds) return null;

  return (
    <Card>
      <CardBody>
        <VStack spacing={4} align="stretch">
          {predictions && (
            <Box>
              <Heading size="sm" mb={2}>Match Predictions</Heading>
              <HStack spacing={4}>
                <VStack>
                  <Text>Home Win</Text>
                  <Progress
                    value={predictions.home_team_win_prob * 100}
                    size="lg"
                    width="100px"
                    colorScheme="green"
                  />
                  <Text>{(predictions.home_team_win_prob * 100).toFixed(1)}%</Text>
                </VStack>
                <VStack>
                  <Text>Draw</Text>
                  <Progress
                    value={predictions.draw_prob * 100}
                    size="lg"
                    width="100px"
                    colorScheme="yellow"
                  />
                  <Text>{(predictions.draw_prob * 100).toFixed(1)}%</Text>
                </VStack>
                <VStack>
                  <Text>Away Win</Text>
                  <Progress
                    value={predictions.away_team_win_prob * 100}
                    size="lg"
                    width="100px"
                    colorScheme="blue"
                  />
                  <Text>{(predictions.away_team_win_prob * 100).toFixed(1)}%</Text>
                </VStack>
              </HStack>
              <Text mt={2}>Predicted Score: {predictions.predicted_score}</Text>
            </Box>
          )}
          
          {odds && (
            <Box>
              <Heading size="sm" mb={2}>Betting Odds</Heading>
              <HStack spacing={4} justify="space-around">
                <VStack>
                  <Badge colorScheme="green">{odds.home_win_odds}</Badge>
                  <Text>Home Win</Text>
                </VStack>
                <VStack>
                  <Badge colorScheme="yellow">{odds.draw_odds}</Badge>
                  <Text>Draw</Text>
                </VStack>
                <VStack>
                  <Badge colorScheme="blue">{odds.away_win_odds}</Badge>
                  <Text>Away Win</Text>
                </VStack>
              </HStack>
            </Box>
          )}
        </VStack>
      </CardBody>
    </Card>
  );
};

const HeadToHead = ({ matches }) => (
  <Table size="sm">
    <Thead>
      <Tr>
        <Th>Date</Th>
        <Th>Home Team</Th>
        <Th>Score</Th>
        <Th>Away Team</Th>
      </Tr>
    </Thead>
    <Tbody>
      {matches.map((match) => (
        <Tr key={match.id}>
          <Td>{new Date(match.match_date).toLocaleDateString()}</Td>
          <Td>{match.home_team}</Td>
          <Td>{match.home_team_score} - {match.away_team_score}</Td>
          <Td>{match.away_team}</Td>
        </Tr>
      ))}
    </Tbody>
  </Table>
);

const MatchDetail = ({ match }) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const toast = useToast();

  useEffect(() => {
    if (match?.id) {
      fetchMatchAnalysis();
    }
  }, [match?.id]);

  const fetchMatchAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get(`/matches/${match.id}/match_analysis/`);
      setAnalysis(response.data);
    } catch (error) {
      console.error('Error fetching match analysis:', error);
      const errorMessage = error.response?.data?.message || error.message || 'Failed to fetch match analysis';
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

  if (!match) {
    return (
      <Box p={4} textAlign="center">
        <Text>No match data available</Text>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box p={4} textAlign="center">
        <Spinner size="xl" />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={4} textAlign="center">
        <Text color="red.500">{error}</Text>
      </Box>
    );
  }

  return (
    <Box>
      <VStack spacing={6} align="stretch">
        {/* Match Header */}
        <Box textAlign="center">
          <Heading size="md" mb={2}>
            {match.home_team} vs {match.away_team}
          </Heading>
          <Text color="gray.500">
            {match.match_date ? new Date(match.match_date).toLocaleDateString() : 'Date not available'}
          </Text>
          {match.status && (
            <Badge 
              colorScheme={match.status === 'FINISHED' ? 'green' : 'yellow'} 
              mt={2}
            >
              {match.status}
            </Badge>
          )}
          {(match.home_team_score !== null && match.away_team_score !== null) && (
            <Heading size="lg" mt={2}>
              {match.home_team_score} - {match.away_team_score}
            </Heading>
          )}
        </Box>

        {/* Match Analysis Tabs */}
        <Tabs isFitted variant="enclosed">
          <TabList>
            <Tab>Stats</Tab>
            <Tab>Formations</Tab>
            <Tab>Top Performers</Tab>
            <Tab>Predictions</Tab>
            <Tab>Head to Head</Tab>
          </TabList>

          <TabPanels>
            <TabPanel>
              {analysis?.stats ? (
                <MatchStats stats={analysis.stats} />
              ) : (
                <Text textAlign="center">No stats available</Text>
              )}
            </TabPanel>

            <TabPanel>
              <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4}>
                <Box>
                  <Heading size="sm" mb={2}>Home Team</Heading>
                  {analysis?.formations?.home_team ? (
                    <Formation formation={analysis.formations.home_team} />
                  ) : (
                    <Text>No formation data available</Text>
                  )}
                </Box>
                <Box>
                  <Heading size="sm" mb={2}>Away Team</Heading>
                  {analysis?.formations?.away_team ? (
                    <Formation formation={analysis.formations.away_team} />
                  ) : (
                    <Text>No formation data available</Text>
                  )}
                </Box>
              </Grid>
            </TabPanel>

            <TabPanel>
              {analysis?.top_performers?.length > 0 ? (
                <TopPerformers performers={analysis.top_performers} />
              ) : (
                <Text textAlign="center">No top performers data available</Text>
              )}
            </TabPanel>

            <TabPanel>
              <Predictions 
                predictions={analysis?.predictions} 
                odds={analysis?.betting_odds}
              />
            </TabPanel>

            <TabPanel>
              {analysis?.head_to_head?.length > 0 ? (
                <HeadToHead matches={analysis.head_to_head} />
              ) : (
                <Text textAlign="center">No head to head data available</Text>
              )}
            </TabPanel>
          </TabPanels>
        </Tabs>
      </VStack>
    </Box>
  );
};

export default MatchDetail;
