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
  Image,
} from '@chakra-ui/react';
import axios from 'axios';

const Players = () => {
  const [players, setPlayers] = useState([]);
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/players/`);
        setPlayers(response.data);
      } catch (error) {
        console.error('Error fetching players:', error);
      }
    };

    fetchPlayers();
  }, []);

  return (
    <Container maxW="container.xl" py={5}>
      <VStack spacing={5} align="stretch">
        <Heading size="lg" mb={4}>
          Players
        </Heading>
        <Box
          bg={bgColor}
          shadow="md"
          borderRadius="lg"
          borderWidth="1px"
          borderColor={borderColor}
          overflow="hidden"
        >
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Name</Th>
                <Th>Team</Th>
                <Th>Position</Th>
                <Th>Age</Th>
                <Th>Nationality</Th>
              </Tr>
            </Thead>
            <Tbody>
              {players.map((player) => (
                <Tr key={player.id}>
                  <Td>
                    <Text fontWeight="medium">{player.name}</Text>
                  </Td>
                  <Td>{player.team}</Td>
                  <Td>{player.position}</Td>
                  <Td>{player.age}</Td>
                  <Td>{player.nationality}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      </VStack>
    </Container>
  );
};

export default Players;
