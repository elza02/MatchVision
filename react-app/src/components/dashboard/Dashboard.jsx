import React from 'react';
import {
  Box,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Icon,
  Flex,
  Text,
  Heading,
} from '@chakra-ui/react';
import { FiUsers, FiActivity, FiAward, FiCalendar } from 'react-icons/fi';

function StatsCard({ title, stat, icon, description }) {
  return (
    <Stat
      px={{ base: 4, md: 8 }}
      py="5"
      shadow="base"
      rounded="lg"
      bg="white"
      _dark={{
        bg: 'gray.800',
      }}
    >
      <Flex justifyContent="space-between">
        <Box pl={2}>
          <StatLabel fontWeight="medium" isTruncated>
            {title}
          </StatLabel>
          <StatNumber fontSize="3xl" fontWeight="medium">
            {stat}
          </StatNumber>
          <StatHelpText>{description}</StatHelpText>
        </Box>
        <Box
          my="auto"
          color="brand.500"
          alignContent="center"
        >
          <Icon as={icon} w={8} h={8} />
        </Box>
      </Flex>
    </Stat>
  );
}

function Dashboard() {
  return (
    <Box>
      <Heading mb={6}>Dashboard</Heading>
      
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={{ base: 5, lg: 8 }}>
        <StatsCard
          title="Total Teams"
          stat="24"
          icon={FiUsers}
          description="Active teams in the league"
        />
        <StatsCard
          title="Matches Played"
          stat="380"
          icon={FiActivity}
          description="Total matches this season"
        />
        <StatsCard
          title="Top Scorer"
          stat="25 Goals"
          icon={FiAward}
          description="Current leading scorer"
        />
        <StatsCard
          title="Next Match"
          stat="2 Days"
          icon={FiCalendar}
          description="Time until next fixture"
        />
      </SimpleGrid>

      {/* Add more dashboard content here */}
    </Box>
  );
}

export default Dashboard;
