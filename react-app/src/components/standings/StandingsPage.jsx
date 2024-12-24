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
  Alert,
  AlertIcon,
} from '@chakra-ui/react';
import apiService from '../../services/api';
import Standings from './Standings';

function StandingsPage() {
  const [competitions, setCompetitions] = useState([]);
  const [selectedCompetition, setSelectedCompetition] = useState('');
  const [selectedSeason, setSelectedSeason] = useState('2023');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const toast = useToast();

  useEffect(() => {
    const fetchCompetitions = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiService.getCompetitions();
        // Filter out competitions with null names
        const validCompetitions = response.filter(comp => comp.name != null);
        setCompetitions(validCompetitions);
        if (validCompetitions.length > 0) {
          setSelectedCompetition(validCompetitions[0].id.toString());
        }
      } catch (error) {
        console.error('Error fetching competitions:', error);
        setError('Failed to fetch competitions');
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

  const selectedCompetitionData = selectedCompetition
    ? competitions.find(c => c.id.toString() === selectedCompetition)
    : null;

  if (loading) {
    return (
      <Container maxW="container.xl" py={8}>
        <Flex justify="center" align="center" minH="400px">
          <Spinner size="xl" />
        </Flex>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxW="container.xl" py={8}>
        <Alert status="error">
          <AlertIcon />
          {error}
        </Alert>
      </Container>
    );
  }

  if (competitions.length === 0) {
    return (
      <Container maxW="container.xl" py={8}>
        <Alert status="info">
          <AlertIcon />
          No competitions available
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Flex justify="space-between" align="center" wrap="wrap" gap={4}>
          <Heading size="lg">League Standings</Heading>
          <HStack spacing={4} flexWrap="wrap">
            <Select
              value={selectedCompetition}
              onChange={(e) => setSelectedCompetition(e.target.value)}
              minW="200px"
              isDisabled={loading || competitions.length === 0}
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
              fallbackSrc="https://via.placeholder.com/40"
            />
            <Box>
              <Text fontSize="lg" fontWeight="bold">
                {selectedCompetitionData.name}
              </Text>
              <Text fontSize="sm" color="gray.600">
                {selectedCompetitionData.area_name || 'Unknown Area'} • Season {selectedSeason}
              </Text>
            </Box>
          </Flex>
        )}

        {selectedCompetition && selectedSeason && (
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
