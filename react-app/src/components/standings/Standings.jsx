import React, { useState, useEffect } from 'react';
import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Image,
  Text,
  Flex,
  Spinner,
  useToast,
  Badge,
  Alert,
  AlertIcon,
  Icon,
} from '@chakra-ui/react';
import { FaMedal } from 'react-icons/fa';
import apiService from '../../services/api';

function Standings({ competitionId, season }) {
  const [standings, setStandings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const toast = useToast();

  useEffect(() => {
    const fetchStandings = async () => {
      if (!competitionId || !season) return;
      
      try {
        setLoading(true);
        setError(null);
        const response = await apiService.getStandings(competitionId, season);
        if (response?.standings && Array.isArray(response.standings)) {
          // Sort standings by position
          const sortedStandings = response.standings.sort((a, b) => a.position - b.position);
          setStandings(sortedStandings);
        } else {
          setError('No standings data available');
        }
      } catch (error) {
        console.error('Error fetching standings:', error);
        setError(error.message || 'Failed to fetch standings');
        toast({
          title: 'Error',
          description: error.message || 'Failed to fetch standings',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStandings();
  }, [competitionId, season, toast]);

  const getFormBadgeColor = (result) => {
    switch (result) {
      case 'W': return 'green';
      case 'D': return 'yellow';
      case 'L': return 'red';
      default: return 'gray';
    }
  };

  const getMedalColor = (position) => {
    switch (position) {
      case 1: return 'gold';
      case 2: return 'silver';
      case 3: return '#CD7F32'; // bronze
      default: return null;
    }
  };

  const renderForm = (form) => {
    if (!form) return null;
    return form.split(',').map((result, index) => (
      <Badge
        key={index}
        colorScheme={getFormBadgeColor(result)}
        mr={1}
        fontSize="xs"
      >
        {result}
      </Badge>
    ));
  };

  if (loading) {
    return (
      <Flex justify="center" align="center" h="200px">
        <Spinner size="xl" color="blue.500" />
      </Flex>
    );
  }

  if (error) {
    return (
      <Alert status="error" borderRadius="md">
        <AlertIcon />
        {error}
      </Alert>
    );
  }

  if (!standings || standings.length === 0) {
    return (
      <Alert status="info" borderRadius="md">
        <AlertIcon />
        No standings data available for this competition and season
      </Alert>
    );
  }

  return (
    <Box overflowX="auto" shadow="lg" borderRadius="lg" bg="white">
      <Table variant="simple" size="sm">
        <Thead bg="gray.50">
          <Tr>
            <Th textAlign="center" px={2} width="40px">Pos</Th>
            <Th>Team</Th>
            <Th isNumeric>MP</Th>
            <Th isNumeric>W</Th>
            <Th isNumeric>D</Th>
            <Th isNumeric>L</Th>
            <Th isNumeric>GF</Th>
            <Th isNumeric>GA</Th>
            <Th isNumeric>GD</Th>
            <Th isNumeric>Pts</Th>
            <Th>Form</Th>
          </Tr>
        </Thead>
        <Tbody>
          {standings.map((team) => (
            <Tr key={team.id}>
              <Td textAlign="center">
                <Flex align="center" justify="center" gap={1}>
                  <Badge
                    colorScheme={team.position <= 4 ? 'green' : 
                              team.position >= standings.length - 3 ? 'red' : 
                              'gray'}
                  >
                    {team.position}
                  </Badge>
                  {team.position <= 3 && (
                    <Icon
                      as={FaMedal}
                      color={getMedalColor(team.position)}
                      w={4}
                      h={4}
                    />
                  )}
                </Flex>
              </Td>
              <Td>
                <Flex align="center" gap={2}>
                  <Image
                    src={team?.team_crest}
                    alt={team?.name}
                    boxSize="24px"
                    objectFit="contain"
                    fallbackSrc="https://via.placeholder.com/24"
                  />
                  <Text fontWeight="medium">{team?.team_name}</Text>
                </Flex>
              </Td>
              <Td isNumeric>{team.played_games}</Td>
              <Td isNumeric>{team.won}</Td>
              <Td isNumeric>{team.draw}</Td>
              <Td isNumeric>{team.lost}</Td>
              <Td isNumeric>{team.goals_for}</Td>
              <Td isNumeric>{team.goals_against}</Td>
              <Td isNumeric>
                <Text color={team.goal_difference > 0 ? 'green.500' : 
                          team.goal_difference < 0 ? 'red.500' : 
                          'gray.500'}>
                  {team.goal_difference > 0 ? '+' : ''}{team.goal_difference}
                </Text>
              </Td>
              <Td isNumeric fontWeight="bold">{team.points}</Td>
              <Td>
                <Flex gap={1}>
                  {renderForm(team.form)}
                </Flex>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
}

export default Standings;
