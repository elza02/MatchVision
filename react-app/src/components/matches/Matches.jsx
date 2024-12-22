import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  VStack,
  HStack,
  Text,
  Image,
  Heading,
  useColorModeValue,
  Spinner,
  Alert,
  AlertIcon,
  Select,
  Button,
  Grid,
  GridItem,
  Badge,
  Input,
  Stack,
  Card,
  CardBody,
  Divider,
  IconButton,
} from '@chakra-ui/react';
import { ChevronLeftIcon, ChevronRightIcon } from '@chakra-ui/icons';
import apiService from '../../services/api';

const Matches = () => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState({
    status: '',
    competition: '',
    team: '',
    dateFrom: '',
    dateTo: '',
  });

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    fetchMatches();
  }, [currentPage, filters]);

  const fetchMatches = async () => {
    try {
      setLoading(true);
      let url = `/matches/?page=${currentPage}`;
      
      // Add filters to URL
      if (filters.status) url += `&status=${filters.status}`;
      if (filters.competition) url += `&competition=${filters.competition}`;
      if (filters.team) url += `&team=${filters.team}`;
      if (filters.dateFrom) url += `&date_from=${filters.dateFrom}`;
      if (filters.dateTo) url += `&date_to=${filters.dateTo}`;

      const response = await apiService.get(url);
      setMatches(response.data.results);
      setTotalPages(Math.ceil(response.data.count / 20)); // 20 is page_size from backend
      setError(null);
    } catch (error) {
      console.error('Error fetching matches:', error);
      setError('Failed to load matches. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setCurrentPage(1); // Reset to first page when filters change
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toUpperCase()) {
      case 'SCHEDULED': return 'blue';
      case 'LIVE': return 'green';
      case 'FINISHED': return 'gray';
      case 'POSTPONED': return 'red';
      default: return 'gray';
    }
  };

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
      <VStack spacing={6} align="stretch">
        <Heading size="lg">Matches</Heading>

        {/* Filters */}
        <Stack direction={{ base: 'column', md: 'row' }} spacing={4}>
          <Select
            placeholder="Status"
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
          >
            <option value="SCHEDULED">Scheduled</option>
            <option value="LIVE">Live</option>
            <option value="FINISHED">Finished</option>
            <option value="POSTPONED">Postponed</option>
          </Select>
          <Input
            type="date"
            value={filters.dateFrom}
            onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
            placeholder="From Date"
          />
          <Input
            type="date"
            value={filters.dateTo}
            onChange={(e) => handleFilterChange('dateTo', e.target.value)}
            placeholder="To Date"
          />
        </Stack>

        {/* Matches Grid */}
        <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={6}>
          {matches.map((match) => (
            <GridItem key={match.id}>
              <Card
                bg={bgColor}
                borderWidth="1px"
                borderColor={borderColor}
                borderRadius="lg"
                overflow="hidden"
              >
                <CardBody>
                  <VStack spacing={4}>
                    <HStack justify="space-between" width="100%">
                      <Text fontSize="sm" color="gray.500">
                        {new Date(match.match_date).toLocaleDateString()}
                      </Text>
                      <Badge colorScheme={getStatusColor(match.status)}>
                        {match.status}
                      </Badge>
                    </HStack>

                    <Text fontWeight="bold" color="gray.500">
                      {match.competition_name} - {match.stage}
                    </Text>

                    <Grid templateColumns="1fr auto 1fr" gap={4} width="100%" alignItems="center">
                      {/* Home Team */}
                      <VStack>
                        <Image
                          src={match.home_team_crest}
                          alt={match.home_team_name}
                          boxSize="50px"
                          objectFit="contain"
                          fallbackSrc="https://via.placeholder.com/50"
                        />
                        <Text fontWeight="bold" textAlign="center">
                          {match.home_team_name}
                        </Text>
                      </VStack>

                      {/* Score */}
                      <VStack>
                        <Text fontSize="2xl" fontWeight="bold">
                          {match.status === 'FINISHED' || match.status === 'LIVE'
                            ? `${match.home_team_score} - ${match.away_team_score}`
                            : 'vs'}
                        </Text>
                      </VStack>

                      {/* Away Team */}
                      <VStack>
                        <Image
                          src={match.away_team_crest}
                          alt={match.away_team_name}
                          boxSize="50px"
                          objectFit="contain"
                          fallbackSrc="https://via.placeholder.com/50"
                        />
                        <Text fontWeight="bold" textAlign="center">
                          {match.away_team_name}
                        </Text>
                      </VStack>
                    </Grid>
                  </VStack>
                </CardBody>
              </Card>
            </GridItem>
          ))}
        </Grid>

        {/* Pagination */}
        <HStack justify="center" spacing={4}>
          <IconButton
            icon={<ChevronLeftIcon />}
            onClick={() => handlePageChange(currentPage - 1)}
            isDisabled={currentPage === 1}
            aria-label="Previous page"
          />
          <Text>
            Page {currentPage} of {totalPages}
          </Text>
          <IconButton
            icon={<ChevronRightIcon />}
            onClick={() => handlePageChange(currentPage + 1)}
            isDisabled={currentPage === totalPages}
            aria-label="Next page"
          />
        </HStack>
      </VStack>
    </Container>
  );
};

export default Matches;
