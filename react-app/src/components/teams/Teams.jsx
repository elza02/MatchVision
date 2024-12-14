// import { useState, useEffect } from 'react';
// import {
//   Box,
//   SimpleGrid,
//   Card,
//   CardBody,
//   Image,
//   Heading,
//   Text,
//   Stack,
//   Input,
//   InputGroup,
//   InputLeftElement,
//   Button,
//   useDisclosure,
//   Modal,
//   ModalOverlay,
//   ModalContent,
//   ModalHeader,
//   ModalBody,
//   ModalCloseButton,
//   Table,
//   Thead,
//   Tbody,
//   Tr,
//   Th,
//   Td,
//   Spinner,
//   Alert,
//   AlertIcon,
// } from '@chakra-ui/react';
// import { FiSearch } from 'react-icons/fi';
// import api from '../../services/api';

// function Teams() {
//   const [teams, setTeams] = useState([]);
//   const [searchQuery, setSearchQuery] = useState('');
//   const [selectedTeam, setSelectedTeam] = useState(null);
//   const [teamStats, setTeamStats] = useState(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);
//   const { isOpen, onOpen, onClose } = useDisclosure();

//   useEffect(() => {
//     fetchTeams();
//   }, []);

//   const fetchTeams = async () => {
//     try {
//       const response = await api.get('/teams/');
//       setTeams(response.data?.results || []);
//       console.log(response.data)
//       setError(null);
//     } catch (error) {
//       console.error('Error fetching teams:', error);
//       setError('Failed to load teams. Please try again later.');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const fetchTeamStats = async (teamId) => {
//     try {
//       const response = await api.get(`/teams/${teamId}/statistics/`);
//       setTeamStats(response.data || null);
//       setError(null);
//     } catch (error) {
//       console.error('Error fetching team statistics:', error);
//       setError('Failed to load team statistics. Please try again later.');
//     }
//   };

//   const handleTeamClick = async (team) => {
//     setSelectedTeam(team);
//     await fetchTeamStats(team.id);
//     onOpen();
//   };

//   const filteredTeams = teams?.filter((team) =>
//     team.name.toLowerCase().includes(searchQuery.toLowerCase())
//   ) || [];

//   if (loading) {
//     return (
//       <Box display="flex" justifyContent="center" alignItems="center" minH="500px">
//         <Spinner size="xl" />
//       </Box>
//     );
//   }

//   if (error) {
//     return (
//       <Alert status="error" mt={4}>
//         <AlertIcon />
//         {error}
//       </Alert>
//     );
//   }

//   return (
//     <Box p={4}>
//       <Box mb={6}>
//         <Heading mb={4}>Teams</Heading>
//         <InputGroup maxW="400px">
//           <InputLeftElement pointerEvents="none">
//             <FiSearch />
//           </InputLeftElement>
//           <Input
//             placeholder="Search teams..."
//             value={searchQuery}
//             onChange={(e) => setSearchQuery(e.target.value)}
//           />
//         </InputGroup>
//       </Box>

//       {filteredTeams.length === 0 ? (
//         <Alert status="info">
//           <AlertIcon />
//           No teams found
//         </Alert>
//       ) : (
//         <SimpleGrid columns={{ base: 1, md: 2, lg: 3, xl: 4 }} spacing={6}>
//           {filteredTeams.map((team) => (
//             <Card
//               key={team.id}
//               cursor="pointer"
//               onClick={() => handleTeamClick(team)}
//               _hover={{ transform: 'translateY(-2px)', shadow: 'lg' }}
//               transition="all 0.2s"
//             >
//               <CardBody>
//                 <Stack spacing={4}>
//                   <Image
//                     src={team.logo_url || 'https://via.placeholder.com/150'}
//                     alt={team.name}
//                     borderRadius="lg"
//                     fallbackSrc="https://via.placeholder.com/150"
//                   />
//                   <Heading size="md">{team.name}</Heading>
//                   <Text color="gray.500">{team.venue}</Text>
//                 </Stack>
//               </CardBody>
//             </Card>
//           ))}
//         </SimpleGrid>
//       )}

