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
  Select,
  Spinner,
  useToast,
  Badge,
  Tooltip,
} from '@chakra-ui/react';
import apiService from '../../services/api';

function Standings({ competitionId, season }) {
  const [standings, setStandings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const toast = useToast();

  useEffect(() => {
    const fetchStandings = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await apiService.getStandings(competitionId, season);
        setStandings(data);
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
      <Box p={4} bg="red.100" color="red.900" borderRadius="md">
        {error}
      </Box>
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
          {standings.map((standing) => (
            <Tr
              key={standing.id}
              _hover={{ bg: 'gray.50' }}
              transition="background-color 0.2s"
            >
              <Td textAlign="center" px={2}>
                <Badge
                  colorScheme={standing.position <= 4 ? 'green' : 
                             standing.position >= standings.length - 3 ? 'red' : 
                             'gray'}
                >
                  {standing.position}
                </Badge>
              </Td>
              <Td>
                <Flex align="center" gap={2}>
                  <Image
                    src={standing.team_crest}
                    alt={standing.team_name}
                    boxSize="24px"
                    objectFit="contain"
                    fallbackSrc="https://via.placeholder.com/24"
                  />
                  <Text fontWeight="medium">{standing.team_name}</Text>
                </Flex>
              </Td>
              <Td isNumeric>{standing.played_games}</Td>
              <Td isNumeric>{standing.won}</Td>
              <Td isNumeric>{standing.draw}</Td>
              <Td isNumeric>{standing.lost}</Td>
              <Td isNumeric>{standing.goals_for}</Td>
              <Td isNumeric>{standing.goals_against}</Td>
              <Td isNumeric>
                <Text color={standing.goal_difference > 0 ? 'green.500' : 
                          standing.goal_difference < 0 ? 'red.500' : 
                          'gray.500'}>
                  {standing.goal_difference > 0 ? '+' : ''}{standing.goal_difference}
                </Text>
              </Td>
              <Td isNumeric fontWeight="bold">{standing.points}</Td>
              <Td>
                <Flex gap={1}>
                  {renderForm(standing.form)}
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
