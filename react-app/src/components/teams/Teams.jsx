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
  Input,
  InputGroup,
  InputLeftElement,
  Grid,
  GridItem,
  Stack,
  Card,
  CardBody,
  IconButton,
  Badge,
  Stat,
  StatLabel,
  StatNumber,
  Divider,
} from '@chakra-ui/react';
import { ChevronLeftIcon, ChevronRightIcon, SearchIcon } from '@chakra-ui/icons';
import apiService from '../../services/api';

const Teams = () => {
  const [teams, setTeams] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    fetchTeams();
  }, [currentPage, searchQuery]);

  const fetchTeams = async () => {
    try {
      setLoading(true);
      const params = {
        page: currentPage,
        ...(searchQuery && { search: searchQuery })
      };

      const response = await apiService.getTeams(params);
      const teamsData = response.data.results || [];
      
      // Validate and clean the data
      const validTeams = teamsData.map(team => ({
        ...team,
        name: team.name || 'Unknown Team',
        short_name: team.short_name || 'Unknown',
        tla: team.tla || 'UNK',
        area_name: team.area_name || 'Unknown',
        venue: team.venue || 'Unknown Venue',
        founded: team.founded || 'N/A',
        crest: team.crest || 'https://via.placeholder.com/120?text=No+Crest'
      }));

      setTeams(validTeams);
      setTotalPages(Math.ceil(response.data.count / 12));
      setError(null);
    } catch (error) {
      console.error('Error fetching teams:', error);
      setError('Failed to load teams. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  const handleSearch = (value) => {
    setSearchQuery(value);
    setCurrentPage(1); // Reset to first page when searching
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
        <Stack direction={{ base: 'column', md: 'row' }} justify="space-between" align="center">
          <Heading size="lg">Teams ({teams.length})</Heading>
          <InputGroup maxW={{ base: "100%", md: "300px" }}>
            <InputLeftElement pointerEvents="none">
              <SearchIcon color="gray.300" />
            </InputLeftElement>
            <Input
              placeholder="Search teams..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
            />
          </InputGroup>
        </Stack>

        <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }} gap={6}>
          {teams.map((team) => (
            <GridItem key={team.id}>
              <Card
                bg={bgColor}
                borderWidth="1px"
                borderColor={borderColor}
                borderRadius="lg"
                overflow="hidden"
                _hover={{ transform: 'translateY(-2px)', shadow: 'lg' }}
                transition="all 0.2s"
              >
                <CardBody>
                  <VStack spacing={4} align="center">
                    <Image
                      src={team.crest}
                      alt={team.name}
                      boxSize="120px"
                      objectFit="contain"
                      fallbackSrc="https://via.placeholder.com/120?text=No+Crest"
                    />
                    <VStack spacing={2} align="center">
                      <Heading size="md" textAlign="center">
                        {team.name}
                      </Heading>
                      {team.tla && (
                        <Badge colorScheme="blue" fontSize="sm">
                          {team.tla}
                        </Badge>
                      )}
                    </VStack>
                    <Divider />
                    <Grid templateColumns="repeat(2, 1fr)" gap={4} width="100%">
                      <Stat>
                        <StatLabel>Founded</StatLabel>
                        <StatNumber fontSize="md">
                          {team.founded || 'N/A'}
                        </StatNumber>
                      </Stat>
                      <Stat>
                        <StatLabel>Area</StatLabel>
                        <StatNumber fontSize="md">
                          {team.area_name || 'N/A'}
                        </StatNumber>
                      </Stat>
                    </Grid>
                    {team.venue && (
                      <Text color="gray.500" fontSize="sm" textAlign="center">
                        🏟️ {team.venue}
                      </Text>
                    )}
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

export default Teams;