//       <Modal isOpen={isOpen} onClose={onClose} size="xl">
//         <ModalOverlay />
//         <ModalContent>
//           <ModalHeader>{selectedTeam?.name} Statistics</ModalHeader>
//           <ModalCloseButton />
//           <ModalBody pb={6}>
//             {error ? (
//               <Alert status="error">
//                 <AlertIcon />
//                 {error}
//               </Alert>
//             ) : !teamStats ? (
//               <Box display="flex" justifyContent="center" p={4}>
//                 <Spinner />
//               </Box>
//             ) : (
//               <Table variant="simple">
//                 <Thead>
//                   <Tr>
//                     <Th>Statistic</Th>
//                     <Th>Value</Th>
//                   </Tr>
//                 </Thead>
//                 <Tbody>
//                   <Tr>
//                     <Td>Matches Played</Td>
//                     <Td>{teamStats.matches_played || 0}</Td>
//                   </Tr>
//                   <Tr>
//                     <Td>Wins</Td>
//                     <Td>{teamStats.wins || 0}</Td>
//                   </Tr>
//                   <Tr>
//                     <Td>Draws</Td>
//                     <Td>{teamStats.draws || 0}</Td>
//                   </Tr>
//                   <Tr>
//                     <Td>Losses</Td>
//                     <Td>{teamStats.losses || 0}</Td>
//                   </Tr>
//                   <Tr>
//                     <Td>Goals Scored</Td>
//                     <Td>{teamStats.goals_scored || 0}</Td>
//                   </Tr>
//                   <Tr>
//                     <Td>Goals Conceded</Td>
//                     <Td>{teamStats.goals_conceded || 0}</Td>
//                   </Tr>
//                 </Tbody>
//               </Table>
//             )}
//           </ModalBody>
//         </ModalContent>
//       </Modal>
//     </Box>
//   );
// }

// export default Teams;


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
} from '@chakra-ui/react';
import { FiSearch } from 'react-icons/fi';
import axios from 'axios';

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
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/teams/`);
      setTeams(response.data || []); // Adjust based on the API response structure
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
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/analytics/team/${teamId}/`);
      setTeamStats(response.data || null); // Adjust based on the API response structure
      setError(null);
    } catch (error) {
      console.error('Error fetching team statistics:', error);
      setError('Failed to load team statistics. Please try again later.');
    }
  };

  const handleTeamClick = async (team) => {
    setSelectedTeam(team);
    await fetchTeamStats(team.id);
    onOpen();
  };

  const filteredTeams = teams?.filter((team) =>
    team.name.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

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
      <Box mb={6}>
        <Heading mb={4}>Teams</Heading>
        <InputGroup maxW="400px">
          <InputLeftElement pointerEvents="none">
            <FiSearch />
          </InputLeftElement>
          <Input
            placeholder="Search teams..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </InputGroup>
      </Box>

      {filteredTeams.length === 0 ? (
        <Alert status="info">
          <AlertIcon />
          No teams found
        </Alert>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3, xl: 4 }} spacing={6}>
          {filteredTeams.map((team) => (
            <Card
              key={team.id}
              cursor="pointer"
              onClick={() => handleTeamClick(team)}
              _hover={{ transform: 'translateY(-2px)', shadow: 'lg' }}
              transition="all 0.2s"
            >
              <CardBody>
                <Stack spacing={4}>
                  <Image
                    src={team.logo_url || 'https://via.placeholder.com/150'}
                    alt={team.name}
                    borderRadius="lg"
                    fallbackSrc="https://via.placeholder.com/150"
                  />
                  <Heading size="md">{team.name}</Heading>
                  <Text color="gray.500">{team.venue}</Text>
                </Stack>
              </CardBody>
            </Card>
          ))}
        </SimpleGrid>
      )}

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
              <Table variant="simple">
                <Thead>
                  <Tr>
                    <Th>Statistic</Th>
                    <Th>Value</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  <Tr>
                    <Td>Matches Played</Td>
                    <Td>{teamStats.matches_played || 0}</Td>
                  </Tr>
                  <Tr>
                    <Td>Wins</Td>
                    <Td>{teamStats.wins || 0}</Td>
                  </Tr>
                  <Tr>
                    <Td>Draws</Td>
                    <Td>{teamStats.draws || 0}</Td>
                  </Tr>
                  <Tr>
                    <Td>Losses</Td>
                    <Td>{teamStats.losses || 0}</Td>
                  </Tr>
                  <Tr>
                    <Td>Goals Scored</Td>
                    <Td>{teamStats.goals_scored || 0}</Td>
                  </Tr>
                  <Tr>
                    <Td>Goals Conceded</Td>
                    <Td>{teamStats.goals_conceded || 0}</Td>
                  </Tr>
                </Tbody>
              </Table>
            )}
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
}

export default Teams;
