import { useState, useEffect } from 'react';
import {
  Box,
  SimpleGrid,
  Card,
  CardBody,
  Image,
  Heading,
  Text,
  Stack,
  Input,
  InputGroup,
  InputLeftElement,
  Button,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Spinner,
  Alert,
  AlertIcon,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel
} from '@chakra-ui/react';
import { FiSearch } from 'react-icons/fi';
import api from '../../services/api';

function Teams() {
  const [teams, setTeams] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [teamStats, setTeamStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      setLoading(true);
      const response = await api.get('/teams/');
      const teamsData = response.data || [];
      
      // Filter out any malformed team data
      const validTeams = teamsData.filter(team => team && team.name);
      setTeams(validTeams);
      setError(null);
    } catch (error) {
      console.error('Error fetching teams:', error);
      setError('Failed to load teams. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const fetchTeamStats = async (teamId) => {
    try {
      const response = await api.get(`/teams/${teamId}/statistics/`);
      setTeamStats(response.data || null);
      setError(null);
    } catch (error) {
      console.error('Error fetching team statistics:', error);
      setError('Failed to load team statistics. Please try again later.');
    }
  };

  const handleTeamClick = async (team) => {
    if (!team || !team.id) return;
    setSelectedTeam(team);
    await fetchTeamStats(team.id);
    onOpen();
  };

  const filteredTeams = teams.filter((team) => {
    if (!team || !team.name) return false;
    return team.name.toLowerCase().includes((searchQuery || '').toLowerCase());
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
    <Box p={4}>
      <InputGroup mb={6}>
        <InputLeftElement pointerEvents="none">
          <FiSearch color="gray.300" />
        </InputLeftElement>
        <Input
          placeholder="Search teams..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </InputGroup>

      <SimpleGrid columns={{ base: 1, md: 2, lg: 3, xl: 4 }} spacing={6}>
        {filteredTeams.map((team) => (
          <Card
            key={team.id}
            onClick={() => handleTeamClick(team)}
            cursor="pointer"
            _hover={{ transform: 'scale(1.02)', transition: 'all 0.2s' }}
          >
            <CardBody>
              <Stack spacing={4} align="center">
                {team.crest && (
                  <Image
                    src={team.crest}
                    alt={`${team.name} crest`}
                    boxSize="100px"
                    objectFit="contain"
                    fallbackSrc="https://via.placeholder.com/100?text=No+Image"
                  />
                )}
                <Heading size="md" textAlign="center">{team.name}</Heading>
                {team.area_name && (
                  <Text color="gray.600">Area: {team.area_name}</Text>
                )}
                {team.founded && (
                  <Text color="gray.600">Founded: {team.founded}</Text>
                )}
                {team.venue && (
                  <Text color="gray.600">Venue: {team.venue}</Text>
                )}
              </Stack>
            </CardBody>
          </Card>
        ))}
      </SimpleGrid>

      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{selectedTeam?.name} Statistics</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            {error ? (
              <Alert status="error">
                <AlertIcon />
                {error}
              </Alert>
            ) : !teamStats ? (
              <Box display="flex" justifyContent="center" p={4}>
                <Spinner />
              </Box>
            ) : (
              <Tabs>
                <TabList>
                  <Tab>Overall Stats</Tab>
                  <Tab>Top Scorers</Tab>
                  <Tab>Squad Details</Tab>
                </TabList>
                <TabPanels>
                  {/* Overall Statistics */}
                  <TabPanel>
                    <Table variant="simple">
                      <Thead>
                        <Tr>
                          <Th>Statistic</Th>
                          <Th>Value</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {Object.entries(teamStats.overall || {}).map(([key, value]) => (
                          <Tr key={key}>
                            <Td>{key.replace(/_/g, ' ').toUpperCase()}</Td>
                            <Td>{value}</Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  </TabPanel>

                  {/* Top Scorers */}
                  <TabPanel>
                    <Table variant="simple">
                      <Thead>
                        <Tr>
                          <Th>Name</Th>
                          <Th>Goals</Th>
                          <Th>Assists</Th>
                          <Th>Avg Minutes</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {teamStats.top_scorers?.map((scorer, index) => (
                          <Tr key={index}>
                            <Td>{scorer.name}</Td>
                            <Td>{scorer.total_goals}</Td>
                            <Td>{scorer.total_assists}</Td>
                            <Td>{scorer.avg_minutes?.toFixed(2)}</Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  </TabPanel>

                  {/* Squad Details */}
                  <TabPanel>
                    <Table variant="simple">
                      <Thead>
                        <Tr>
                          <Th>Squad Metric</Th>
                          <Th>Value</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        <Tr>
                          <Td>Total Players</Td>
                          <Td>{teamStats.squad.size}</Td>
                        </Tr>
                        <Tr>
                          <Td>Total Market Value</Td>
                          <Td>${teamStats.squad.total_market_value?.toLocaleString()}</Td>
                        </Tr>
                        <Tr>
                          <Td>Average Player Value</Td>
                          <Td>${teamStats.squad.average_player_value?.toLocaleString()}</Td>
                        </Tr>
                      </Tbody>
                    </Table>
                  </TabPanel>
                </TabPanels>
              </Tabs>
            )}
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
}

export default Teams;