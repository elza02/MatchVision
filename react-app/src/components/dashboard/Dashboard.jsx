import React, { useState, useEffect } from 'react';
import {
  Box,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Icon,
  Flex,
  Text,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Image,
  Badge,
  useColorMode,
  Skeleton,
  Alert,
  AlertIcon,
} from '@chakra-ui/react';
import { FiUsers, FiActivity, FiAward, FiCalendar } from 'react-icons/fi';
import apiService from '../../services/api';

function StatsCard({ title, stat, icon, description }) {
  const { colorMode } = useColorMode();
  
  return (
    <Stat
      px={{ base: 4, md: 8 }}
      py="5"
      shadow="base"
      rounded="lg"
      bg={colorMode === 'light' ? 'white' : 'gray.800'}
    >
      <Flex justifyContent="space-between">
        <Box pl={2}>
          <StatLabel fontWeight="medium" isTruncated>
            {title}
          </StatLabel>
          <StatNumber fontSize="3xl" fontWeight="medium">
            {stat}
          </StatNumber>
          <StatHelpText>{description}</StatHelpText>
        </Box>
        <Box
          my="auto"
          color="brand.500"
          alignContent="center"
        >
          <Icon as={icon} w={8} h={8} />
        </Box>
      </Flex>
    </Stat>
  );
}

function UpcomingMatchesList({ matches, isLoading, error }) {
  const { colorMode } = useColorMode();

  if (error) {
    return (
      <Alert status="error" rounded="md">
        <AlertIcon />
        Failed to load upcoming matches
      </Alert>
    );
  }

  return (
    <Box
      bg={colorMode === 'light' ? 'white' : 'gray.800'}
      rounded="lg"
      shadow="base"
      overflow="hidden"
    >
      <Table size="sm">
        <Thead>
          <Tr>
            <Th>Date</Th>
            <Th>Home Team</Th>
            <Th>Away Team</Th>
            <Th>Competition</Th>
          </Tr>
        </Thead>
        <Tbody>
          {isLoading ? (
            [...Array(5)].map((_, i) => (
              <Tr key={i}>
                <Td><Skeleton height="20px" /></Td>
                <Td><Skeleton height="20px" /></Td>
                <Td><Skeleton height="20px" /></Td>
                <Td><Skeleton height="20px" /></Td>
              </Tr>
            ))
          ) : (
            matches.map((match) => (
              <Tr key={match.id}>
                <Td whiteSpace="nowrap">
                  {new Date(match.match_date).toLocaleDateString()}
                </Td>
                <Td>
                  <Flex align="center" gap={2}>
                    <Image
                      src={match.home_team_crest}
                      alt={match.home_team_name}
                      boxSize="20px"
                      objectFit="contain"
                    />
                    <Text>{match.home_team_name}</Text>
                  </Flex>
                </Td>
                <Td>
                  <Flex align="center" gap={2}>
                    <Image
                      src={match.away_team_crest}
                      alt={match.away_team_name}
                      boxSize="20px"
                      objectFit="contain"
                    />
                    <Text>{match.away_team_name}</Text>
                  </Flex>
                </Td>
                <Td>
                  <Badge colorScheme="brand" variant="subtle">
                    {match.competition_name}
                  </Badge>
                </Td>
              </Tr>
            ))
          )}
        </Tbody>
      </Table>
    </Box>
  );
}

function TopScorersList({ scorers, isLoading, error }) {
  const { colorMode } = useColorMode();

  if (error) {
    return (
      <Alert status="error" rounded="md">
        <AlertIcon />
        Failed to load top scorers
      </Alert>
    );
  }

  return (
    <Box
      bg={colorMode === 'light' ? 'white' : 'gray.800'}
      rounded="lg"
      shadow="base"
      overflow="hidden"
    >
      <Table size="sm">
        <Thead>
          <Tr>
            <Th>Player</Th>
            <Th>Team</Th>
            <Th isNumeric>Goals</Th>
            <Th isNumeric>Assists</Th>
          </Tr>
        </Thead>
        <Tbody>
          {isLoading ? (
            [...Array(5)].map((_, i) => (
              <Tr key={i}>
                <Td><Skeleton height="20px" /></Td>
                <Td><Skeleton height="20px" /></Td>
                <Td><Skeleton height="20px" /></Td>
                <Td><Skeleton height="20px" /></Td>
              </Tr>
            ))
          ) : (
            scorers.map((scorer) => (
              <Tr key={scorer.id}>
                <Td>
                  <Text fontWeight="medium">{scorer.player_name}</Text>
                </Td>
                <Td>
                  <Flex align="center" gap={2}>
                    <Image
                      src={scorer.team_crest}
                      alt={scorer.team_name}
                      boxSize="20px"
                      objectFit="contain"
                    />
                    <Text>{scorer.team_name}</Text>
                  </Flex>
                </Td>
                <Td isNumeric fontWeight="bold" color="brand.500">
                  {scorer.goals}
                </Td>
                <Td isNumeric>{scorer.assists}</Td>
              </Tr>
            ))
          )}
        </Tbody>
      </Table>
    </Box>
  );
}

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [upcomingMatches, setUpcomingMatches] = useState([]);
  const [topScorers, setTopScorers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        const [statsData, matchesData, scorersData] = await Promise.all([
          apiService.getDashboardStats(),
          apiService.getUpcomingMatches(),
          apiService.getTopScorers()
        ]);
        
        setStats(statsData);
        setUpcomingMatches(matchesData);
        setTopScorers(scorersData);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <Box>
      <Heading mb={6}>Dashboard</Heading>
      
      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={{ base: 5, lg: 8 }} mb={8}>
        <StatsCard
          title="Total Teams"
          stat={stats?.total_teams || '-'}
          icon={FiUsers}
          description="Active teams in database"
        />
        <StatsCard
          title="Total Matches"
          stat={stats?.total_matches || '-'}
          icon={FiActivity}
          description="Total matches recorded"
        />
        <StatsCard
          title="Total Players"
          stat={stats?.total_players || '-'}
          icon={FiAward}
          description="Players in database"
        />
        {/* <StatsCard
          title="Next Match"
          stat={upcomingMatches?.[0] ? new Date(upcomingMatches[0].match_date).toLocaleDateString() : '-'}
          icon={FiCalendar}
          description={upcomingMatches?.[0] ? `${upcomingMatches[0].home_team_name} vs ${upcomingMatches[0].away_team_name}` : 'No upcoming matches'}
        /> */}
      </SimpleGrid>

      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
        <Box>
          <Heading size="md" mb={4}>Upcoming Matches</Heading>
          <UpcomingMatchesList
            matches={upcomingMatches}
            isLoading={isLoading}
            error={error}
          />
        </Box>

        <Box>
          <Heading size="md" mb={4}>Top Scorers</Heading>
          <TopScorersList
            scorers={topScorers}
            isLoading={isLoading}
            error={error}
          />
        </Box>
      </SimpleGrid>
    </Box>
  );
}

export default Dashboard;
