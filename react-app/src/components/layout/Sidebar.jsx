import { Box, VStack, Icon, Text, Link } from '@chakra-ui/react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import * as FI from 'react-icons/fi';

const menuItems = [
  { name: 'Dashboard', icon: FI.FiHome, path: '/' },
  { name: 'Competitions', icon: FI.FiTrophy, path: '/competitions' },
  { name: 'Teams', icon: FI.FiUsers, path: '/teams' },
  { name: 'Matches', icon: FI.FiCalendar, path: '/matches' },
  { name: 'Players', icon: FI.FiUser, path: '/players' },
  { name: 'Analytics', icon: FI.FiPieChart, path: '/analytics' },
];

function Sidebar() {
  const location = useLocation();

  return (
    <Box
      as="nav"
      pos="fixed"
      left="0"
      h="100vh"
      w="250px"
      bg="white"
      borderRightWidth="1px"
      borderRightColor="gray.200"
      _dark={{
        bg: 'gray.800',
        borderRightColor: 'gray.700'
      }}
      boxShadow="sm"
      zIndex="sticky"
    >
      <VStack spacing="1" align="stretch" py="4">
        {menuItems.map((item) => (
          <Link
            key={item.name}
            as={RouterLink}
            to={item.path}
            textDecoration="none"
            _hover={{ textDecoration: 'none' }}
          >
            <Box
              px="4"
              py="3"
              mx="2"
              display="flex"
              alignItems="center"
              bg={location.pathname === item.path ? 'brand.50' : 'transparent'}
              _dark={{
                bg: location.pathname === item.path ? 'gray.700' : 'transparent'
              }}
              _hover={{
                bg: 'brand.50',
                _dark: { bg: 'gray.700' }
              }}
              borderRadius="md"
              transition="all 0.2s"
            >
              <Icon
                as={item.icon}
                boxSize="5"
                color={location.pathname === item.path ? 'brand.500' : 'gray.600'}
                _dark={{
                  color: location.pathname === item.path ? 'brand.400' : 'gray.400'
                }}
              />
              <Text
                ml="3"
                fontSize="sm"
                fontWeight="medium"
                color={location.pathname === item.path ? 'brand.500' : 'gray.600'}
                _dark={{
                  color: location.pathname === item.path ? 'brand.400' : 'gray.400'
                }}
              >
                {item.name}
              </Text>
            </Box>
          </Link>
        ))}
      </VStack>
    </Box>
  );
}

export default Sidebar;
