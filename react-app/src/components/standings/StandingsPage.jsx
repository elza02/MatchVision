import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  Select,
  VStack,
  HStack,
  Text,
  Image,
  Flex,
  Spinner,
  useToast,
} from '@chakra-ui/react';
import apiService from '../../services/api';
import Standings from './Standings';

function StandingsPage() {
  const [competitions, setCompetitions] = useState([]);
  const [selectedCompetition, setSelectedCompetition] = useState('');
  const [selectedSeason, setSelectedSeason] = useState('2023');
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    const fetchCompetitions = async () => {
      try {
        setLoading(true);
        const data = await apiService.getCompetitions();
        setCompetitions(data);
        if (data.length > 0) {
          setSelectedCompetition(data[0].id.toString());
        }
      } catch (error) {
        console.error('Error fetching competitions:', error);
        toast({
          title: 'Error',
          description: 'Failed to fetch competitions',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchCompetitions();
  }, [toast]);

  const selectedCompetitionData = competitions.find(
    c => c.id.toString() === selectedCompetition
  );

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Flex justify="space-between" align="center">
          <Heading size="lg">League Standings</Heading>
          <HStack spacing={4}>
            <Select
              value={selectedCompetition}
              onChange={(e) => setSelectedCompetition(e.target.value)}
              minW="200px"
              isDisabled={loading}
            >
              {competitions.map((competition) => (
                <option key={competition.id} value={competition.id}>
                  {competition.name}
                </option>
              ))}
            </Select>
            <Select
              value={selectedSeason}
              onChange={(e) => setSelectedSeason(e.target.value)}
              minW="120px"
              isDisabled={loading}
            >
              <option value="2023">2023-24</option>
              <option value="2022">2022-23</option>
              <option value="2021">2021-22</option>
            </Select>
          </HStack>
        </Flex>

        {selectedCompetitionData && (
          <Flex align="center" gap={4} bg="gray.50" p={4} borderRadius="md">
            <Image
              src={selectedCompetitionData.emblem}
              alt={selectedCompetitionData.name}
              boxSize="40px"
              objectFit="contain"
            />
            <Box>
              <Text fontSize="lg" fontWeight="bold">
                {selectedCompetitionData.name}
              </Text>
              <Text fontSize="sm" color="gray.600">
                {selectedCompetitionData.area_name} • Season {selectedSeason}
              </Text>
            </Box>
          </Flex>
        )}

        {loading ? (
          <Flex justify="center" py={8}>
            <Spinner size="xl" />
          </Flex>
        ) : (
          <Standings
            competitionId={selectedCompetition}
            season={selectedSeason}
          />
        )}
      </VStack>
    </Container>
  );
}

export default StandingsPage;
