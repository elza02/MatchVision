import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardBody,
  Stack,
  Heading,
  Text,
  SimpleGrid,
  Select,
  HStack,
  Badge,
  Button,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Progress,
  Spinner,
  useToast,
  Center,
  Alert,
  AlertIcon,
} from '@chakra-ui/react';
import api from '../../services/api';
import { pollingService } from '../../services/polling';
import MatchDetail from './MatchDetail';
import InfiniteScroll from 'react-infinite-scroll-component';

function Matches() {
  const [matches, setMatches] = useState([]);
  const [competitions, setCompetitions] = useState([]);
  const [selectedCompetition, setSelectedCompetition] = useState('');
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();
  const PAGE_SIZE = 12;

  const fetchData = useCallback(async (pageNum = 1, append = false) => {
    try {
      setError(null);
      if (pageNum === 1) {
        setLoading(true);
        setHasMore(true);
      } else {
        setIsLoadingMore(true);
      }

      // Fetch competitions if needed
      if (!competitions || competitions.length === 0) {
        const competitionsResponse = await api.get('/competitions/');
        const competitionsData = competitionsResponse.data;
        setCompetitions(competitionsData);
        if (!selectedCompetition && competitionsData.length > 0) {
          setSelectedCompetition(competitionsData[0].id.toString());
        }
      }

      // Fetch matches with pagination
      const matchesUrl = `/matches/?page=${pageNum}&page_size=${PAGE_SIZE}${
        selectedCompetition ? `&competition=${selectedCompetition}` : ''
      }`;
      
      const matchesResponse = await api.get(matchesUrl);
      const matchesData = matchesResponse.data;
      
      // Validate response data
      if (!matchesData || typeof matchesData !== 'object') {
        throw new Error('Invalid response data');
      }

      // Extract results and pagination info
      const results = Array.isArray(matchesData.results) ? matchesData.results : [];
      const hasNextPage = !!matchesData.next;
      
      // Update matches state based on whether we're appending or replacing
      setMatches(prev => append ? [...prev, ...results] : results);
      setHasMore(hasNextPage);
      setPage(pageNum);

    } catch (err) {
      console.error('Error fetching data:', err);
      const errorMessage = err.response?.data?.message || err.message || 'Failed to fetch data';
      setError(errorMessage);
      toast({
        title: 'Error',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      setHasMore(false);
    } finally {
      setLoading(false);
      setIsLoadingMore(false);
    }
  }, [selectedCompetition, competitions, toast]);

  useEffect(() => {
    fetchData(1, false);
  }, [fetchData]);

  const handleCompetitionChange = (event) => {
    setSelectedCompetition(event.target.value);
    setPage(1);
    setMatches([]);
    setHasMore(true);
    fetchData(1, false);
  };

  const loadMore = useCallback(() => {
    if (!loading && !isLoadingMore && hasMore) {
      fetchData(page + 1, true);
    }
  }, [loading, isLoadingMore, hasMore, page, fetchData]);

  const handleMatchClick = useCallback((match) => {
    setSelectedMatch(match);
    onOpen();
  }, [onOpen]);

  if (loading && (!matches || matches.length === 0)) {
    return (
      <Center h="calc(100vh - 100px)">
        <Spinner size="xl" color="brand.500" />
      </Center>
    );
  }

  if (error && (!matches || matches.length === 0)) {
    return (
      <Alert status="error" variant="subtle" flexDirection="column" alignItems="center" justifyContent="center" textAlign="center" height="200px">
        <AlertIcon boxSize="40px" mr={0} />
        <Text mt={4} mb={1} fontSize="lg">
          Error loading matches
        </Text>
        <Text mb={4}>{error}</Text>
        <Button onClick={() => fetchData(1, false)} colorScheme="red" variant="outline">
          Try Again
        </Button>
      </Alert>
    );
  }

  return (
    <Box p={4}>
      <Stack spacing={4}>
        <HStack justify="space-between" align="center">
          <Heading size="lg">Matches</Heading>
          <Select
            placeholder="All Competitions"
            value={selectedCompetition}
            onChange={handleCompetitionChange}
            maxW="300px"
            isDisabled={loading}
          >
            {competitions?.map(competition => (
              <option key={competition.id} value={competition.id}>
                {competition.name}
              </option>
            ))}
          </Select>
        </HStack>

        <InfiniteScroll
          dataLength={matches?.length || 0}
          next={loadMore}
          hasMore={hasMore}
          loader={
            <Center p={4}>
              <Spinner />
            </Center>
          }
          endMessage={
            matches?.length > 0 ? (
              <Text textAlign="center" color="gray.500" p={4}>
                No more matches to load
              </Text>
            ) : null
          }
          scrollThreshold={0.8}
        >
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
            {matches?.map(match => (
              <Card 
                key={match.id} 
                cursor="pointer" 
                onClick={() => handleMatchClick(match)}
                _hover={{ transform: 'translateY(-2px)', shadow: 'lg' }}
                transition="all 0.2s"
              >
                <CardBody>
                  <Stack spacing={4}>
                    <Badge 
                      colorScheme={match.status === 'FINISHED' ? 'green' : 'yellow'} 
                      alignSelf="start"
                    >
                      {match.status || 'Unknown'}
                    </Badge>
                    <Stack spacing={2}>
                      <Text fontWeight="bold">{match.home_team?.name || 'Unknown Team'}</Text>
                      <Text fontSize="sm" color="gray.500">vs</Text>
                      <Text fontWeight="bold">{match.away_team?.name || 'Unknown Team'}</Text>
                    </Stack>
                    <Text color="gray.500">
                      {match.match_date ? new Date(match.match_date).toLocaleDateString() : 'Date not available'}
                    </Text>
                    {(match.home_team_score !== null && match.away_team_score !== null) ? (
                      <Text fontWeight="bold">
                        {match.home_team_score} - {match.away_team_score}
                      </Text>
                    ) : (
                      <Text color="gray.500">Score not available</Text>
                    )}
                  </Stack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        </InfiniteScroll>
      </Stack>

      {selectedMatch && (
        <Modal isOpen={isOpen} onClose={onClose} size="4xl" scrollBehavior="inside">
          <ModalOverlay />
          <ModalContent maxW="1000px">
            <ModalHeader>
              {selectedMatch.home_team?.name} vs {selectedMatch.away_team?.name}
            </ModalHeader>
            <ModalCloseButton />
            <ModalBody pb={6}>
              <MatchDetail match={selectedMatch} />
            </ModalBody>
          </ModalContent>
        </Modal>
      )}
    </Box>
  );
}

export default Matches;
