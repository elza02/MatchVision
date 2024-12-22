import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Text,
  VStack,
  useColorModeValue,
  Container,
  Spinner,
  Alert,
  AlertIcon,
  Input,
  InputGroup,
  InputLeftElement,
  Stack,
  Tag,
  Avatar,
} from '@chakra-ui/react';
import { FiSearch } from 'react-icons/fi';
import apiService from '../../services/api';

const Players = () => {
  const [players, setPlayers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        setLoading(true);
        const response = await apiService.getPlayers();
        const validPlayers = (response.data || []).filter(player => player && player.name);
        setPlayers(validPlayers);
        setError(null);
      } catch (error) {
        console.error('Error fetching players:', error);
        setError('Failed to load players. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchPlayers();
  }, []);

  const filteredPlayers = players.filter(player => {
    const searchLower = searchQuery.toLowerCase();
    return (
      player.name.toLowerCase().includes(searchLower) ||
      (player.team_name && player.team_name.toLowerCase().includes(searchLower)) ||
      (player.nationality && player.nationality.toLowerCase().includes(searchLower)) ||
      (player.position && player.position.toLowerCase().includes(searchLower))
    );
  });

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minH="500px">
        <Spinner size="xl" />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert status="error" mt={4}>
        <AlertIcon />
        {error}
      </Alert>
    );
  }

  return (
    <Container maxW="container.xl" py={5}>
      <VStack spacing={5} align="stretch">
        <Stack direction={{ base: 'column', md: 'row' }} justify="space-between" align="center">
          <Heading size="lg">Players ({filteredPlayers.length})</Heading>
          <InputGroup maxW={{ base: "100%", md: "300px" }}>
            <InputLeftElement pointerEvents="none">
              <FiSearch color="gray.300" />
            </InputLeftElement>
            <Input
              placeholder="Search players..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </InputGroup>
        </Stack>

        <Box
          bg={bgColor}
          shadow="md"
          borderRadius="lg"
          borderWidth="1px"
          borderColor={borderColor}
          overflow="auto"
        >
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Name</Th>
                <Th>Team</Th>
                <Th>Position</Th>
                <Th isNumeric>Age</Th>
                <Th>Nationality</Th>
              </Tr>
            </Thead>
            <Tbody>
              {filteredPlayers.map((player) => (
                <Tr key={player.id}>
                  <Td>
                    <Text fontWeight="medium">{player.name || 'Unknown'}</Text>
                  </Td>
                  <Td>
                    <Text>{player.team_name || 'Unknown Team'}</Text>
                  </Td>
                  <Td>
                    <Tag colorScheme={getPositionColor(player.position)}>
                      {player.position || 'Unknown'}
                    </Tag>
                  </Td>
                  <Td isNumeric>
                    {player.age || 'N/A'}
                  </Td>
                  <Td>
                    {player.nationality || 'Unknown'}
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      </VStack>
    </Container>
  );
};

const getPositionColor = (position) => {
  if (!position) return 'gray';
  position = position.toLowerCase();
  if (position.includes('forward') || position.includes('striker')) return 'red';
  if (position.includes('midfielder')) return 'green';
  if (position.includes('defender')) return 'blue';
  if (position.includes('goalkeeper')) return 'yellow';
  return 'gray';
};

export default Players;
