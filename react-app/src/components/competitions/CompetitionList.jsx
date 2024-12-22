import { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  Heading,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  Text,
  Link,
  Spinner,
  useToast,
} from '@chakra-ui/react';
import apiService from '../../services/api';

function CompetitionList() {
  const [competitions, setCompetitions] = useState([]);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    fetchCompetitions();
  }, []);

  const fetchCompetitions = async () => {
    try {
      setLoading(true);
      const response = await apiService.getCompetitions();
      setCompetitions(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load competitions',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minH="300px">
        <Spinner size="xl" />
      </Box>
    );
  }

  return (
    <Container maxW="container.xl" py={6}>
      <Heading mb={6}>Competitions</Heading>
      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
        {competitions.map((competition) => (
          <Link
            as={RouterLink}
            to={`/competitions/${competition.id}`}
            key={competition.id}
            _hover={{ textDecoration: 'none' }}
          >
            <Card>
              <CardHeader>
                <Heading size="md">{competition.name}</Heading>
              </CardHeader>
              <CardBody>
                <Text>
                  Area: {competition.area_name || 'Not specified'}
                </Text>
                <Text>
                  Season: {competition.season || 'Not specified'}
                </Text>
                {competition.type && (
                  <Text>Type: {competition.type}</Text>
                )}
                {competition.emblem && (
                  <Box mt={2}>
                    <img 
                      src={competition.emblem} 
                      alt={`${competition.name} emblem`} 
                      style={{ maxHeight: '50px' }} 
                    />
                  </Box>
                )}
              </CardBody>
            </Card>
          </Link>
        ))}
      </SimpleGrid>
    </Container>
  );
}

export default CompetitionList;
